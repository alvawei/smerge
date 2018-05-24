package smerge.ast;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import smerge.ast.parsers.Parser;

/*
 * This class represents a generic Abstract Syntax Tree. It is a wrapper
 * around a root ASTNode.
 * 
 */

public class AST implements Iterable<ASTNode> {
	
	private Parser p;
	private ASTNode root;
	
	public AST(ASTNode root, Parser p) {
		this.root = root;
		this.p = p;
	}
	
	public ASTNode getRoot() {
		return root;
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
		return p.unparse(this);
	}
	
	public String debugTree() {
		StringBuilder sb = new StringBuilder();
		root.debugTree(sb, "");
		return sb.toString();
	}
}
