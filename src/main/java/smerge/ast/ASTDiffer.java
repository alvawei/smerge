package smerge.ast;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import smerge.ast.actions.Action;


public class ASTDiffer {
	
	// possible solution:
	// generate a Map<Integer, Set/List<Integer>> for each tree, mapping node.getID() -> node.children().getID()
	// run line based diffing on each set
	
	private ASTMatcher matcher;
	
	public ASTDiffer(AST base, AST local, AST remote) {
		
		matcher = new ASTMatcher(base.getRoot(), local.getRoot(), remote.getRoot());
		
		// if trees are equal then no diff needed (probably an import conflict)
		// gotta actually implement equals() method though
		// or figure it out while matching
		if (!(base.equals(local) && base.equals(remote))) {
			
		}
		
	}
	
	// merges the base->local and base->remote diffs
	// returns null if not possible
	public List<Action> mergedDiff() {
		
		return null;
	}
	
}
