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
	

	
	public void addInsert(ASTNode parent, ASTNode child, int position) {
		inserts.add(new Insert());
	}
	
	public void addDelete(ASTNode parent, ASTNode child, int position) {
		deletes.add(new Delete());
	}

	public void addUpdate() {
		// if two updates on same node, throw error? unless node types are comment?
		updates.add(new Update());
	}
	
	public void addMove() {
		moves.add(new Move());
	}
}
