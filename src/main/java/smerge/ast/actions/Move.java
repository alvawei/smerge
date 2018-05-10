package smerge.ast.actions;

import smerge.ast.ASTNode;

public class Move implements Action {
	
	private ASTNode parent;
	private ASTNode child; // node in 
	
	
	public void apply() {
		
	}
	
	public String toString() {
		return "Move";
	}
}
