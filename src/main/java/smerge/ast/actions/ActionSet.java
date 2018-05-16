package smerge.ast.actions;

import java.util.Map;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;

// basically a merged tree diff
// actively merges actions as they are detected in both local and remote trees
// sorts the actions and applies them to the base tree

public class ActionSet {
	
	private Map<Integer, Insert> inserts;
	private Map<Integer, Delete> deletes;
	private Map<Integer, Move> moves;
	private Map<Integer, Update> updates;
	
	private SortedSet<Action> sortedActions;
		
	private Set<Integer> noDeletes; // set of base nodes that cant be deleted
	
	public ActionSet() {
		inserts = new HashMap<>();
		deletes = new HashMap<>();
		moves = new HashMap<>();
		updates = new HashMap<>();
		
		noDeletes = new HashSet<>();
	}
	
	// returns true iff actions are merged into base tree
	public boolean apply() {
		for (int id : moves.keySet()) {
			addInsert(id, moves.get(id).ins);
			addDelete(id, moves.get(id).del);
		}
		
		// sort actions
		sortedActions = new TreeSet<>(new ActionSort());
		sortedActions.addAll(inserts.values());
		sortedActions.addAll(deletes.values());
		sortedActions.addAll(updates.values());
		
		System.out.println(sortedActions);
		// apply actions
		for (Action a : sortedActions) a.apply();
		
		return true;
	}
	
	public void addInsert(int id, Insert insert) {
		if (inserts.containsKey(id)) {
			throw new RuntimeException("Duplicate Insert: conflicting Move?");
		}
		int parentID = insert.getParentID();
		if (deletes.containsKey(parentID)) {
			deletes.remove(parentID);
		}
		noDeletes.add(parentID);
		inserts.put(id, insert);
		
	}
	
	// TODO:
	// need to not delete a node if the other edit tree inserts/moves a node as a child to the deletion
	public void addDelete(int id, Delete delete) {
		if (!noDeletes.contains(id)) {
			deletes.put(id, delete);
		}
	}
	
	// this may be complicated?
	// possibly just implement as an insert and a delete,
	// but what if both trees move it to different locations:
	// conflicting inserts, which could be determined in addInsert()
	public void addMove(int id, Move move) {
		moves.put(id, move);
	}
	
	public void addUpdate(int id, Update update, boolean isLocal) {
		if (updates.containsKey(id)) {
			// merge updates
		    updates.get(id).setEdit(update.getEdit(isLocal), isLocal);
		} else {
			// remove delete from other edit if it exists
			if (deletes.containsKey(id)) {
				deletes.remove(id);
			}
			noDeletes.add(id);
			updates.put(id, update);
		}		
	}
	
	public class ActionSort implements Comparator<Action> {
		
		// order by action type: delete -> insert -> update

		@Override
		public int compare(Action o1, Action o2) {
			
			// DO NOT EVER RETURN 0
			// otherwise actions are considered equal and rewrite each other when being sorted in the set
			
			// do all updates last
			if (o1 instanceof Update) return 1;
			if (o2 instanceof Update) return 1;
			
			// then do deletes
			if (o1 instanceof Delete) return -1;
			if (o2 instanceof Delete) return 1;
				
			return -1;
		}
	}
	
	// note this returns different strings before and after running apply()
	public String toString() {
		String result = "Actions:\n";
		if (sortedActions != null)
			return result + sortedActions.toString();
		
		for (Action a : inserts.values()) result += a.toString() + "\n";
		for (Action a : deletes.values()) result += a.toString() + "\n";
		for (Action a : moves.values()) result += a.toString() + "\n";
		for (Action a : updates.values()) result += a.toString() + "\n";
		return result;
	}
}
