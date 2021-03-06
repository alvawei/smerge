package smerge.actions;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

import smerge.ast.ASTNode;
import smerge.ast.ASTNode.Type;
import smerge.parsers.Parser;

/**
 * This class is responsible for applying the two ActionSets (base->local and base->remote)
 * back onto the base AST. This class also counts merge conflicts and how many of them are 
 * solvable for evaluation purposes.
 * 
 * @author Jediah Conachan, Steven Miller (documentation)
 */
public class ActionMerger {
	
	// these integers are for evaluation purposes
	public int totalConflicts;
	public int unsolvedConflicts;
	
	private ActionSet localActions;
	private ActionSet remoteActions;
	private Parser p;
	
	/**
	 * Initializes a new ActionMerger instance.
	 * @param localActions - set of local changes to be merged
	 * @param remoteActions - set of remote changes to be merged
	 */
	public ActionMerger(ActionSet localActions, ActionSet remoteActions, Parser p) {
		this.localActions = localActions;
		this.remoteActions = remoteActions;
		this.p = p;
	}
	
	/**
	 * Applies both local and remote actions, merging changes as necessary.
	 */
	public void merge() {
		mergeInsertAndDeleteActions();
		mergeUpdateActions();
	}
	
	/**
	 * merge all inserts and deletes onto the base tree
	 */
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
			
			// TODO: ignore certain deletes
			
			if (localDeletes != null && remoteInserts != null) {
				
			}

			// ignore all deletes at first by adjusting inserts
			for (Delete delete : localDeletes) {
				for (int position : localInserts.keySet()) {
					// if the local insert position is >= the position we're
					// deleting from,
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
	
	/**
	 * merge all inserts into the base tree
	 * @param localInsert Insert action of the local tree
	 * @param remoteInsert Insert action of the remote tree
	 * @return a single Insert object
	 */
	private Insert mergeInserts(Insert localInsert, Insert remoteInsert) {
		ASTNode local = localInsert.getChild();
		ASTNode remote = remoteInsert.getChild();

		ASTNode.Type type = local.getType();
		ASTNode mergedNode;
		if (type == Type.IMPORT) {
			mergedNode = mergeImports(null, local, remote);
			totalConflicts++;
		} else if (local.getContent().equals(remote.getContent())) {
			mergedNode = new ASTNode(type, local.getContent(), local.getIndentation());
			mergedNode.setID(local.getID());
		} else {
			mergedNode = wrapConflict(null, local, remote);
			totalConflicts++;
		}
		return new Insert(localInsert.getParent(), mergedNode, localInsert.getPosition());
	}
	
	/**
	 * merge all updates onto the base tree
	 */
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
	
	/**
	 * merges two conflicting updates if possible
	 * @param localUpdate the local Update action
	 * @param remoteUpdate the remote Update action
	 */
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
			}
		}
	}
	 
	/**
	 * applies non-conflicting updates
	 * @param updates
	 * @param intersection
	 */
	private void applyUpdates(Map<Integer, Update> updates, Set<Integer> intersection) {
		for (int id : updates.keySet()) {
			if (!intersection.contains(id)) {
				updates.get(id).apply();
			}
		}
	}
	
	/**
	 * applies actions from one action set that doesn't interfere with the other action set
	 * @param actions
	 */
	private void applyDeletesAndInserts(ActionSet actions) {
		for (int parentID : actions.parents()) {
			// apply deletes then inserts
			for (Delete delete : actions.getDeletes(parentID))
				delete.apply();
			for (Insert insert : actions.getInserts(parentID))
				insert.apply();
		}
	}
	
	/**
	 * wraps an unsolvable conflict with conflict identifiable text
	 * returns a new base node if the given base node is null
	 * @param base
	 * @param local
	 * @param remote
	 * @return
	 */
	private ASTNode wrapConflict(ASTNode base, ASTNode local, ASTNode remote) {
		unsolvedConflicts++;
		String baseContent = base == null ? "" : base.subtreeContent(p) + "\n=======\n";	
		String conflict = 
				"<<<<<<< REMOTE\n" + 
				remote.subtreeContent(p) + "\n" +
				"=======\n" +
				baseContent +
				local.subtreeContent(p) + "\n" +
				">>>>>>> LOCAL";
		if (base == null) {
			base = new ASTNode(local.getType(), conflict, 0);
			base.setID(local.getID());
		} else {
			base.setContent(conflict);
		}
		System.out.println("@@@@@" + base.getID());
		return base;
	}
	
	/**
	 * merges all imports into a base node (returns a new base node if its a two-insert conflict)
	 * this method may be simplified if we choose not to include the base import
	 * @param base base node
	 * @param local local node
	 * @param remote remote node
	 * @return the base node
	 */
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