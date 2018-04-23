package conflerge.tree.visitor;

import java.util.ArrayList;

import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.visitor.Visitable;

import conflerge.tree.DiffResult;
import conflerge.tree.ast.NodeListWrapper;

/**
 * 'Unwraps' a tree that has been wrapped by NodeListWrapperVisitor: Removes
 * any NodeListWrappers and replaces them with their wrapped NodeLists.
 */
public class NodeListUnwrapperVisitor extends ModifierVisitor<DiffResult>  {  
    
    /**
     * Replace a NodeListWrapper with its wrapped NodeList.
     */
    @SuppressWarnings({ "rawtypes", "unchecked" })
    @Override
    public Visitable visit(NodeList n, DiffResult arg) {
        if (n instanceof NodeListWrapper) {
            n = ((NodeListWrapper) n).nodeList;
        }
        for (Node node : new ArrayList<Node>(n)) {
            node.accept(this, arg);
        }
        return n;
    } 
}