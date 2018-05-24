package smerge.actions;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import smerge.ast.ASTNode;

// this class merges two action sets and applys the merged actions onto the base tree
// also counts conflicts
public class ActionMerger {
	
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
	// TODO: copy stuff over from NodeMerger
	
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
	
	
	
	public void merge() {
		// TODO: add getter methods in ActionSet
		
		// separate parents into three sets that don't share any common parent IDs
		Set<Integer> parentsIntersection = new HashSet<>();
		parentsIntersection.addAll(localActions.parents());
		parentsIntersection.retainAll(remoteActions.parents());
		localActions.parents().removeAll(parentsIntersection);
		remoteActions.parents().removeAll(parentsIntersection);
		
		// apply local-only ande remote-only insert/delete actions
		applyActions(localActions);
		applyActions(remoteActions);		
		
		// apply the rest of the insert/delete actions
		for (int parentID : parentsIntersection) {
			throw new RuntimeException("not yet implemented");
		}
		
		// TODO: apply all update actions
		
		
	}
	
	// applys actions from one action set that doesn't interfere with the other action set
	private void applyActions(ActionSet actions) {
		for (int parentID : actions.parents()) {
			// apply deletes then inserts
			for (Delete delete : actions.getDeleteMap(parentID).values())
				delete.apply();
			for (Insert insert : actions.getInsertMap(parentID).values())
				insert.apply();
		}
	}
	
	// wraps an unsolvable conflict with conflict identifiable text
	// returns a new base node if it doesn't exist
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