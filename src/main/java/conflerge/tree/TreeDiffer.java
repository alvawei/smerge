package conflerge.tree;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.nodeTypes.NodeWithModifiers;

import conflerge.tree.ast.ASTInputProcessing;
import conflerge.tree.ast.NodeListWrapper;
import conflerge.tree.ast.NodeListWrapperNode;
import conflerge.tree.visitor.ShallowEqualsVisitor;

/**
 * Uses the mmdiff algorithm (by Sudarshan S. Chawathe, available at http://www.vldb.org/conf/1999/P8.pdf)
 * to diff two ASTs (referred to as A and B throughout) and generate an edit script from tree A to tree B.
 * 
 * This algorithm gives the minimum-cost sequence of insert, delete, and replace edits between the two
 * trees, where all edits occur on the tree's leaf nodes. So although the edits themselves are single node
 * operations, after they are computed they can view them as entire subtree insertions, deletions, and 
 * replacements. This is particularly useful for merging.
 * 
 */
public class TreeDiffer {
    
    /**
     * The cost of an edit operation.
     */
    public static final int editCost = 1;
    
    /**  
     *  Nodes in A that were deleted in B. Logically this is a Set,
     *  not a Map, but we use IdentityHashMap because nodes are 
     *  tracked based on object identity rather than equality.
     */
    private Set<Node> deletes = Collections.newSetFromMap(new IdentityHashMap<Node, Boolean>());
    
    /**
     *  Mapping from nodes in A to nodes they replaced with in B.
     */
    private IdentityHashMap<Node, Node> replacesA = new IdentityHashMap<>();
    
    /**
     *  Mapping from nodes in B that to nodes they replaced in A.
     */
    private IdentityHashMap<Node, Node> replacesB = new IdentityHashMap<>();
    
    /**
     * Mappings from nodes in A and to nodes in B that are aligned. 
     * The mmdiff algorithm enforces that key, values nodes MUST be 
     * shallowly equal: otherwise it would be a replacement, 
     * not an alignment.
     */
    private IdentityHashMap<Node, Node> alignsA = new IdentityHashMap<>();
    
    /**
     * Mappings between nodes in B to nodes in A that are aligned. 
     */
    private IdentityHashMap<Node, Node> alignsB = new IdentityHashMap<>();
    
    /**
     * Javaparser does not treat modifiers (public, private, static, etc) as 
     * nodes, so the mmdiff algorithm ignores them. This map stores a mapping
     * from nodes in A to their altered modifiers in B, if any. 
     */
    private IdentityHashMap<Node, EnumSet<Modifier>> modifiers = new IdentityHashMap<>();
    
    /**
     * Mapping of nodes aligned in A to their comments modified in B.
     */
    private IdentityHashMap<Node, Optional<Comment>> comments = new IdentityHashMap<>();
    
    /**
     * A map from NodeListWrapperNodes to nodes that were
     * inserted under their NodeList.
     */
    private IdentityHashMap<NodeListWrapperNode, List<Node>> listInserts  = new IdentityHashMap<>();
    
    /**
     *  Sometimes mmdiff will return insertions that do not correspond
     *  to inserting a node into a list of parameters. If these insertions
     *  are top-level (defn: there are no modifications to these insertion's
     *  ancestors) performing the merge is problematic. These insertions
     *  are stored separately so they can later be translated into replace
     *  operations and merged correctly.
     */
    private IdentityHashMap<Node, Node> nonListInserts = new IdentityHashMap<>();
    
    /**
     *  Maps from nodes in A to their parent nodes. Unlike the node's 'getParent' 
     *  method, this returns NodeListWrapperNodes if the node is a member of a wrapped 
     *  NodeList. Never use 'getParent' if you expected wrapper nodes.
     */
    private final IdentityHashMap<Node, Node> parentsA;
    
    /**
     *  Maps from nodes in B to their parent nodes.
     */
    private final IdentityHashMap<Node, Node> parentsB;
    
       
    /**
     *  Array of optimal subproblem edit distances.
     */
    private int[][] opt;
    
    /**
     *  Length of opt's first dimension, equal to the number of nodes in A.
     *  The name is 'n' chosen to correspond to the mmdiff paper's notation.
     */
    private final int m;
    
    /**
     *  Length of opt's second dimension, equal to the number of nodes in B.
     *  The name 'n' is chosen to correspond to the mmdiff paper's notation.
     */
    private final int n;
    
    /**
     *  The nodes in A in pre-order.
     */
    private final Node[] aN;
    
    /**
     *  The nodes in B in pre-order.
     */
    private final Node[] bN;
    
    /**
     * The depth of nodes in A in pre-order. If Node n is the ith node in A 
     * and has depth d, then: aD[i] = d
     */
    private final int[] aD;
    
    /**
     * The depth of nodes in B in pre-order.
     */
    private final int[] bD;

    /**
     * Constructs a new ASTDiffer to operate on trees A, B.
     * A call to diff() will return a DiffResult containing
     * an edit script from A to B.
     * 
     * @param A 'Base' tree for the diff.
     * @param B 'Dest' tree for the diff.
     */
    public TreeDiffer(Node A, Node B) {        
        this.aN = ASTInputProcessing.getOrderedNodes(A);
        this.bN = ASTInputProcessing.getOrderedNodes(B);
       
        this.aD = ASTInputProcessing.getDepths(A);
        this.bD = ASTInputProcessing.getDepths(B);
        
        this.parentsA = ASTInputProcessing.getParentMap(A);
        this.parentsB = ASTInputProcessing.getParentMap(B);
        
        m = aN.length;
        n = bN.length;

        this.opt = new int[m][n];
    }

    /**
     * @return An edit script from this ASTDiffer's A tree to its B tree.
     */
    public DiffResult diff() {
        // Run mmdiff to compute the edit distance between trees A and B.
        computeEdits();
        
        // Run mmdiff backward to recover the edit script, stored in the
        // replace, align, and insert fields.
        recoverEdits();
        
        // mmDiff may return an edit script that includes an insertion that
        // isn't inserting a node into a list of nodes. Performing these inserts
        // is prohibitively complicated on trees where edges are labeled (eg., ASTs).
        // When this occurs, add a 'replace' operation for the inserted node's parent
        // to avoid performing the non-list insert.
        replaceNonListInserts();
         
        // Produce a mapping of NodeLists -> indexes to insert -> Nodes to insert.
        // This operation must be performed last because it depends on complete
        // alignment and replacement maps.
        IdentityHashMap<NodeListWrapper, Map<Integer, List<Node>>> indexInserts = processListInserts();
        
        return new DiffResult(deletes, replacesA, modifiers, comments, indexInserts);
    }

    /**
     * Runs the mmdiff algorithm. Populates opt with the computation's results.
     */
    private void computeEdits() {
       int max = m + n + 1;
       for (int i = 1; i < m; i++) {
           opt[i][0] = opt[i-1][0] + editCost;
       }
       for (int j = 1; j < n; j++) {
           opt[0][j] = opt[0][j-1] + editCost;
       }
       for (int i = 1; i < m; i++) {
           for (int j = 1; j < n; j++) {
               int align  = max;
               int delete = max; 
               int insert = max;           
               if (aD[i] == bD[j]) {
                   align = opt[i-1][j-1] + updateCost(aN[i], bN[j]);
               }
               if (j == n - 1 || bD[j+1] <= aD[i]) {
                   delete = opt[i-1][j] + editCost;
               }
               if (i == m - 1 || aD[i+1] <= bD[j]) {
                   insert = opt[i][j-1] + editCost;
               }
               opt[i][j] = min(align, delete, insert);
           }
       }
    }    
  
    /**
     * Recovers the edit script. Must not be called until opt has been
     * populated by a call to computeEdits.
     */
    private void recoverEdits() {
       int i = m - 1;
       int j = n - 1;    
       while (i > 0 && j > 0) {
           if (opt[i][j] == opt[i-1][j] + editCost && (j == n-1 || bD[j+1] <= aD[i])) {
               addDelete(i, j);
               i--;
           } else if (opt[i][j] == opt[i][j-1] + editCost && (i == m-1 || aD[i+1] <= bD[j])) {             
               addInsert(i, j);
               j--;
           } else {
               addAlignOrReplace(i, j);
               i--;
               j--;
           } 
       }
       while (i > 0) { addDelete(i, j); i--; }
       while (j > 0) { addInsert(i, j); j--; }
    }
     
    /**
     * Process an aligment or replacement operation.
     * @param i index of A node in aN.
     * @param j index of B node in bN.
     */
    private void addAlignOrReplace(int i, int j) {
        if (updateCost(aN[i], bN[j]) == 0)  {
            
            if (aN[i] instanceof NodeWithModifiers) {
                EnumSet<Modifier> aMods = ((NodeWithModifiers<?>) aN[i]).getModifiers();
                EnumSet<Modifier> bMods = ((NodeWithModifiers<?>) bN[j]).getModifiers();
                if (!aMods.equals(bMods)) {
                    modifiers.put(aN[i], bMods);
                }
            }
                
            Optional<Comment> commentA = aN[i].getComment();
            Optional<Comment> commentB = bN[j].getComment();
            if (!commentA.equals(commentB)) {
                comments.put(aN[i], commentB);
            }
            
            alignsA.put(aN[i], bN[j]);
            alignsB.put(bN[j], aN[i]);
        } else {
            replacesA.put(aN[i], bN[j]);
            replacesB.put(bN[j], aN[i]);
        }
    }

    /**
     * Process a delete operation.
     * @param i index of A node in aN.
     * @param j index of B node in bN.
     */
    private void addDelete(int i, int j) {
        deletes.add(aN[i]);
    }
    
    /**
     * Process an insert operation.
     * @param i index of A node in aN.
     * @param j index of B node in bN.
     */
    private void addInsert(int i, int j) {
        Node parent = parentsB.get(bN[j]);     
        if (parentsB.get(bN[j]) instanceof NodeListWrapperNode) {
            if (!listInserts.containsKey(parent)) {
              listInserts.put((NodeListWrapperNode) parent, new ArrayList<Node>());
            }
            listInserts.get(parent).add(bN[j]);
        } else {
            nonListInserts.put(bN[j], bN[j]);
        }
    }   
    
    //-Output-Processing---------------------------------------------
    
    /**
     *  Replaces any non-list insert operation with the replacement of that
     *  Node's parent. This operation spares our merge visitor from performing 
     *  inserts that are not into lists of nodes.
     */
    private void replaceNonListInserts() {
        for (Node n : nonListInserts.keySet()) {
            if (alignsB.containsKey(parentsB.get(n))) {
                replacesA.put(alignsB.get(parentsB.get(n)), parentsB.get(n));
            }
        }
    }
    
    /**
     * Returns a mapping of NodeList -> index of insertion(s) into that NodeList -> Node(s) inserted.
     * 
     * This operation must be performed after the edits have been computed and
     * recovered because it depends on the compelete alignment and replacement maps. 
     */
    private IdentityHashMap<NodeListWrapper, Map<Integer, List<Node>>> processListInserts() {
        
        IdentityHashMap<NodeListWrapper, Map<Integer, List<Node>>> result = new IdentityHashMap<>();       
        
        for (NodeListWrapperNode nlwn : listInserts.keySet()) {
            
            // If the list wasn't aligned it won't be relevant; it's not a 'top-level' operation.
            if (!alignsB.containsKey(nlwn)) {
                continue;
            }
            
            // Get the wrapper node's NodeList
            NodeList<? extends Node> nl = nlwn.list.nodeList;
            
            // The recoverEdits step returns the inserts in reverse order, so correct that.
            Collections.reverse(listInserts.get(nlwn));
            
            // Get the corresponding NodeListWrapperNode from A
            NodeListWrapperNode alignedNlwn = (NodeListWrapperNode) alignsB.get(nlwn);
           
            // Set up the index -> inserts 
            Map<Integer, List<Node>> inserts = new HashMap<>();
           
            // Add the index, insert pairs  
            for (Node insert : listInserts.get(nlwn)) {
                int insertIndex = getInsertIndex(nl, insert);
                if (!inserts.containsKey(insertIndex)) {
                    inserts.put(insertIndex, new ArrayList<Node>());
                }
                inserts.get(insertIndex).add(insert);
            }
            
            // Map the NodeList in A to the index -> inserts map
            result.put(alignedNlwn.list, inserts);
        }
        
        return result;
    }
    
    /**
     * 
     * @param nl
     * @param insert
     * @return
     */
    private int getInsertIndex(NodeList<? extends Node> nl, Node insert) {
        // Get the inserted node's index in it's NodeList
        int i = indexOfObj(nl, insert);
        
        // Look back through the NodeList for a 'reference node': a node in B that aligns with
        // a node in A.
        while (i >= 0 && !alignsB.containsKey(nl.get(i)) && !replacesB.containsKey(nl.get(i))) {
            i--;
        }
        
        // Return the index be after the reference node in A, or 0 if no reference node was found.
        if (i >= 0) {
            Node matchedSibling = alignsB.containsKey(nl.get(i)) ? 
                                        alignsB.get(nl.get(i)) : 
                                            replacesB.get(nl.get(i));      
            NodeListWrapperNode matchedParent = (NodeListWrapperNode) parentsA.get(matchedSibling);
             return indexOfObj(matchedParent.list.nodeList, matchedSibling) + 1;
        } else {
            return  0;
        } 
    }

    //-Utility-Methods---------------------------------------------
    
    /**
     * Nodes are identified strictly by object equality, so this
     * method is the correct way to locate a Node in a list.
     */
    private static int indexOfObj(Iterable<?> items, Object item) {
        int i = 0;
        for (Object o : items) {
            if (o == item) {
                return i;
            }
            i++;
        }
        return -1;
    }
    
    /**
     * Returns the minimum value from the parameters.
     */
    private static int min(int... args) {
        int min = Integer.MAX_VALUE;
        for (int i = 0; i < args.length; i++)
            min = args[i] < min ? args[i] : min;
          
        return min;
    }
      
    /**
     * Returns 1 iff Node n1, n2 are shallowly equal. 
     */
    private int updateCost(Node n1, Node n2) {
        return ShallowEqualsVisitor.equals(n1, n2) ? 0 : editCost;
    } 
}