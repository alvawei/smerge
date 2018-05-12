package smerge.ast;

import java.util.List;

import smerge.ast.Match;
import smerge.ast.actions.Action;
import smerge.ast.actions.ActionSet;
import smerge.ast.actions.Delete;
import smerge.ast.actions.Insert;

// produces an ActionSet given 3 trees
public class Differ {
	
	public static ActionSet diff(AST base, AST local, AST remote) {
		Matcher matcher = new Matcher(base, local, remote);
		
		
		// for each id, there are are 1-3 nodes
		ActionSet actions = new ActionSet();
		List<Match> matches = matcher.matches();
		for (int i = 1; i < matches.size(); i++) { // start at 1 to skip root
			Match m = matches.get(i);
;
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
	public static void addActions(ActionSet actions, List<Match> matches, Match m, ASTNode node) {
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
			ASTNode parent = base.parent;
			int position = parent.children().indexOf(base);
			m.addDelete(parent, position);
		} else {
			int baseParentID = base.parent.getID();
			int nodeParentID = node.parent.getID();
			
			if (baseParentID != nodeParentID) {
				// node must have been moved
				// need to also see if node changed position
				base.indentation = node.indentation;
				ASTNode srcParent = matches.get(baseParentID).base();
				int srcPos = srcParent.children().indexOf(base);
				Delete del = new Delete(srcParent, srcPos);
				
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
