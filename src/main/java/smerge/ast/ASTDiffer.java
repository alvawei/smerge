package smerge.ast;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import smerge.ast.actions.Action;

// given two matched trees, produce a list of actions
// actions are things like move, add, remove nodes (lines) 
public class ASTDiffer {
	
	// possible solution:
	// generate a Map<Integer, Set/List<Integer>> for each tree, mapping node.getID() -> node.children().getID()
	// run line based diffing on each set
	
	private ASTMatcher matcher;
	
	public ASTDiffer(AST base, AST local, AST remote) {

		matcher = new ASTMatcher(base.getRoot(), local.getRoot(), remote.getRoot());
		// TODO: At this point, our matcher has gone through and identified all of the nodes (lines) that
		// are equivalent between base/local and base/remote. The trees may look completely different,
		// with nodes moved around, and I don't know how to deal with that. Wrote the helper methods to
		// get the Id's but might not be necessary.
		int baseId = matcher.getBaseId();
		int localId = matcher.getLocalId();
		int remoteId = matcher.getRemoteId();
	}

	// merges the base->local and base->remote diffs
	// returns null if not possible
	public List<Action> mergedDiff() {
		List<Action> actions = new ArrayList<Action>();

		return null;
	}
	
}
