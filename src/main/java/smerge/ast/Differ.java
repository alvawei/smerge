package smerge.ast;

import java.util.List;

import smerge.ast.Match;
import smerge.ast.actions.ActionSet;
import smerge.ast.actions.Delete;
import smerge.ast.actions.Insert;
import smerge.ast.actions.Move;
import smerge.ast.actions.Update;

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
	public ActionSet diff(AST base, AST local, AST remote) throws MergeException {
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
		ASTNode base = m.getBaseNode();
		ASTNode edit = isLocal ? m.getLocalNode() : m.getRemoteNode();
		if (base == null){
			if (edit != null) {
				// a new node was inserted, insert it to the index
				ASTNode parent = edit.parent;
				int position = parent.children().indexOf(edit);
				ASTNode baseParentEquivalent = matchList.get(parent.getID()).getBaseNode();
				Insert ins = new Insert(parent, baseParentEquivalent, position);
				actions.addInsert(id, ins);
			}
		} else if (edit == null) {
			// node was deleted
			ASTNode parent = base.parent;
			int position = parent.children().indexOf(base);
			Delete del = new Delete(parent, position);
			actions.addDelete(id, del);
		} else {
			if (base.parent != null && edit.parent != null) {
				int baseParentID = base.parent.getID();
				int nodeParentID = edit.parent.getID();
				int baseNodeIndex = base.parent.children.indexOf(base);
				int editNodeIndex = edit.parent.children.indexOf(edit);
				
				if (baseParentID != nodeParentID || (baseNodeIndex != editNodeIndex)) {
					// node must have been moved to a different parent
					base.indentation = edit.indentation;
					ASTNode srcParent = matchList.get(baseParentID).getBaseNode();
					int srcPos = srcParent.children().indexOf(base);
					Delete del = new Delete(srcParent, srcPos);
					
					ASTNode destParent = matchList.get(nodeParentID).getBaseNode();
					// check if it was a move to a node not yet in base
					if (destParent == null) {
						destParent = edit.parent;
					}
					int destPos = edit.parent.children().indexOf(edit);
					Insert ins = new Insert(destParent, edit, destPos);
					Move move = new Move(ins, del);
					
					actions.addMove(id, move);
				} 
//					else if (baseNodeIndex != editNodeIndex) {
//					// the child node is moved but within the same parent index the same parent
//				}
			}
			if (!base.getContent().equals(edit.getContent())) {
				// node updated
				Update update = new Update(base, edit, isLocal);
				actions.addUpdate(id, update, isLocal);
			}
		}
	}
}
