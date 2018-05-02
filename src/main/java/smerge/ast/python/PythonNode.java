package smerge.ast.python;

import smerge.ast.ASTNode;


// A PythonTree just holds onto the root PythonNode
// Primarily acts as an "unparser" through the toString() method
public class PythonNode extends ASTNode {
	
	public static final String INDENT = "    ";
	
	private int indentation;
	private String text;
		
	public PythonNode() {
		this(-1, "@root");
	}
	
	public PythonNode (int indentation, String text) {
		super();
		this.indentation = indentation;
		this.text = text;
	}
	
	// unparses this (sub)tree back to source code
	public String toString() {
		StringBuilder sb = new StringBuilder();
		if (indentation != -1) {
			indent(indentation, sb);
			sb.append(text);
		}
		for (ASTNode child : children) {
			sb.append(child.toString());
		}
		return sb.toString();
	}
	
	// appends indentation to the given string builder
	private void indent(int indentation, StringBuilder sb) {
		for (int i = 0; i < indentation; i++) {
			sb.append(INDENT);
		}
	}

}
