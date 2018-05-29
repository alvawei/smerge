package smerge.actions;

import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

import javax.swing.text.html.HTMLDocument.Iterator;

import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;

import smerge.ast.ASTNode;

// TODO: deletes don't have to be sorted, just use Map<Integer, Set<Delete>>???

/**
 * An ActionSet represents a diff between two ASTs by storing sets of different Actions.
 * Actions are detected and added to an ActionSet in Differ. Once all actions are detected,
 * the entire ActionSet is minimized (see ActionSet.minimize()).
 * 
 * @author Jediah Conachan, Steven Miller
 */
public class ActionSet {
	
	private Set<Integer> parents;
	private Map<Integer, Update> updates;
	
	// <parent ID <position of insert, Insert object>>
	protected Map<Integer, Map<Integer, Insert>> insertSets;
	
	// <parent ID <position of delete, Delete object>>
	private Map<Integer, Map<Integer, Delete>> deleteSets;
	
	private Map<Integer, Set<Shift>> shiftSets;
	
	/**
	 * Constructs an empty ActionSet.
	 */
	public ActionSet() {
		parents = new HashSet<>();
		updates = new HashMap<>();
		
		insertSets = new TreeMap<>();
		deleteSets = new HashMap<>();
		shiftSets = new HashMap<>();
	}
	
	/**
	 * Adds an Insert action to this ActionSet.
	 * @param parent - node that the child node is inserted under
	 * @param child - node being inserted
	 * @param position - index where the child should be inserted
	 */
	public void addInsert(ASTNode parent, ASTNode child, int position) {
		int parentID = parent.getID();
		if (!insertSets.containsKey(parentID)) {
			insertSets.put(parentID, new TreeMap<>());
			parents.add(parentID);
		}
		insertSets.get(parentID).put(position, new Insert(parent, child, position));
	}
	
	/**
	 * Adds a Delete action to this ActionSet.
	 * @param child - node to be deleted
	 */
	public void addDelete(ASTNode child) {
		int parentID = child.getParent().getID();
		if (!deleteSets.containsKey(parentID)) {
			deleteSets.put(parentID, new TreeMap<>((a, b) -> b.compareTo(a)));
			parents.add(parentID);
		}
		deleteSets.get(parentID).put(child.getPosition(), new Delete(child));
	}

	/**
	 * Adds an Update action to this ActionSet.
	 * @param base - the base version of the node
	 * @param edit - the updated version of the node
	 */
	public void addUpdate(ASTNode base, ASTNode edit) {
		updates.put(base.getID(), new Update(base, edit));	
	}
	
	/**
	 * Records a temporary Shift action
	 * @param parent - the parent of the edit node (base version)
	 * @param edit - the child node that was shifted
	 * @param oldPos - the position of the child in the base tree
	 * @param newPos - the position of the child in the edit tree
	 */
	public void addShift(ASTNode parent, ASTNode edit, int oldPos, int newPos) {
		if (!shiftSets.containsKey(parent.getID())) {
			shiftSets.put(parent.getID(), new HashSet<>());
		}
		shiftSets.get(parent.getID()).add(new Shift(parent, edit, oldPos, newPos));
	}
	
	/**
	 * This method should only be called after all actions have been detected by Differ.
	 * This method minimizes the action set. 
	 * 
	 * For example, if one user inserts a new method,
	 * then the method header and all lines within the method are initially considered as separate
	 * inserts. Calling this method will reduce all of the separate inserts into a single Insert action. 
	 */
	public void minimize() {
		// shifts must be minimized first
		minimizeShifts();
		minimizeInserts();
		minimizeDeletes();
	}
	
	// minimizes inserts by removing all but the root of a subtree -- avoids
	// adding an entire subtree to the insertSets
	private void minimizeInserts() {
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
	private void minimizeDeletes() {
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
	
	// removes shift actions caused by Insert/Delete actions
	// TODO: Convert remaining shifts to insert/delete actions
	private void minimizeShifts() {
		// remove implicit shifts
		for (int parentID : shiftSets.keySet()) {
			Set<Shift> shiftSet = shiftSets.get(parentID);
			Map<Integer, Insert> insertSet= insertSets.get(parentID);
			Map<Integer, Delete> deleteSet = deleteSets.get(parentID);			
			//  adjust shifts for each insert
			if (insertSet != null) {
				for (int position : insertSet.keySet()) {
					for (Shift shift : shiftSet) {
						if (shift.oldPosition >= position) {
							shift.oldPosition++;
						}
					}
				}
			}
			
			// adjust shifts for each delete
			if (deleteSet != null) {
				for (int position : deleteSet.keySet()) {
					for (Shift shift : shiftSet) {
						if (shift.oldPosition >= position) {
							shift.oldPosition--;
						}
					}
				}
			}
			
			// transform the shifts into a pair of inserts/deletes
			for (Shift shift : shiftSet) {
				if (shift.oldPosition != shift.newPosition) {
					Insert insert = new Insert(shift.getParent(), shift.getChild(), shift.newPosition);
					Map<Integer, Insert> positionToInsert = new HashMap<Integer, Insert>();
					positionToInsert.put(shift.newPosition, insert);
					insertSets.put(shift.getParent().getID(), positionToInsert);
					
					// do the same for deletes
					Delete delete = new Delete(shift.getChild());
					Map<Integer, Delete> positionToDelete = new HashMap<Integer, Delete>();
					positionToDelete.put(shift.oldPosition, delete);
					deleteSets.put(shift.getParent().getID(), positionToDelete);
				}
			}
		}
	}
	
	// transforms all shifts to a pair of inserts and deletes
//	public void transformShifts() {
//		// iterate over the parent ID's, get the sets of shifts
//		Set<Shift> unecessaryShifts = new HashSet<>();
//		for (int parentID : shiftSets.keySet()) {
//			Set<Shift> shiftSet = shiftSets.get(parentID);
//			// for each shift object, create an insert object and map it to the position
//			// of the insert, then put the insert into insertSets
//			for (Shift shift : shiftSet) {
//				Insert insert = new Insert(shift.getParent(), shift.getChild(), shift.newPosition);
//				Map<Integer, Insert> positionToInsert = new HashMap<Integer, Insert>();
//				positionToInsert.put(shift.newPosition, insert);
//				insertSets.put(shift.getParent().getID(), positionToInsert);
//				
//				// do the same for deletes
//				Delete delete = new Delete(shift.getChild());
//				Map<Integer, Delete> positionToDelete = new HashMap<Integer, Delete>();
//				positionToDelete.put(shift.oldPosition, delete);
//				deleteSets.put(shift.getParent().getID(), positionToDelete);
//			}
//			shiftSet.removeAll(unecessaryShifts);
//		}
//	}
	
	// Getter methods
	
	public Set<Integer> parents() {
		return parents;
	}
	
	public Collection<Delete> getDeletes(int parentID) {
		Map<Integer, Delete> map = deleteSets.get(parentID);
		return map != null ? map.values() : new TreeSet<>();
	}
	
	public Map<Integer, Insert> getInsertMap(int parentID) {
		Map<Integer, Insert> map = insertSets.get(parentID);
		return map != null ? map : new TreeMap<>();
	}
	
	public Collection<Insert> getInserts(int parentID) {
		Map<Integer, Insert> map = insertSets.get(parentID);
		return map != null ? map.values() : new TreeSet<>();
	}
	
	public Map<Integer, Update> getUpdateMap() {
		return updates;
	}
	
	// debugging method
	public String toString() {
		String result = "";
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