package smerge.actions;

import smerge.ast.ASTNode;

/**
 * When a node is inserted underneath a parent, the index of the nodes
 * to the right are incremented by one. The purpose of the shift class is
 * to avoid classify shifted nodes as a "move" (an insert/delete). When
 * we examine the rest of the child list, we ignore the index change if
 * it was only the result of shifting.
 * 
 * @author Jediah Conachan, Steven Miller (documentation only)
 *
 */
public class Shift {
	
	private ASTNode baseParent;
	private ASTNode baseChild;
	protected int oldPosition;
	
	private ASTNode editParent;
	private ASTNode editChild;
	protected int newPosition;
	
	/**
	 * @param baseParent
	 * @param baseChild
	 * @param oldPosition
	 * @param editParent
	 * @param editChild
	 * @param newPosition
	 */
	public Shift(ASTNode baseParent, ASTNode baseChild, int oldPosition,
			ASTNode editParent, ASTNode editChild, int newPosition) {
		this.baseParent = baseParent;
		this.baseChild = baseChild;
		this.oldPosition = oldPosition;
		this.editParent = editParent;
		this.editChild = editChild;
		this.newPosition = newPosition;
	}
	
	/**
	 * @return the base nodes parent
	 */
	public ASTNode getBaseParent() {
		return baseParent;
	}
	
	/**
	 * @return the base nodes child
	 */
	public ASTNode getBaseChild() {
		return baseChild;
	}
	
	/**
	 * @return the edit (either local or remote) nodes parent
	 */
	public ASTNode getEditParent() {
		return editParent;
	}
	
	/**
	 * @return the edit (either local or remote) nodes child
	 */
	public ASTNode getEditChild() {
		return editChild;
	}
}
