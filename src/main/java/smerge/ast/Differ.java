package smerge.ast;

import java.util.List;

import smerge.ast.Match;
import smerge.ast.actions.ActionSet;
import smerge.ast.actions.Delete;
import smerge.ast.actions.Insert;

// produces an ActionSet given 3 trees
public class Differ {
	
	public static ActionSet diff(AST base, AST local, AST remote) throws MergeException {
		// match the nodes between the three trees
		// note the matcher constructor indirectly calls detectActions()
		// we could combine this class with the Matcher class easily if we wanted
		Matcher matcher = new Matcher(base, local, remote);
		ActionSet actions = new ActionSet(matcher.matches());
		return actions;
	}
	
	// edit node is either local or remote node
	// this is called from Matcher while matching
	public static void detectActions(List<Match> matches, int id, boolean isLocal) throws MergeException {
		Match m = matches.get(id);
		ASTNode base = m.getBaseNode();
		ASTNode edit = isLocal ? m.getLocalNode() : m.getRemoteNode();
		if (base == null){
			if (edit != null) {
				// a new node was inserted
				ASTNode parent = edit.parent;
				int position = parent.children().indexOf(edit);
				ASTNode baseParentEquivalent = matches.get(parent.getID()).getBaseNode();
				m.addInsert(baseParentEquivalent, edit, position);
			}
		} else if (edit == null) {
			// node was deleted
			ASTNode parent = base.parent;
			int position = parent.children().indexOf(base);
			m.addDelete(parent, position);
		} else {
			int baseParentID = base.parent.getID();
			int nodeParentID = edit.parent.getID();
			
			if (baseParentID != nodeParentID) {
				// node must have been moved
				// need to also see if node changed position
				base.indentation = edit.indentation;
				ASTNode srcParent = matches.get(baseParentID).getBaseNode();
				int srcPos = srcParent.children().indexOf(base);
				Delete del = new Delete(srcParent, srcPos);
				
				ASTNode destParent = matches.get(nodeParentID).getBaseNode();
				// check if it was a move to a node not yet in base
				if (destParent == null) {
					destParent = edit.parent;
				}
				int destPos = edit.parent.children().indexOf(edit);
				Insert ins = new Insert(destParent, edit, destPos);
				
				m.addMove(ins, del);
			}
			if (!base.getContent().equals(edit.getContent())) {
				// node updated
				m.addUpdate(base, edit);
			}			
		}
	}
}
