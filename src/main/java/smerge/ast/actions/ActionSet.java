package smerge.ast.actions;

import java.util.List;
import java.util.ArrayList;

// basically a tree diff
public class ActionSet {
	
	public List<Insert> inserts;
	public List<Delete> deletes;
	public List<Update> updates;
	public List<Move> moves;
	
	
	// returns an action set
	// use to merge the two tree diffs
	// returns null if there is a conflict
	
	public static ActionSet merge(ActionSet a, ActionSet b) {
		
		
		return null;
	}

}
