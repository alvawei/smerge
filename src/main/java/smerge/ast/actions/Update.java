package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Update implements Action {
	
	private ASTNode before;
	private ASTNode after;
	
	public Update(ASTNode before, ASTNode after) {
		this.before = before;
		this.after = after;
	}
	
	// swap before with after
	public void apply() {
		// before.setLabel(after.getLabel());
	}

}
