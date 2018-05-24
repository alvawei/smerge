package smerge.actions;

import java.util.Map;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeMap;
import java.util.TreeSet;

import smerge.ast.ASTNode;
import smerge.ast.ASTNode.Type;
import smerge.ast.NodeMerger;

import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;


// basically a merged tree diff
// actively merges actions as they are detected in both local and remote trees
// sorts the actions and applies them to the base tree

public class ActionSet {
	
	private Set<Integer> parents;
	
	private Map<Integer, Move> moves;
	private Map<Integer, Update> updates;
	
	private SortedSet<Action> sortedActions;
	
	protected Map<Integer, Map<Integer, Insert>> insertSets;
	private Map<Integer, Map<Integer, Delete>> deleteSets;
	private Map<Integer, Set<Shift>> shiftSets;
	
	public ActionSet() {
		parents = new HashSet<>();
		moves = new HashMap<>();
		updates = new HashMap<>();
		
		insertSets = new TreeMap<>();
		deleteSets = new HashMap<>();
		shiftSets = new HashMap<>();
	}
	
	public void addInsert(ASTNode parent, ASTNode child, int position, boolean isLocal) {
		int parentID = parent.getID();
		if (!insertSets.containsKey(parentID)) {
			insertSets.put(parentID, new TreeMap<>());
			parents.add(parentID);
		}
		insertSets.get(parentID).put(position, new Insert(parent, child, position));
	}
	
	// need to not delete a node if the other edit tree inserts/moves a node as a child to the deletion
	public void addDelete(ASTNode base) {
		int parentID = base.getParent().getID();
		if (!deleteSets.containsKey(parentID)) {
			deleteSets.put(parentID, new TreeMap<>((a, b) -> b.compareTo(a)));
			parents.add(parentID);
		}
	}
	
	public void addMove(ASTNode destParent, ASTNode base, int position) {
		int id = base.getID();
		moves.put(id, new Move(destParent, base, position));
	}
	
	public void addShift(ASTNode parent, ASTNode edit, int oldPos, int newPos) {
		if (!shiftSets.containsKey(parent.getID())) {
			shiftSets.put(parent.getID(), new HashSet<>());
		}
		shiftSets.get(parent.getID()).add(new Shift(parent, edit, oldPos, newPos));
	}

	public void addUpdate(ASTNode base, ASTNode edit, boolean isLocal) {
		updates.put(base.getID(), new Update(base, edit, isLocal));	
	}
	
	// minimizes actions
	public void minimize() {
		// remove implicit shifts
		for (int parentID : shiftSets.keySet()) {
			Set<Shift> shiftSet = shiftSets.get(parentID);
			Map<Integer, Insert> insertSet= insertSets.get(parentID);
			Map<Integer, Delete> deleteSet = deleteSets.get(parentID);
			
			Set<Shift> unecessaryShifts = new HashSet<>();
			
			//  adjust shifts for each insert
			for (int position : insertSet.keySet()) {
				for (Shift shift : shiftSet) {
					if (shift.oldPosition >= position) {
						shift.oldPosition++;
					}
				}
			}
			
			// adjust shifts for each delete
			for (int position : deleteSet.keySet()) {
				for (Shift shift : shiftSet) {
					if (shift.oldPosition >= position) {
						shift.oldPosition--;
					}
				}
			}
			
			// remove unnecessary shifts
			for (Shift shift : shiftSet) {
				if (shift.oldPosition == shift.newPosition) {
					unecessaryShifts.add(shift);
				}
			}
			shiftSet.removeAll(unecessaryShifts);
		}
	}
	
	public Set<Integer> parents() {
		return parents;
	}
	
	public Map<Integer, Delete> getDeleteMap(int parentID) {
		return deleteSets.get(parentID);
	}
	
	public Map<Integer, Insert> getInsertMap(int parentID) {
		return insertSets.get(parentID);
	}
	
	// note this returns different strings before and after running apply()
	public String toString() {
		String result = "Actions:\n";
		for (Map<Integer, Insert> insertSet : insertSets.values()) {
			for (Insert insert : insertSet.values()) result += insert.toString() + "\n";
		}
		for (Map<Integer, Delete> deleteSet : deleteSets.values()) {
			for (Delete delete : deleteSet.values()) result += delete.toString() + "\n";
		}
		for (Action a : moves.values()) result += a.toString() + "\n";
		for (Action a : updates.values()) result += a.toString() + "\n";
		return result;
	}
}
