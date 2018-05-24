package smerge.ast;

import smerge.actions.Action;
import smerge.actions.Delete;
import smerge.actions.Insert;
import smerge.actions.Move;
import smerge.actions.Update;


// a match object contains up to three versions of an ASTNode (base, local, and remote versions)

// this object allows us to determine the diff between two trees
// for example if a base version of this node exists and a local version does not,
// then the node must have been deleted in local

// this object also is used for merging two diff actions by keeping track of all possible actions
// for example, during iteration, if an update on this node is detected from base to local then we record it
// later on, if we detect an update on this node from base to remote, then we merge the updates 
// if possible (such as if this node is an import node), otherwise a MergeException is thrown

public class Match {
	
	private int id;
	private ASTNode base, local, remote;	
	
    public Match(int id) {
    	this.id = id;
    }
    
    public int getID() {
    	return id;
    }
    
    public Match setBaseNode(ASTNode base) {
    	base.setID(id);
    	this.base = base;
    	return this;
    }
    
    public Match setEditNode(ASTNode edit, boolean isLocal) {
    	edit.setID(id);
    	if (isLocal) {
        	this.local = edit;
    	} else {
    		this.remote = edit;
    	}
    	return this;
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
    
    public String toString() {
    	String baseString = base == null ? null : base.getContent();
    	String localString = local == null ? null : local.getContent();
    	String remoteString = remote == null ? null : remote.getContent();
    	return baseString + "\n" + localString + "\n" + remoteString;

    	
    }
}
