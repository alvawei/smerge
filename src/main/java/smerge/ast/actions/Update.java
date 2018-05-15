package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Update implements Action {
	
	private ASTNode before;
	public ASTNode after;
	
	public Update(ASTNode before, ASTNode after) {
		this.before = before;
		this.after = after;
	}
	
	// swap before with after
	public void apply() {
		before.setContent(after.getContent());
	}
	
	public String toString() {
		return "Update " + before.getID();
	}

}
