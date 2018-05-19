package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Move implements Action {
	
	private Insert insert;
	private Delete delete;
	
	public Move(ASTNode destParent, ASTNode base, double editNodePosition) {
		delete = new Delete(base);
		insert = new Insert(destParent, base, editNodePosition);
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
