package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Delete implements Action {
	
	private ASTNode parent;
	private int position;
	

	public void apply() {
		parent.children().remove(position);		
	}

	
}
