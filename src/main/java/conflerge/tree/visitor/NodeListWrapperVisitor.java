package conflerge.tree.visitor;

import java.util.ArrayList;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.visitor.Visitable;

import conflerge.tree.ast.NodeListWrapper;

/**
 * 'Wraps' the NodeLists in an AST. In the resulting AST, all 
 * NodeList fields are replaced with NodeListWrappers. 
 */
public class NodeListWrapperVisitor extends ModifierVisitor<String> {
    
    /**
     * Replace the NodeList with a NodeListWrapper.
     */
    @SuppressWarnings({ "rawtypes", "unchecked" })
    @Override
    public Visitable visit(NodeList n, String arg) {
        for (Node node : new ArrayList<Node>(n)) {
            node.accept(this, arg);
        }
        return new NodeListWrapper(n);       
    }
}