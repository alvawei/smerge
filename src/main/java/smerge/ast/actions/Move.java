package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Move implements Action {
	
	private Insert insert;
	private Delete delete;
	
	public Move(ASTNode destParent, ASTNode base, int position) {
		delete = new Delete(base);
		insert = new Insert(destParent, base, position);
	}
	
	
	public void apply() {
		delete.apply();
		insert.apply();
	}
	
	public Insert getInsert() {
		return insert;
	}
	
	public Delete getDelete() {
		return delete;
	}
	
	public String toString() {
		return "Move (" + delete + ", " + insert + ")";
	}
}
