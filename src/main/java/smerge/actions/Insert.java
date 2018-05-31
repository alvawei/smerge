package smerge.actions;

import smerge.ast.ASTNode;

/**
 * The Insert class represents the inserting of a node into a tree. Once
 * an Insert is identified in Differ.java, it can be merged in the ActionMerger
 * class.
 * 
 * @author Jediah Conachan, Steven Miller (documentation)
 */
public class Insert implements Action {
	
	private ASTNode parent; // node the child is inserted into (in base tree)
	private ASTNode child; // child introduced in edit tree (base if in move)
	private int position;
	
	/**
	 * @param parent the parent node
	 * @param child the child node
	 * @param position the position of the insert of the child
	 */
	public Insert(ASTNode parent, ASTNode child, int position) {
		this.parent = parent;
		this.child = child;
		this.position = position;
	}
	
	/*
	 * Applies the Insert action
	 */
	public void apply() {
		parent.children().add(position, child);
		child.setParent(parent);

	}
	
	/**
	 * @return the position of the insert
	 */
	public int getPosition() {
		return position;
	}
	
	/**
	 * @param set the position of the insert
	 */
	public void setPosition(int position) {
		this.position = position;
	}
	
	/**
	 * @return the id of the parent
	 */
	public int getParentID() {
		return parent.getID();
	}
	
	/**
	 * @return the parent node
	 */
	public ASTNode getParent() {
		return parent;
	}
	
	/**
	 * @return the child node
	 */
	public ASTNode getChild() {
		return child;
	}
	
	/*
	 * Useful for debugging
	 */
	public String toString() {
		return "Insert " + child.getID() + 
				"->" + parent.getID() + 
				"[" + position + "]";
	}

}
