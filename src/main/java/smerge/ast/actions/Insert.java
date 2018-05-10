package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Insert {
	
	private ASTNode parent;
	private ASTNode node;
	private int position;
	
	public Insert(ASTNode parent, ASTNode node, int positon) {
		this.parent = parent;
		this.node = node;
		this.position = position;
	}
	
	// inserts the sutree with root node under the given parent at the given position
	public void apply() {
		parent.children().add(position, node);
	}

}
