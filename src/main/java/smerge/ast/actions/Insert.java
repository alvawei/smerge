package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Insert {
	
	private ASTNode parent; // node the child is inserted into (in base tree)
	private ASTNode child; // child introduced in local or remote tree
	private int position; // index of child
	
	public Insert(ASTNode parent, ASTNode child, int positon) {
		this.parent = parent;
		this.child = child;
		this.position = position;
	}
	
	// inserts the sutree with root node under the given parent at the given position
	public void apply() {
		parent.children().add(position, child);
	}

}
