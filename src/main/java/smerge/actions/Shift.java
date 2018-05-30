package smerge.actions;

import smerge.ast.ASTNode;

public class Shift {
	
	private ASTNode baseParent;
	private ASTNode baseChild;
	protected int oldPosition;
	
	private ASTNode editParent;
	private ASTNode editChild;
	protected int newPosition;
	
	public Shift(ASTNode baseParent, ASTNode baseChild, int oldPosition,
			ASTNode editParent, ASTNode editChild, int newPosition) {
		this.baseParent = baseParent;
		this.baseChild = baseChild;
		this.oldPosition = oldPosition;
		this.editParent = editParent;
		this.editChild = editChild;
		this.newPosition = newPosition;
	}
	
	public ASTNode getBaseParent() {
		return baseParent;
	}
	
	public ASTNode getBaseChild() {
		return baseChild;
	}
	
	public ASTNode getEditParent() {
		return editParent;
	}
	
	public ASTNode getEditChild() {
		return editChild;
	}
}
