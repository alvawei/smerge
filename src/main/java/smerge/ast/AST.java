package smerge.ast;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/*
 * This class represents a generic Abstract Syntax Tree. It is a wrapper
 * around a root ASTNode.
 * 
 */

public class AST implements Iterable<ASTNode> {
	
	private ASTNode root;
	
	public AST(ASTNode root) {
		this.root = root;
	}
	
	public ASTNode getRoot() {
		return root;
	}	
	
	public String unparse() {
		StringBuilder sb = new StringBuilder();
		root.unparse(sb);
		return sb.toString();
	}
	
	// returns an iterator that performs a preorder traversal of the tree
	public Iterator<ASTNode> iterator() {
		return root.preOrder();
	}
	
	public List<ASTNode> preOrderList() {
		List<ASTNode> list = new ArrayList<>();
		for (ASTNode n : this) {
			list.add(n);
		}
		return list;
	}
	public String toString() {
		return unparse();
	}
	
	public String debugTree() {
		StringBuilder sb = new StringBuilder();
		root.debugTree(sb, "");
		return sb.toString();
	}
}
