package smerge.ast.actions;

import java.util.List;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeSet;

import smerge.ast.ASTNode;

import java.util.ArrayList;
import java.util.Comparator;

// basically a tree diff
public class ActionSet {
	
	public List<Insert> inserts;
	public List<Delete> deletes;
	public List<Update> updates;
	public List<Move> moves;
	
	private SortedSet<Action> actions;
	
	public ActionSet() {
		actions = new TreeSet<Action>(new ActionSort());
	}
	
	// returns true iff actions are merged into base tree
	public boolean apply() {
		for (Action a : actions) {
			a.apply();
		}
		return false;
	}
	

	public void add(Action a) {
		actions.add(a);
	}
	
	public class ActionSort implements Comparator<Action> {

		@Override
		public int compare(Action o1, Action o2) {
			// TODO Auto-generated method stub
			return 0;
		}

		
	}
}
