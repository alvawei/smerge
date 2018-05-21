package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Shift {
	
	private ASTNode parent;
	private ASTNode child;
	public int oldPosition;
	public int newPosition;
	
	public Shift(ASTNode parent, ASTNode child, int oldPosition, int newPosition) {
		this.parent = parent;
		this.child = child;
		this.oldPosition = oldPosition;
		this.newPosition = newPosition;
	}
}
