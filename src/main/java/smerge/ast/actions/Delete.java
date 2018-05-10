package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Delete implements Action {
	
	private ASTNode parent; // parent removed from (in base tree)
	private ASTNode child; // child being removed (remote or local)
	private int position; // index of child
	
	public Delete(ASTNode parent, ASTNode child, int position) {
		this.parent = parent;
		this.child = child;
		this.position = position;
	}
	

	public void apply() {
		parent.children().remove(position);
	}

	
}
