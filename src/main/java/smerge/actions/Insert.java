package smerge.actions;

import smerge.ast.ASTNode;

public class Insert implements Action {
	
	private ASTNode parent; // node the child is inserted into (in base tree)
	private ASTNode child; // child introduced in edit tree (base if in move)
	private int position;
	
	public Insert(ASTNode parent, ASTNode child, int position) {
		this.parent = parent;
		this.child = child;
		this.position = position;
	}
	
	// inserts the sutree with root node under the given parent at the given position
	public void apply() {
		// TODO should all the children of child still be attached?
		parent.children().add(position, child);
		child.setParent(parent);

	}
	
	public int getPosition() {
		return position;
	}
	
	public void setPosition(int position) {
		this.position = position;
	}
	
	// returns the id of the parent
	public int getParentID() {
		return parent.getID();
	}
	
	public ASTNode getParent() {
		return parent;
	}
	
	public ASTNode getChild() {
		return child;
	}
	
	public String toString() {
		return "Insert " + child.getID() + 
				"->" + parent.getID() + 
				"[" + position + "]";
	}

}
