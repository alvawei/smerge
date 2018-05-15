package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Update implements Action {
	
	private ASTNode base;
	private ASTNode local;
	private ASTNode remote;
	
	public Update(ASTNode base, ASTNode edit, boolean isLocal) {
		this.base = base;
		setEdit(edit, isLocal);
		
	}
	
	public void setEdit(ASTNode edit, boolean isLocal) {
		if (isLocal) {
			this.local = edit;
		} else {
			this.remote = edit;
		}
	}
	
	public ASTNode getEdit(boolean isLocal) {
		return isLocal ? local : remote;
	}
	// swap before with after
	public void apply() {
		if (local != null && remote != null) {
			// merge nodes or identify conflict
		}
		//base.setContent(newContent);
	}
	
	public String toString() {
		return "Update " + base.getID();
	}

}
