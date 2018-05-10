package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Delete implements Action {
	
	private ASTNode parent; // parent removed from (in base tree)
	private int position; // index of child
	
	public Delete(ASTNode parent, int position) {
		this.parent = parent;
		this.position = position;
	}
	

	public void apply() {
		parent.children().remove(position);
	}
	
	public String toString() {
		return "Delete " + parent.children().get(position).getID() + " from " + parent.getID() + "[" + position + "]";
	}

	
}
