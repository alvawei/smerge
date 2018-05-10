package smerge.ast;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.github.difflib.DiffUtils;
import com.github.difflib.algorithm.DiffException;
import com.github.difflib.patch.Delta;
import com.github.difflib.patch.Patch;

import smerge.ast.ASTMatcher.Match;
import smerge.ast.actions.Action;
import smerge.ast.actions.ActionSet;

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
	
	public ActionSet diff() {
		// for each id, there are are 1-3 nodes
		ActionSet actions = new ActionSet();
		List<Match> matches = matcher.matches();
		for (int i = 1; i < matches.size(); i++) { // start at 1 to skip root
			Match m = matches.get(i);
			addActions(actions, matches, m.base(), m.local());
			addActions(actions, matches, m.base(), m.remote());
		}
		
		return actions;
	}
	
	// node is either local or remote node
	public void addActions(ActionSet actions, List<Match> matches, ASTNode base, ASTNode node) {
		if (base == null){
			if (node != null) {
				// a new node was inserted
				ASTNode parent = node.parent;
				int position = parent.children().indexOf(node);
				ASTNode baseParentEquivalent = matches.get(parent.getID()).base();
				actions.addInsert(baseParentEquivalent, node, position);
			}
		} else if (node == null) {
			// node was deleted
			ASTNode parent = node.parent;
			int position = parent.children().indexOf(node);
			ASTNode baseParentEquivalent = matches.get(parent.getID()).base();
			actions.addDelete(baseParentEquivalent, node, position);
		} else {
			int baseParentID = base.parent.getID();
			int nodeParentID = node.parent.getID();
			
			if (baseParentID != nodeParentID) {
				// node must have been moved
				// actions.addMove();
			}
			
			if (base.label.equals(node.label)) {
				// node updated
				// actions.addUpdate();
			}
			
		}
	}

	// merges the base->local and base->remote diffs
	// returns null if not possible
	public List<Action> mergedDiff() {
		List<Action> actions = new ArrayList<Action>();

		return null;
	}
	
	public static List<Action> lineBasedDiff(AST src, AST dest) throws DiffException {
		Map<Integer, ArrayList<Integer>> srcEncoding= new HashMap<>();
		src.getRoot().encode(srcEncoding);
		Map<Integer, ArrayList<Integer>> destEncoding = new HashMap<>();
		dest.getRoot().encode(destEncoding);

		
		List<Integer> original = srcEncoding.get(0);
		List<Integer> revised = destEncoding.get(0);

		Patch<Integer> patch = DiffUtils.diff(original, revised);
		
		        
		for (Delta delta : patch.getDeltas()) {
		    System.out.println(delta);
		}
		
		return null;
	}
	
}
