package smerge.ast.actions;

public class Move implements Action {
	
	public Insert ins;
	public Delete del;
	
	public Move(Insert ins, Delete del) {
		this.ins = ins;
		this.del = del;
	}
	
	
	public void apply() {
		// del.apply();
		// ins.apply();
	}
	
	public String toString() {
		return "Move (" + del + ", " + ins + ")";
	}
}
