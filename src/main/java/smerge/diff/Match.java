package smerge.diff;

import smerge.actions.Action;
import smerge.actions.Delete;
import smerge.actions.Insert;
import smerge.actions.Move;
import smerge.actions.Update;
import smerge.ast.ASTNode;


// a match object contains up to three versions of an ASTNode (base, local, and remote versions)
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
