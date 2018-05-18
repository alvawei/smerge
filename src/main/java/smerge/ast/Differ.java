package smerge.ast;

import java.util.List;

import smerge.ast.Match;
import smerge.ast.actions.ActionSet;

// produces an ActionSet given 3 trees
public class Differ {
	
	private Matcher matcher;
	private ActionSet actions;
	private List<Match> matchList;
	
	public Differ(AST base, AST local, AST remote) throws MergeException {
		this.matcher = new Matcher(base, local, remote);
		this.matchList = matcher.matches();
		actions = new ActionSet();
	}
	
	public List<Match> getMatches() {
		return matchList;
	}
	
	// match the nodes between the three trees
	// note the matcher constructor indirectly calls detectActions()
	// we could combine this class with the Matcher class easily if we wanted	
	public ActionSet diff() throws MergeException {
		// for each match in mathces, all detect actions on base/local, base/remote
		for (Match m : matchList) {
			detectActions(m, true);
			detectActions(m, false);
		}
		return actions;
	}
	
	// edit node is either local or remote node
	// this is called from Matcher while matching
	public void detectActions(Match m, boolean isLocal) throws MergeException {
		int id = m.getID();
		if (id == 0) return; // don't do it with root
		ASTNode base = m.getBaseNode();
		ASTNode edit = isLocal ? m.getLocalNode() : m.getRemoteNode();
		if (base == null){
			if (edit != null) {
				// a new node was inserted
				
				// get the base parent equivalent
				ASTNode parent = matchList.get(edit.getParent().getID()).getBaseNode();
				if (parent == null) {
					// base parent equivalent doesn't exist, parent must also be an insert
					parent = edit.getParent();
				}
				actions.addInsert(parent, edit, edit.getParent().children().indexOf(edit));
			}
		} else if (edit == null) {
			// node was deleted from base
			actions.addDelete(base);
		} else {
			if (base.parent != null && edit.parent != null) {
				int baseParentID = base.getParent().getID();
				int editParentID = edit.getParent().getID();
				int baseNodeIndex = base.getParent().children().indexOf(base);
				int editNodeIndex = edit.getParent().children().indexOf(edit);
				
				if (baseParentID != editParentID || (baseNodeIndex != editNodeIndex)) {
					
					ASTNode parent = matchList.get(editParentID).getBaseNode();
					if (parent == null) {
						// base parent equivalent doesn't exist, parent must also be an insert
						parent = edit.getParent();
					}
					actions.addMove(parent, base, editNodeIndex);
					
					// also update indentation
					if (parent.getID() != editParentID) {
						actions.addUpdate(base, edit, isLocal);
					}
				
				}
			}
			if (!base.getContent().equals(edit.getContent())) {
				// node updated
				actions.addUpdate(base, edit, isLocal);
			}
		}
	}
}
