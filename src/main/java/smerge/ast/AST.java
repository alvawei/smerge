package smerge.ast;

import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;

public class AST {
	
	private ASTNode root;
	
	// stored in a list just for purpose of retaining order
	protected List<String> imports;
	
	public AST(ASTNode root) {
		this.root = root;
		this.imports = new ArrayList<>();
	}
	
	public ASTNode getRoot() {
		return root;
	}
	
	public List<String> imports() {
		return imports;
	}
	
	
	public String toString() {
		return root.toString();
	}
	
	public String debugTree() {
		StringBuilder sb = new StringBuilder();
		root.debugTree(sb, "");
		return sb.toString();
	}
	
	public String idTree() {
		StringBuilder sb = new StringBuilder();
		root.idTree(sb, "");
		return sb.toString();
	}
	
	public Iterator<ASTNode> preOrder() {
		return root.preOrder();
	}
}
