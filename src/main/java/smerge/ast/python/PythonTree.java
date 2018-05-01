package smerge.ast.python;

import smerge.ast.AST;
import smerge.ast.ASTNode;


// A PythonTree just holds onto the root PythonNode
// Primarily acts as an "unparser" through the toString() method
public class PythonTree extends AST {
	
	private PythonNode root;
	
	public PythonTree(PythonNode root) {
		this.root = root;
	}
	
	public String toString() {
		return toString(root);
	}
	
	public String toString(PythonNode node) {
		String res = "";
		for (ASTNode n : node.getChildren()) {
			res += n.toString();
			res += toString((PythonNode) n);
		}
		
		return res;
	}

}
