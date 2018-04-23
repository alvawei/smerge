package conflerge.tree.ast;

import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.List;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;

/**
 * The diff algorithm requires several preprocessing steps on the ASTs.
 * They appear in this file to keep ASTDiffer.java a bit more managable.
 */
public class ASTInputProcessing {

    /**
     * Returns an identity map from each Node in n to its parent node.
     * If the node is a member of a NodeListWrapper linked to a 
     * NodeListWrapperNode, that NodeListWrapperNode will be the parent.
     * 
     * @param root
     * @return IdentityHashMap of Node -> Parent(Node)
     */
    public static IdentityHashMap<Node, Node> getParentMap(Node root) {
        IdentityHashMap<Node, Node> parents = new IdentityHashMap<>();
        parents.put(root, null);
        return getParentMap(root, parents);
    }
    
    /**
     * Private helper for getParentMap
     */
    private static IdentityHashMap<Node, Node> getParentMap(Node root, IdentityHashMap<Node, Node> parents) {
        List<Node> children = new ArrayList<>(root.getChildNodes());   
        List<NodeList<?>> nodeLists = root.getNodeLists();
        for (NodeList<?> nl : nodeLists) {
            if (nl instanceof NodeListWrapper) {
                NodeListWrapper nlw = (NodeListWrapper) nl;
                parents.put(nlw.node, root);
                for (Node n : nlw.nodeList) {
                    parents.put(n, nlw.node);
                    children.remove(n);
                    getParentMap(n, parents);       
                }
            }
        }
        for (Node n : children) {
            parents.put(n, root);
            getParentMap(n, parents);
        }
        return parents;
    }
    
    /**
     * Returns the depth of nodes in root in pre-order. If Node n is the ith node in 
     * the tree rooted at root and has depth d then: getDepths(root)[i] = d.
     * 
     * @param root
     * @return int[] of depths
     */
    public static int[] getDepths(Node root) {
        List<Integer> list = new ArrayList<Integer>();
        list.add(null); 
        getDepths(root, list, 0);
        int[] res = new int[list.size()];
        for (int i = 1; i < list.size(); i++) {
            res[i] = list.get(i);
        }
        return res;
    }
    
    /**
     * Private helper for getDepths.
     */
    private static void getDepths(Node root, List<Integer> list, int d) {
        list.add(d);
        List<Node> children = new ArrayList<>(root.getChildNodes());   
        List<NodeList<?>> nodeLists = root.getNodeLists();
        for (NodeList<?> nl : nodeLists) {
            if (nl instanceof NodeListWrapper) {
                list.add(d + 1);
                for (Node n : ((NodeListWrapper)nl).nodeList) {
                    getDepths(n, list, d + 2);
                    children.remove(n);
                }
            }
        }
        for (Node n : children) {
            getDepths(n, list, d + 1);
        }
    }
    
    /**
     * Returns Node[] of pre-order nodes in root. This array is intended
     * to be treated as 1-indexed, so the 0th element is null. Additionally,
     * any NodeListWrapper in root will be reflected as a NodeListWrapperNode
     * in this array.
     * 
     * @param root
     * @return Node[] of pre-order nodes in root.
     */
    public static Node[] getOrderedNodes(Node root) {
        List<Node> res = new ArrayList<Node>();
        res.add(null);
        getOrderedNodes(root, res);
        return res.toArray(new Node[res.size()]);
    }
      
    /**
     * Private helper for getOrderedNodes.
     */
    private static void getOrderedNodes(Node root, List<Node> list) {
        list.add(root);
        List<Node> children = new ArrayList<>(root.getChildNodes());   
        List<NodeList<?>> nodeLists = root.getNodeLists(); 
        for (NodeList<?> nl : nodeLists) {
            if (nl instanceof NodeListWrapper) {
                NodeListWrapper nlw = (NodeListWrapper) nl;
                NodeListWrapperNode nlwn = new NodeListWrapperNode(nlw);
                nlw.node = nlwn;
                list.add(nlwn);
                for (Node n : nlw.nodeList) {
                    getOrderedNodes(n, list);
                    children.remove(n);
                }
            }
        }
        for (Node n : children) {
            getOrderedNodes(n, list);
        }
    }
}
