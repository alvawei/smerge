package smerge.ast.actions;

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
	
	private Map<Integer, Insert> inserts;
	private Map<Integer, Delete> deletes;
	private Map<Integer, Move> moves;
	private Map<Integer, Update> updates;
	
	private SortedSet<Action> sortedActions;
	
	private Map<Integer, Map<Integer, Insert>> insertSets;
	private Map<Integer, Set<Delete>> deleteSets;
	private Map<Integer, Set<Shift>> shiftSets;

		
	private Set<Integer> noDeletes; // set of base nodes that cant be deleted
	
	public ActionSet() {
		inserts = new HashMap<>();
		deletes = new HashMap<>();
		moves = new HashMap<>();
		updates = new HashMap<>();
		
		insertSets = new TreeMap<>();
		deleteSets = new HashMap<>();
		shiftSets = new HashMap<>();
		
		noDeletes = new HashSet<>();
	}
	
	// returns true iff actions are merged into base tree
	public boolean apply() {
		
		/*
		System.out.println(moves);
		for (int id : moves.keySet()) {
			inserts.put(id, moves.get(id).getInsert());
			deletes.put(id, moves.get(id).getDelete());
		} */
		
		// applies inserts by order of parentID and then position
		for (int parentID : insertSets.keySet()) {
			for (Insert ins : insertSets.get(parentID).values()) {
				ins.apply();
			}
		}	
		
		/*
		for (Delete delete : deletes.values()) delete.apply(); 
		
		for (Move m : moves.values()) m.apply();
		*/
		for (Update update : updates.values()) update.apply();
		
		
		/*
		// sort actions
		sortedActions = new TreeSet<>(new ActionSort());
		sortedActions.addAll(inserts.values());
		sortedActions.addAll(deletes.values());
		sortedActions.addAll(updates.values());
		
		System.out.println(sortedActions);
		// apply actions
		for (Action a : sortedActions) a.apply();
		*/
		
		return true;
	}
	
	public void addInsert(ASTNode parent, ASTNode child, int position, boolean isLocal) {
		int id = child.getID();
		int parentID = parent.getID();
		
		if (!insertSets.containsKey(parentID)) {
			insertSets.put(parentID, new TreeMap<>());
		}
		if (insertSets.get(parentID).containsKey(position) && child.getType() != Type.WHITESPACE) {
			// conflicting inserts to same position
			ASTNode other = insertSets.get(parentID).get(position).getChild();
			ASTNode local = isLocal ? child : other;
			ASTNode remote = isLocal ? other : child;
			ASTNode base = NodeMerger.merge(null, local, remote);
			
			insertSets.get(parentID).put(position, new Insert(parent, base, position));
		} else {
			insertSets.get(parentID).put(position, new Insert(parent, child, position));
		}
		
		// TODO: counts as resolved conflict?
		if (deletes.containsKey(parentID)) {
			deletes.remove(parentID);
		}
		inserts.put(id, new Insert(parent, child, position));
	}
	
	// need to not delete a node if the other edit tree inserts/moves a node as a child to the deletion
	public void addDelete(ASTNode base) {
		int id = base.getID();
		if (!noDeletes.contains(id)) {
			deletes.put(id, new Delete(base));
		}
	}
	
	// this may be complicated?
	// possibly just implement as an insert and a delete,
	// but what if both trees move it to different locations:
	// conflicting inserts, which could be determined in addInsert()
	public void addMove(int id, Move move) {
		moves.put(id, move);
	}
	
	public void addMove(ASTNode destParent, ASTNode base, int position) {
		int id = base.getID();
		if (moves.containsKey(id)) {
			int baseParentID = base.getParent().getID();
			int otherDestParentID = moves.get(id).getInsert().getParentID();
			int thisDestParentID = destParent.getID();
			if (thisDestParentID != baseParentID && otherDestParentID != baseParentID && 
					thisDestParentID != otherDestParentID) {
				// need to duplicate it? or not move it?
				moves.remove(id);
				return;
				//throw new RuntimeException("conflicting moves");
			} else if (otherDestParentID != baseParentID){
				// use existing move over this one
				return;
			}
		}
		moves.put(id, new Move(destParent, base, position));
	}
	
	public void addShift(ASTNode parent, ASTNode edit, int oldPos, int newPos) {
		if (!shiftSets.containsKey(parent.getID())) {
			shiftSets.put(parent.getID(), new HashSet<>());
		}
		shiftSets.get(parent.getID()).add(new Shift(parent, edit, oldPos, newPos));
		
	}

	
	public void addUpdate(ASTNode base, ASTNode edit, boolean isLocal) {
		int id = base.getID();
		if (updates.containsKey(id)) {
			// merge updates
		    updates.get(id).setEdit(edit, isLocal);
		} else {
			// remove delete from other edit if it exists
			if (deletes.containsKey(id)) {
				deletes.remove(id);
			}
			noDeletes.add(id);
			updates.put(id, new Update(base, edit, isLocal));
		}		
	}
	
	// minimizes actions
	public void minimize() {
		// remove implicit shifts
		for (int parentID : shiftSets.keySet()) {
			Set<Shift> shiftSet = shiftSets.get(parentID);
			Map<Integer, Insert> insertSet= insertSets.get(parentID);
			Set<Delete> deleteSet = deleteSets.get(parentID);
			
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
			for (Delete delete : deleteSet) {
				for (Shift shift : shiftSet) {
					if (shift.oldPosition >= delete.getPosition()) {
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
	
	/*
	public class ActionSort implements Comparator<Action> {
		
		// order by action type: delete -> insert -> update

		@Override
		public int compare(Action o1, Action o2) {
			if (o1 instanceof Insert && o2 instanceof Insert) {
				Insert ins1 = (Insert) o1;
				Insert ins2 = (Insert) o2;
				
				if ()
				
				
			}
			
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
	} */
	
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
