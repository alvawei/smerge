package smerge.ast.parsers.python;

import smerge.ast.ASTNode;


// A PythonTree just holds onto the root PythonNode
// Primarily acts as an "unparser" through the toString() method
public class PythonNode extends ASTNode {
	
	public static final String INDENT = "    ";
	
	public String text;
		
	public PythonNode() {
		this(-1, "@root\n", Type.ROOT);
	}
	
	public PythonNode (int indentation, String content, Type type) {
		super();
		this.indentation = indentation;
		this.content = content;
		this.type = type;
	}
	
	// unparses this (sub)tree back to source code
	public String toString() {
		StringBuilder sb = new StringBuilder();
		if (indentation != -1) {
			indent(indentation, sb);
			sb.append(content);
		}
		for (ASTNode child : children) {
			sb.append(child.toString());
		}
		return sb.toString();
	}
	
	// unparse this node and it's children
	public void unparse(StringBuilder sb) {
		if (!this.isRoot()) {
			indent(indentation, sb);
			sb.append(content + "\n");
		}
		for (ASTNode child : children) {
			child.unparse(sb);
		}
	}
	
	// appends indentation to the given string builder
	private void indent(int indentation, StringBuilder sb) {
		for (int i = 0; i < indentation; i++) {
			sb.append(" ");
		}
	}

	@Override
	public boolean merge(ASTNode n1, ASTNode n2) {
		// TODO Auto-generated method stub
		return false;
	}
}
