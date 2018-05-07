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
		StringBuilder sb = new StringBuilder();
		for (String imp : imports) {
			sb.append(imp + "\n");
		}
		sb.append(root.toString());
		return sb.toString();
	}
	
	public Iterator<ASTNode> preOrder() {
		return root.preOrder();
	}
}
