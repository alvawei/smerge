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
	
	public PythonNode (int indentation, String text, Type type) {
		super();
		this.indentation = indentation;
		this.text = text;
		this.label = this.text;
		this.type = type;
	}
	
	// unparses this (sub)tree back to source code
	public String toString() {
		StringBuilder sb = new StringBuilder();
		if (indentation != -1) {
			indent(indentation, sb);
			sb.append(label);
		}
		for (ASTNode child : children) {
			sb.append(child.toString());
		}
		return sb.toString();
	}
	
	// appends indentation to the given string builder
	private void indent(int indentation, StringBuilder sb) {
		for (int i = 0; i < indentation; i++) {
			sb.append(" ");
		}
	}
	
	@Override
	public void update(ASTNode o) {
		PythonNode other = (PythonNode) o;
		System.out.println(this.indentation + " -> "  + other.indentation);
		this.indentation = other.indentation;
		this.label = other.label;
	}

}