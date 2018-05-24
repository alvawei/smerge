package smerge.actions;

import java.util.Map;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeMap;
import java.util.TreeSet;

import smerge.ast.ASTNode;
import smerge.ast.ASTNode.Type;

import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;


// basically a merged tree diff
// actively merges actions as they are detected in both local and remote trees
// sorts the actions and applies them to the base tree

public class ActionSet {
	
	private Set<Integer> parents;
	
	private Map<Integer, Update> updates;
	
	private SortedSet<Action> sortedActions;
	
	// <parent ID <position of insert, Insert object>>
	protected Map<Integer, Map<Integer, Insert>> insertSets;
	
	// <parent ID <position of delete, Delete object>>
	private Map<Integer, Map<Integer, Delete>> deleteSets;
	
	private Map<Integer, Set<Shift>> shiftSets;
	
	public ActionSet() {
		parents = new HashSet<>();
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
	
	public void addShift(ASTNode parent, ASTNode edit, int oldPos, int newPos) {
		if (!shiftSets.containsKey(parent.getID())) {
			shiftSets.put(parent.getID(), new HashSet<>());
		}
		shiftSets.get(parent.getID()).add(new Shift(parent, edit, oldPos, newPos));
	}

	public void addUpdate(ASTNode base, ASTNode edit, boolean isLocal) {
		updates.put(base.getID(), new Update(base, edit));	
	}
	
	// minimizes actions
	public void minimize() {
		minimizeInserts();
		minimizeDeletes();
		minimizeShifts();
	}
	
	// minimizes inserts by removing all but the root of a subtree -- avoids
	// adding an entire subtree to the insertSets
	public void minimizeInserts() {
		Set<Integer> removalSet = new HashSet<Integer>();
		// for each parent ID in the insertSets, we should remove any of its
		// children that also exist in the insertSets to avoid unnecessary inserts
		for (int parentID : insertSets.keySet()) {
			Map<Integer, Insert> insert = insertSets.get(parentID);
			for (int index : insert.keySet()) {
				if (insertSets.containsKey(insert.get(index).getParentID())) {
					removalSet.add(index);
				}
			}
		}
		for (int i : removalSet) {
			insertSets.remove(i);
		}
	}
	
	// minimizes deletes by removing all but the root of a subtree -- avoids
	// adding an entire subtree to the deleteSets
	public void minimizeDeletes() {
		Set<Integer> removalSet = new HashSet<Integer>();
		// for each parent ID in the deleteSets, we should remove any of its
		// children that also exist in the deleteSets to avoid unnecessary deletes
		for (int parentID : deleteSets.keySet()) {
			Map<Integer, Delete> delete = deleteSets.get(parentID);
			for (int index : delete.keySet()) {
				if (insertSets.containsKey(delete.get(index).getParentID())) {
					removalSet.add(index);
				}
			}
		}
		for (int i : removalSet) {
			insertSets.remove(i);
		}
	}
	
	public void minimizeShifts() {
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
	
	public Map<Integer, Update> getUpdateMap() {
		return updates;
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
		for (Action a : updates.values()) result += a.toString() + "\n";
		return result;
	}
}