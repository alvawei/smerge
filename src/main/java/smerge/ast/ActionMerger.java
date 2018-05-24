package smerge.ast;

import smerge.ast.actions.ActionSet;

// this class merges two action sets and applys the merged actions onto the base tree
public class ActionMerger {
	
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
	
	
	
	public static void merge(ActionSet localActions, ActionSet remoteActions) {
		
	}
	
	private static void mergeImports() {
		
	}
}