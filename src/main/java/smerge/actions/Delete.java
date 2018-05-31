package smerge.actions;

import smerge.ast.ASTNode;

/**
 * The Delete class represents the deletion of a node. Once a Delete is
 * identified in Differ.java, it can be merged in the ActionMerger class.
 * 
 * @author Jediah Conachan, Steven Miller (documentation)
 */
public class Delete implements Action {
	
	private ASTNode child; // node to be deleted
	
	/**
	 * @param child the node to be deleted
	 */
	public Delete(ASTNode child) {
		this.child = child;
	}
	
	
	/**
	 * @return the position of the node to be deleted
	 */
	public int getPosition() {
		return child.getParent().children().indexOf(child);
	}
	
	/**
	 * @return the parent ID of the node to be deleted
	 */
	public int getParentID() {
		return child.getParent().getID();
	}
	

	/*
	 * Applies the action
	 */
	public void apply() {
		child.getParent().children().remove(child);
	}
	
	/*
	 * Used for debugging
	 */
	public String toString() {
		return "Delete " + child.getID();
	}

	
}
