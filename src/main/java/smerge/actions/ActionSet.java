package smerge.actions;

import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;

import smerge.ast.ASTNode;

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
	private Set<Integer> insertedIDs = new HashSet<>();
	
	// <parent ID <position of delete, Delete object>>
	private Map<Integer, Map<Integer, Delete>> deleteSets;
	private Set<Integer> deletedIDs = new HashSet<>();
	
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
		int id = child.getID();
		if (!insertSets.containsKey(parentID)) {
			insertSets.put(parentID, new TreeMap<>());
			parents.add(parentID);
		}
		insertedIDs.add(id);
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
		deletedIDs.add(child.getID());
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
	public void addShift(ASTNode baseParent, ASTNode baseChild, int oldPos, ASTNode editParent, ASTNode editChild, int newPos) {
		if (!shiftSets.containsKey(baseParent.getID())) {
			shiftSets.put(baseParent.getID(), new HashSet<>());
		}
		shiftSets.get(baseParent.getID()).add(new Shift(baseParent, baseChild, oldPos, editParent, editChild, newPos));
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
	
	/**
	 * Minimizes Insert actions by removing (unnecessary) Insert actions that are present
	 * because their parent was also deleted.
	 */
	private void minimizeInserts() {
		for (int id : insertedIDs) {
			if (insertSets.containsKey(id))
				insertSets.remove(id);
		}
	}
	
	/**
	 * Minimizes Delete actions by removing (unnecessary) Delete actions that are present
	 * because their parent was also deleted.
	 */
	private void minimizeDeletes() {
		for (int id : deletedIDs) {
			if (deleteSets.containsKey(id))
				deleteSets.remove(id);
		}
	}
	
	/**
	 * Removes shifts caused by Insert/Delete actions
	 */
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
					addInsert(shift.getBaseParent(), shift.getEditChild(), shift.newPosition);
					addDelete(shift.getBaseChild());
				}
			}
		}
	}
	
	// Getter methods
	
	/**
	 * @return
	 */
	public Set<Integer> parents() {
		return parents;
	}
	
	/**
	 * @param parentID
	 * @return
	 */
	public Collection<Delete> getDeletes(int parentID) {
		Map<Integer, Delete> map = deleteSets.get(parentID);
		return map != null ? map.values() : new TreeSet<>();
	}
	
	/**
	 * @param parentID
	 * @return
	 */
	public Map<Integer, Insert> getInsertMap(int parentID) {
		Map<Integer, Insert> map = insertSets.get(parentID);
		return map != null ? map : new TreeMap<>();
	}
	
	/**
	 * @param parentID
	 * @return
	 */
	public Collection<Insert> getInserts(int parentID) {
		Map<Integer, Insert> map = insertSets.get(parentID);
		return map != null ? map.values() : new TreeSet<>();
	}
	
	/**
	 * @return
	 */
	public Map<Integer, Update> getUpdateMap() {
		return updates;
	}
	
	
	/*
	 * Strictly for debugging
	 */
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