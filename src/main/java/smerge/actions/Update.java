package smerge.actions;

import smerge.ast.ASTNode;

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
		if (base.getIndentation() != edit.getIndentation())
			base.setIndentation(edit.getIndentation());
		if (!base.getContent().equals(edit.getContent()))
			base.setContent(edit.getContent());
	}
	
	public String toString() {
		return "Update " + base.getID();
	}

}
