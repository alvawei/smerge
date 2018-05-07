package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Update implements Action {
	
	private ASTNode parent; // parent of before in base tree

	private ASTNode before;
	private ASTNode after;
	
	// swap before with after
	public void apply() {
		after.children().clear();
		after.children().addAll(before.children());
		
		ASTNode parent = before.getParent();
		after.setParent(parent);
		
		// set after as before's parent's child
		int position = parent.children().indexOf(before);
		parent.children().set(position, after);	
	}

}
