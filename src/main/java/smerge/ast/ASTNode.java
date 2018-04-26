package smerge.ast;

import java.util.ArrayList;

public class ASTNode {
	
	public static final String INDENT = "    ";
	
	private int lineNum;
	private int indentation;
	private String text;
	
	private ASTNode parent;
	private ArrayList<ASTNode> children;
	
	public ASTNode() {
		this.text = "root";
		this.children = new ArrayList<>();
	}
	
	public ASTNode (int lineNum, int indentation, String text) {
		this.lineNum = lineNum;
		this.indentation = indentation;
		this.text = text;
		
		this.children = new ArrayList<>();
	}
	
	public ArrayList<ASTNode> getChildren() {
		return children;
	}
	
	public ASTNode getParent() {
		return parent;
	}
	
	public void setParent(ASTNode node) {
		if (parent != null) 
			parent.children.remove(this);
		
		parent = node;
		parent.children.add(this);
		
	}
	
	public int indentation() {
		return indentation;
	}
	
	public int getID() {
		return text.hashCode();
	}
}
