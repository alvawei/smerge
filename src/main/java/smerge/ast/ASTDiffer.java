package smerge.ast;

import java.util.List;

import smerge.ast.Match;
import smerge.ast.actions.Action;
import smerge.ast.actions.ActionSet;
import smerge.ast.actions.Delete;
import smerge.ast.actions.Insert;

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
		
		System.out.println("matches = " + matcher.matches());
	}
	
	public ActionSet diff() {
		// for each id, there are are 1-3 nodes
		ActionSet actions = new ActionSet();
		List<Match> matches = matcher.matches();
		for (int i = 1; i < matches.size(); i++) { // start at 1 to skip root
			Match m = matches.get(i);
			
			ASTNode base = m.base();
			ASTNode local = m.local();
			ASTNode remote = m.remote();

			addActions(actions, matches, m, m.local());
			addActions(actions, matches, m, m.remote());
			
			
			
			for (Action a : m.actions()) {
				if (a != null) {
					actions.add(a);
				}
			}
		}
		
		return actions;
	}
	
	// node is either local or remote node
	public void addActions(ActionSet actions, List<Match> matches, Match m, ASTNode node) {
		ASTNode base = m.base();
		if (base == null){
			if (node != null) {
				// a new node was inserted
				ASTNode parent = node.parent;
				int position = parent.children().indexOf(node);
				ASTNode baseParentEquivalent = matches.get(parent.getID()).base();
				m.addInsert(baseParentEquivalent, node, position);
			}
		} else if (node == null) {
			// node was deleted
			ASTNode parent = node.parent;
			int position = parent.children().indexOf(node);
			ASTNode baseParentEquivalent = matches.get(parent.getID()).base();
			m.addDelete(baseParentEquivalent, node, position);
		} else {
			int baseParentID = base.parent.getID();
			int nodeParentID = node.parent.getID();
			
			if (baseParentID != nodeParentID) {
				// node must have been moved
				// need to also see if node changed position
				base.indentation = node.indentation;
				ASTNode srcParent = matches.get(baseParentID).base();
				int srcPos = srcParent.children().indexOf(base);
				Delete del = new Delete(srcParent, base, srcPos);
				
				ASTNode destParent = matches.get(nodeParentID).base();
				// check if it was a move to a node not yet in base
				if (destParent == null) {
					destParent = node.parent;
				}
				int destPos = node.parent.children().indexOf(node);
				Insert ins = new Insert(destParent, base, destPos);
				
				m.addMove(ins, del);
			}
			if (!base.label.equals(node.label)) {
				// node updated
				m.addUpdate(base, node);
			}			
		}
	}
}
