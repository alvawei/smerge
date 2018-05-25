package smerge.actions;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

import smerge.ast.ASTNode;
import smerge.ast.ASTNode.Type;

// this class merges two action sets and applys the merged actions onto the base tree
// also counts conflicts

/**
 * This class is responsible for applying the two ActionSets (base->local and base->remote) back onto
 * the base AST. This class also counts merge conflicts and how many of them are solvable for evaluation purposes.
 * 
 * @author Jediah Conachan
 */
public class ActionMerger {
	
	// these integers are for evaluation purposes
	public int totalConflicts;
	public int solvedConflicts;
	
	private ActionSet localActions;
	private ActionSet remoteActions;
	
	public ActionMerger(ActionSet localActions, ActionSet remoteActions) {
		this.localActions = localActions;
		this.remoteActions = remoteActions;
	}
	
	// TODO: conflict definitions here:
	// TODO: we need to handle all of these in merge()
	// TODO: not delete nodes that have inserts under them
	
	// note "two" means one from local and one from remote
	
	// two updates on same node
	//   - imports = merge (solvable)
	//   - comment = ignore (solvable?)
	//   - otherwise conflict (unsolvable)
	
	// two inserts same spot
	//   - imports = merge (solvable)
	//   - treat as two-update conflict on empty base node? (unsolvable)
	//   - both inserts have same content (solvable)
	
	// two inserts different spot (same parent)
	//   - idk
	
	// deletes
	//   - if there is another insert/delete by other tree under same parent, just ignore?
	
	// moves
	//   - idk
	
	
	/**
	 * Applies both local actions and remote actions, merging changes as necessary.
	 */
	public void merge() {
		mergeInsertAndDeleteActions();
		mergeUpdateActions();
	}
	
	// merge all inserts and deletes onto the base tree
	private void mergeInsertAndDeleteActions() {
		// separate parents into three sets that don't share any common parent IDs
		Set<Integer> parentsIntersection = new HashSet<>();
		parentsIntersection.addAll(localActions.parents());
		parentsIntersection.retainAll(remoteActions.parents());
		localActions.parents().removeAll(parentsIntersection);
		remoteActions.parents().removeAll(parentsIntersection);
		
		// apply local-only and remote-only insert/delete actions
		applyDeletesAndInserts(localActions);
		applyDeletesAndInserts(remoteActions);		
		
		// apply the rest of the insert/delete actions
		for (int parentID : parentsIntersection) {
			Set<Delete> localDeletes = new HashSet<>(localActions.getDeletes(parentID));
			Set<Delete> remoteDeletes = new HashSet<>(remoteActions.getDeletes(parentID));
			
			Map<Integer, Insert> localInserts = localActions.getInsertMap(parentID);
			Map<Integer, Insert> remoteInserts = remoteActions.getInsertMap(parentID);
			
			if (localDeletes == null && remoteInserts != null) {
				
			}

			// ignore all deletes at first by adjusting inserts
			for (Delete delete : localDeletes) {
				for (int position : localInserts.keySet()) {
					if (position >= delete.getPosition()) {
						// note the mapping will become unsynced
						localInserts.get(position).setPosition(position++);
					}
				}
			}
			for (Delete delete : remoteDeletes) {
				for (int position : remoteInserts.keySet()) {
					if (position >= delete.getPosition()) {
						// note the mapping will become unsynced
						remoteInserts.get(position).setPosition(position++);
					}
				}
			}
			// merge inserts
			Map<Integer, Insert> inserts = new TreeMap<>();
			for (Insert insert : localInserts.values()) inserts.put(insert.getPosition(), insert);
			for (Insert insert : remoteInserts.values()) {
				int position = insert.getPosition();
				if (inserts.containsKey(position)) {
					totalConflicts++;
					inserts.put(position, mergeInserts(inserts.get(position), insert));
				} else {
					inserts.put(insert.getPosition(), insert);
				}
			}
			
			// apply all inserts
			for (Insert insert : inserts.values()) insert.apply();
			
			// now apply all deletes
			for (Delete delete : localDeletes) delete.apply();
			for (Delete delete : remoteDeletes) delete.apply();
		}
				
	}
	
	// similar to mergeUpdates()
	private Insert mergeInserts(Insert localInsert, Insert remoteInsert) {
		ASTNode local = localInsert.getChild();
		ASTNode remote = remoteInsert.getChild();

		ASTNode.Type type = local.getType();
		ASTNode mergedNode;
		if (type == Type.IMPORT) {
			mergedNode = mergeImports(null, local, remote);
			solvedConflicts++;
		} else {
			mergedNode = wrapConflict(null, local, remote);
		}
		return new Insert(localInsert.getParent(), mergedNode, localInsert.getPosition());
	}
	
	// merge all updates onto the base tree
	private void mergeUpdateActions() {
		Map<Integer, Update> localUpdates = localActions.getUpdateMap();
		Map<Integer, Update> remoteUpdates = remoteActions.getUpdateMap();

		Set<Integer> updatesIntersection = new HashSet<>();
		updatesIntersection.addAll(localUpdates.keySet());
		updatesIntersection.retainAll(remoteUpdates.keySet());
		
		// apply non-intersecting updates
		applyUpdates(localUpdates, updatesIntersection);
		applyUpdates(remoteUpdates, updatesIntersection);
		
		// apply intersecting updates
		for (int id : updatesIntersection) {
			mergeUpdate(localUpdates.get(id), remoteUpdates.get(id));
			totalConflicts++;
		}
	}
	
	// TODO: indentation + content updates in same tree
	// merges two conflicting updates if possible
	private void mergeUpdate(Update localUpdate, Update remoteUpdate) {
		ASTNode base = localUpdate.getBase();
		ASTNode local = localUpdate.getEdit();
		ASTNode remote = remoteUpdate.getEdit();
		
		ASTNode.Type type = base.getType();
		if (type == Type.IMPORT) {
			mergeImports(base, local, remote);
		} else if (type == Type.COMMENT || type == Type.BLOCK_COMMENT) {
			// keep base comment - don't apply any update
		} else {
			if (local.getContent().equals(remote.getContent())) {
				// just apply one update
				remoteUpdate.apply();
			} else if (base.getContent().equals(local.getContent()) || 
					base.getContent().equals(remote.getContent())) {
				// in this case one tree updated indentation and the other updated content
				// update.apply() will update only changed fields, so the following works
				localUpdate.apply();
				remoteUpdate.apply();
			} else {
				// unmergable
				wrapConflict(base, local, remote);
				return; // don't increase solved conflict count
			}
		}
		solvedConflicts++;
	}
	
	// applies non-conflicting updates 
	private void applyUpdates(Map<Integer, Update> updates, Set<Integer> intersection) {
		for (int id : updates.keySet()) {
			if (!intersection.contains(id)) {
				updates.get(id).apply();
			}
		}
	}
	
	// applys actions from one action set that doesn't interfere with the other action set
	private void applyDeletesAndInserts(ActionSet actions) {
		for (int parentID : actions.parents()) {
			// apply deletes then inserts
			for (Delete delete : actions.getDeletes(parentID))
				delete.apply();
			for (Insert insert : actions.getInserts(parentID))
				insert.apply();
		}
	}
	
	// wraps an unsolvable conflict with conflict identifiable text
	// returns a new base node if the given base node is null
	private ASTNode wrapConflict(ASTNode base, ASTNode local, ASTNode remote) {
		String baseContent = base == null ? "" : base.getContent() + "\n=======\n";	
		String conflict = 
				"<<<<<<< REMOTE\n" + 
				remote.getContent() + "\n" +
				"=======\n" +
				baseContent +
				local.getContent() + "\n" +
				">>>>>>> LOCAL";
		if (base == null) {
			base = new ASTNode(local.getType(), conflict, 0);
			base.setID(local.getID());
		} else {
			base.setContent(conflict);
		}
		return base;
	}
	
	// merges all imports into a base node (returns a new base node if its a two-insert conflict)
	// this method may be simplified if we choose not to include the base import
	private ASTNode mergeImports(ASTNode base, ASTNode local, ASTNode remote) {
		if (base != null) {
			String[] imports = {base.getContent(), local.getContent(), remote.getContent()};
			Arrays.sort(imports);
			base.setContent(imports[0] + "\n" + imports[1] + "\n" + imports[2]);
		} else {
			String[] imports = {local.getContent(), remote.getContent()};
			Arrays.sort(imports);
			base = new ASTNode(local.getType(), imports[0] + "\n" + imports[1], 0);
		}
		return base;
	}
}