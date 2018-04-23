package conflerge.tree.ast;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;

/**
 * Unfortunately, Javaparser's trees don't play nicely with our algorithm. This Visitor adds a
 * layer of indirection to  distinguish between children of one type from children of another in 
 * nodes that contain lists of children.
 */
@SuppressWarnings({ "rawtypes" })
public class NodeListWrapper extends NodeList {
    
    /**
     * The wrapped NodeList
     */
    public NodeList<? extends Node> nodeList;
    
    /**
     * A NodeListWrapperNode that corresponds to this NodeListWrapper.
     */
    public NodeListWrapperNode node;
    
    /**
     * Constructs a new NodeListWrapper wrapping the given NodeList.
     * @param nodeList
     */
    public NodeListWrapper(NodeList<? extends Node> nodeList) {
        this.nodeList = nodeList;
    }
    
    @Override
    public boolean isEmpty() { 
        return nodeList.isEmpty();
    }
}

