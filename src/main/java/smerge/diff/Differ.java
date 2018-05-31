package smerge.diff;

import java.util.List;

import smerge.actions.ActionSet;
import smerge.ast.AST;
import smerge.ast.ASTNode;

/**
 * A Differ object generates two different tree diffs (ActionSets), one from the base tree
 * to the local tree, one from the base tree to the remote tree.
 * 
 * @author Jediah Conachan, Steven Miller
 */
public class Differ {
	
	private Matcher matcher;
	private List<Match> matchList;
	
	/**
	 * 
	 * @param base base tree
	 * @param local local tree
	 * @param remote remote tree
	 */
	public Differ(AST base, AST local, AST remote)  {
		this.matcher = new Matcher(base, local, remote);
		this.matchList = matcher.matches();
	}
	
	
	/**
	 * @return the list of matches
	 */
	public List<Match> getMatches() {
		return matchList;
	}
	
	/**
	 * When called (from Merger.java), takes in two ActionSet objects and adds all
	 * of the actions by calling detectActions
	 * @param localActions actions applied to local tree
	 * @param remoteActions actions applied to remote tree
	 */
	public void diff(ActionSet localActions, ActionSet remoteActions) {
		// for each match in matches, all detect actions on base/local, base/remote
		for (Match m : matchList) {
			detectActions(m.getID(), m.getBaseNode(), m.getLocalNode(), localActions);
			detectActions(m.getID(), m.getBaseNode(), m.getRemoteNode(), remoteActions);
		}
		localActions.minimize();
		remoteActions.minimize();
	}
	
	/**
	 * This method does most of the work. It takes in two nodes,the base node and
	 * the edit node (either local or remote), and then determines whether that node
	 * was inserted, deleted, or updated, and adds the action to the ActionSet if one
	 * of those is true.
	 * @param id id of the match
	 * @param base base node of the match
	 * @param edit edit node of the match (either local or remote)
	 * @param actions the ActionSet we're storing all of the actions in
	 */
	public void detectActions(int id, ASTNode base, ASTNode edit, ActionSet actions) {
		if (id == 0) return; // don't do it with root
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
			// node was moved
			if (base.getParent() != null && edit.getParent() != null) {
				int baseParentID = base.getParent().getID();
				int editParentID = edit.getParent().getID();
				int baseNodeIndex = base.getParent().children().indexOf(base);
				int editNodeIndex = edit.getParent().children().indexOf(edit);
				
				ASTNode parent = matchList.get(editParentID).getBaseNode();				
				if (baseParentID != editParentID) {
					if (parent == null) {
						// base parent equivalent doesn't exist, parent must also be an insert
						parent = edit.getParent();
					}
					actions.addDelete(base);
					actions.addInsert(parent, edit, editNodeIndex);
					actions.addUpdate(base, edit);
					
				} else if (baseNodeIndex != editNodeIndex) {
					actions.addShift(parent, base, baseNodeIndex, edit.getParent(), edit, editNodeIndex);
				}
			}
			if (!base.getContent().equals(edit.getContent())) {
				// node updated
				actions.addUpdate(base, edit);
			}
		}
	}
}
