package conflerge.tree.ast;

import com.github.javaparser.Position;
import com.github.javaparser.Range;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.visitor.GenericVisitor;
import com.github.javaparser.ast.visitor.VoidVisitor;

/**
 * A Node representation of the NodeListWrapper, used by the diff algorithm.
 * These should only be used to keep track of NodeListWrappers in collections of 
 * Nodes, and should never be added to an ASTs.
 */
public class NodeListWrapperNode extends Node {
    
    /**
     * A useless 'Range' to placate the super constructor.
     */
    private static final Range dummy_range = new Range(new Position(0, 0), new Position(0, 0));
    
    /**
     * The NodeListWrapper that corresponds to this NodeListWrapperNode.
     */
    public final NodeListWrapper list;
    
    /**
     * Constructs a new NodeListWrapperNode corresponding to the
     * given NodeListWrapper.
     * 
     * @param list
     */
    public NodeListWrapperNode(NodeListWrapper list) { 
        super(dummy_range);
        this.list = list;
    }
    
    @Override
    public <R, A> R accept(GenericVisitor<R, A> v, A arg) { return null; }

    @Override
    public <A> void accept(VoidVisitor<A> v, A arg) { }
}