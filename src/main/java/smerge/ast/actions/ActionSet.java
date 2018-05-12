package smerge.ast.actions;

import smerge.ast.Match;

import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;

// basically a tree diff
public class ActionSet {
	
	
	public List<Action> actions;
	
	public ActionSet(List<Match> matches) {
		actions = new ArrayList<>();
		for (Match m : matches) {
			for (Action a : m.actions()) {
				actions.add(a);
			}
		}
	}
	
	// returns true iff actions are merged into base tree
	public boolean apply() {
		// unwrap moves into single insert and delete
		for (int i = 0; i < actions.size(); i++) {
			if (actions.get(i) instanceof Move) {
				Move m = (Move) actions.get(i);
				actions.remove(i);
				actions.add(m.ins);
				actions.add(m.del);
			}
		}
		// sort actions to be applied in specifc order
		Collections.sort(actions, new ActionSort());
		
		for (Action a : actions) {
			a.apply();
		}
		return false;
	}
	

	public void add(Action a) {
		actions.add(a);
	}
	
	public class ActionSort implements Comparator<Action> {
		
		// order by action type: delete -> insert -> update

		@Override
		public int compare(Action o1, Action o2) {
			if (o1 instanceof Delete && !(o2 instanceof Delete))
				return -1;
			
			if (o2 instanceof Delete && !(o1 instanceof Delete))
				return 1;
			
				
				return 0;
		}
	}
	
	public String toString() {
		return actions.toString();
	}
}
