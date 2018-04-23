package conflerge.tree;

import java.util.EnumSet;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.comments.Comment;

import conflerge.tree.ast.NodeListWrapper;

/**
 * Stores the data associated with a Diff between two trees A and B.
 * The fields are sets of edit operations that transform A to B.
 */
public class DiffResult {
    /**
     * Set of Nodes in A that were deleted. Must be backed by an IdentityHashMap. 
     */
    public final Set<Node> deletes;
    
    /**
     * Map from Nodes in A -> replacements in B.
     */
    public final IdentityHashMap<Node, Node> replaces;
    
    /**
     * Map from NodeListWrapper -> index in list -> nodes inserted at index.
     */
    public final IdentityHashMap<NodeListWrapper, Map<Integer, List<Node>>> listInserts;
    
    /**
     * Map from nodes in A -> altered modifiers in B.
     */
    public final IdentityHashMap<Node, EnumSet<Modifier>> modifiers;
    
    /**
     * Mapping of nodes aligned in A -> their comments modified in B.
     */
    public final IdentityHashMap<Node, Optional<Comment>> comments;
      
    /**
     * @param deletes
     * @param replaces
     * @param modifiers
     * @param listInserts
     */
    public DiffResult(Set<Node> deletes, 
                      IdentityHashMap<Node, Node> replaces,
                      IdentityHashMap<Node, EnumSet<Modifier>> modifiers,
                      IdentityHashMap<Node, Optional<Comment>> comments,
                      IdentityHashMap<NodeListWrapper, Map<Integer, List<Node>>> listInserts) {
        
        this.deletes = deletes;
        this.replaces = replaces;
        this.listInserts = listInserts;
        this.modifiers = modifiers;
        this.comments = comments;
    }
      
    /**
     * @param n
     * @return true iff n was deleted
     */
    public boolean deleted(Node n) {
        return deletes.contains(n);
    }
    
    /**
     * @param n
     * @return true iff n was replaced
     */
    public boolean replaced(Node n) {
        return replaces.containsKey(n);
    }
}