package smerge.ast.actions;

import java.util.List;
import java.util.Map;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;

// basically a tree diff
public class ActionSet {
	
	private Map<Integer, Insert> inserts;
	private Map<Integer, Delete> deletes;
	private Map<Integer, Move> moves;
	private Map<Integer, Update> updates;
		
	public ActionSet() {
		inserts = new HashMap<>();
		deletes = new HashMap<>();
		moves = new HashMap<>();
		updates = new HashMap<>();
	}
	
	// returns true iff actions are merged into base tree
	public boolean apply() {
		/*
		// unwrap moves into single insert and delete
		for (int i = 0; i < actions.size(); i++) {
			if (actions.get(i) instanceof Move) {
				Move m = (Move) actions.get(i);
				actions.remove(i);
				actions.add(m.ins);
				actions.add(m.del);
			}
		}
		// sort actions to be applied in specifc order
		Collections.sort(actions, new ActionSort());
		
		for (Action a : actions) {
			a.apply();
		}
		*/
		return false;
	}
	
	public void addInsert(int id, Insert insert) {
		
	}
	
	public void addDelete(int id, Delete delete) {
		
	}
	
	public void addMove(int id, Move move) {
		
	}
	
	public void addUpdate(int id, Update update) {
		
	}
	
	public class ActionSort implements Comparator<Action> {
		
		// order by action type: delete -> insert -> update

		@Override
		public int compare(Action o1, Action o2) {
			if (o1 instanceof Delete && !(o2 instanceof Delete))
				return -1;
			
			if (o2 instanceof Delete && !(o1 instanceof Delete))
				return 1;
			
				
				return 0;
		}
	}
	
	public String toString() {
		String result = "Actions:\n";
		for (Action a : inserts.values()) {
			result += a.toString() + "\n";
		}
		for (Action a : deletes.values()) {
			result += a.toString() + "\n";
		}
		for (Action a : moves.values()) {
			result += a.toString() + "\n";
		}
		for (Action a : updates.values()) {
			result += a.toString() + "\n";
		}
		return result;
	}
}
