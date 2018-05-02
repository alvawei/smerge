package smerge.ast;

import java.util.List;
import java.util.ArrayList;

public class AST {
	
	private ASTNode root;
	protected List<String> imports;
	
	public AST(ASTNode root) {
		this.root = root;
		this.imports = new ArrayList<>();
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
}
