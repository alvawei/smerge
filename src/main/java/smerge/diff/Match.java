package smerge.diff;

import smerge.ast.ASTNode;


/**
 * A Match object encapsulates up to three versions of an ASTNode (base, local, remote)
 * that share the same ID.
 * 
 * @author Jediah Conachan
 */
public class Match {
		
	private int id;
	private ASTNode base;
	private ASTNode local;
	private ASTNode remote;	
	
	/**
	 * Constructs an empty Match object for the given ID
	 * @param id
	 */
    public Match(int id) {
    	this.id = id;
    }
    
    /**
     * Sets the base node of this match
     * @param base
     * @return this Match
     */
    public Match setBaseNode(ASTNode base) {
    	base.setID(id);
    	this.base = base;
    	return this;
    }
    
    /**
     * Sets an edit node (local or remote) of this Match
     * @param edit node to be added
     * @param isLocal - true iff edit is from the local tree, false if from the remote tree
     * @return this Match
     */
    public Match setEditNode(ASTNode edit, boolean isLocal) {
    	edit.setID(id);
    	if (isLocal) {
        	this.local = edit;
    	} else {
    		this.remote = edit;
    	}
    	return this;
    }
    
    /**
     * Returns the id of this match
     * @return id
     */
    public int getID() {
    	return id;
    }
	
    /**
     * Returns the base node of this match
     * @return base ASTNode
     */
    public ASTNode getBaseNode() {
    	return base;
    }
    
    /**
     * Returns the local node of this match
     * @return local ASTNode
     */
    public ASTNode getLocalNode() {
    	return local;
    }
    
    /**
     * Returns the remote node of this match
     * @return remote ASTNode
     */
    public ASTNode getRemoteNode() {
    	return remote;
    }
}
