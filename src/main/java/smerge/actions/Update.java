package smerge.actions;

import smerge.ast.ASTNode;


/**
 * Represents an updated line of code. It is identified in Differ.java,
 *  and is merged (if possible) in the ActionMerger class.
 * 
 * @author Jediah Conochan, Steven Miller (documentation)
 */
public class Update implements Action {
	
	private ASTNode base;
	private ASTNode edit;
	
	/**
	 * @param base base node
	 * @param edit edit node (either local or remote)
	 */
	public Update(ASTNode base, ASTNode edit) {
		this.base = base;
		this.edit = edit;
		
	}
	
	/**
	 * @return the base node
	 */
	public ASTNode getBase() {
		return base;
	}
	
	/**
	 * @return the edit node
	 */
	public ASTNode getEdit() {
		return edit;
	}
	
	/*
	 * applies the action by replacing the previous node with the new one
	 */
	public void apply() {
		if (base.getIndentation() != edit.getIndentation())
			base.setIndentation(edit.getIndentation());
		if (!base.getContent().equals(edit.getContent()))
			base.setContent(edit.getContent());
	}
	
	/*
	 * Used for debugging
	 */
	public String toString() {
		return "Update " + base.getID();
	}

}
