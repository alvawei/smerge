package smerge.actions;

import smerge.ast.ASTNode;
import smerge.ast.NodeMerger;

public class Update implements Action {
	
	private ASTNode base;
	private ASTNode edit;
	
	public Update(ASTNode base, ASTNode edit) {
		this.base = base;
		this.edit = edit;
		
	}
	
	public ASTNode getBase() {
		return base;
	}
	
	public ASTNode getEdit() {
		return edit;
	}
	// swap before with after
	public void apply() {
		// TODO
	}
	
	public String toString() {
		return "Update " + base.getID();
	}

}
