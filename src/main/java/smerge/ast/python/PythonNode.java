package smerge.ast.python;

import java.util.ArrayList;

import smerge.ast.ASTNode;

public class PythonNode extends ASTNode {
	
	public static final String INDENT = "    ";
	
	private int lineNum;
	private int indentation;
	private String text;
	
	private PythonNode parent;
	private ArrayList<PythonNode> children;
	
	public PythonNode() {
		this.indentation = -1;
		this.children = new ArrayList<>();
	}
	
	public PythonNode (int lineNum, int indentation, String text) {
		this.lineNum = lineNum;
		this.indentation = indentation;
		this.text = text;
		
		this.children = new ArrayList<>();
	}
	
	public PythonNode getParent() {
		return parent;
	}
	
	public void setParent(PythonNode node) {
		this.parent = node;
		
	}
	
	public int indentation() {
		return indentation;
	}
	
	public String toString() {
		if (indentation == -1) return "root";
		String line = "";
		for (int i = 0; i < indentation; i++) 
			line += INDENT;
		line += text + "\n";
		return line;
	}

}
