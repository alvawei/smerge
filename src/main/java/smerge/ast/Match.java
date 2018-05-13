package smerge.ast;

import smerge.ast.actions.Action;
import smerge.ast.actions.Delete;
import smerge.ast.actions.Insert;
import smerge.ast.actions.Move;
import smerge.ast.actions.Update;


// a match object contains up to three versions of an ASTNode (base, local, and remote versions)

// this object allows us to determine the diff between two trees
// for example if a base version of this node exists and a local version does not,
// then the node must have been deleted in local

// this object also is used for merging two diff actions by keeping track of all possible actions
// for example, during iteration, if an update on this node is detected from base to local then we record it
// later on, if we detect an update on this node from base to remote, then we merge the updates 
// if possible (such as if this node is an import node), otherwise a MergeException is thrown

public class Match {
	
	// positions of specific nodes in the node array below
	public static final int BASE = 0;
	public static final int LOCAL = 1;
	public static final int REMOTE = 2;
	
	private int id;
	private ASTNode base, local, remote;
	
	private Insert insert;
	private Delete delete; 
	private Move move;
	private Update update;
	
	
    public Match(int id) {
    	this.id = id;
    }
    

    
	public void addInsert(ASTNode parent, ASTNode child, int position) {
		insert = new Insert(parent, child, position);
		
	}
	
	public void addDelete(ASTNode parent, int position) {
		// unmergable if the other user deleted this node
		if (update != null) {
			throw new RuntimeException("unmergable conflict: node delted and updated");
		}
		delete = new Delete(parent, position);
	}

	public void addUpdate(ASTNode before, ASTNode after) {
		if (update != null) {
			if (before.getType() == ASTNode.Type.IMPORT) {
				// merge imports
				update.after.label += before.label + after.label;
				return;
			} else if (before.getType() == ASTNode.Type.COMMENT) {
				// keep base comment
				update = null;
			} else {
				throw new RuntimeException("unmergable conflict: two updates " + id);
			}
		}
		update = new Update(before, after);
	}
	
	public void addMove(Insert ins, Delete del) {
		// unmergable if other user deleted this node
		if (delete != null) {
			throw new RuntimeException("unmergable conflict: node deleted and moved");
		} else {
			move = new Move(ins, del);
		}
	}
	
    public void setBaseNode(ASTNode base) {
    	base.setID(id);
    	this.base = base;
    }
    
    public void setEditNode(ASTNode edit, boolean isLocal) {
    	edit.setID(id);
    	
    	if (isLocal) {
        	this.local = edit;
    	} else {
    		this.remote = edit;
    	}

    }
	
	public Action[] actions() {
		return new Action[]{insert, delete, move, update};
	}
	
    public ASTNode getBaseNode() {
    	return base;
    }
    
    public ASTNode getLocalNode() {
    	return local;
    }
    
    public ASTNode getRemoteNode() {
    	return remote;
    }
}
