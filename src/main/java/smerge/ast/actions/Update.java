package smerge.ast.actions;

import smerge.Merger;
import smerge.ast.ASTNode;
import smerge.ast.NodeMerger;

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
			Merger.totalConflicts++;
			boolean solved = NodeMerger.merge(base, local, remote);
			if (solved) Merger.solvedConflicts++;
			
		} else if (local != null) {
			base.setContent(local.getContent());
			base.setIndentation(local.getIndentation());
		} else if (remote != null) {
			base.setContent(remote.getContent());
			base.setIndentation(remote.getIndentation());
		}
	}
	
	public String toString() {
		return "Update " + base.getID();
	}

}
