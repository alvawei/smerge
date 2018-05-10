package smerge.ast.actions;

import java.util.List;

import smerge.ast.ASTNode;

import java.util.ArrayList;

// basically a tree diff
public class ActionSet {
	
	public List<Insert> inserts;
	public List<Delete> deletes;
	public List<Update> updates;
	public List<Move> moves;
	
	public ActionSet() {
		this.inserts = new ArrayList<>();
		this.deletes = new ArrayList<>();
		this.updates = new ArrayList<>();
		this.moves = new ArrayList<>();
	}
	
	// returns true iff actions are merged into base tree
	public boolean apply() {
		return false;
	}
	

	public void add(Action a) {
		
	}
}
