package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Insert implements Action {
	
	private ASTNode parent; // node the child is inserted into (in base tree)
	private ASTNode child; // child introduced in edit tree (base if in move)
	private double position;
	
	public Insert(ASTNode parent, ASTNode child, double position) {
		this.parent = parent;
		this.child = child;
		// setting position should probably be done before the object is constructed,
		// but did not change it here since doing so would break a few other places and
		// wanted to keep compiler errors to a minimum before committing.
		this.child.setPosition(position);
	}
	
	// inserts the sutree with root node under the given parent at the given position
	public void apply() {
		child.children().clear();
		parent.children().add(child);
		child.setParent(parent);

	}
	
	// returns the id of the parent
	public int getParentID() {
		return parent.getID();
	}
	public String toString() {
		return "Insert " + child.getID() + 
				"->" + parent.getID() + 
				"[" + position + "]";
	}

}
