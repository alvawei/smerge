package smerge.ast;

import smerge.ast.actions.Action;
import smerge.ast.actions.Delete;
import smerge.ast.actions.Insert;
import smerge.ast.actions.Move;
import smerge.ast.actions.Update;

public class Match {
	
	public static final int BASE = 0;
	public static final int LOCAL = 1;
	public static final int REMOTE = 2;
	
	public static final int DELETE = 0;
	public static final int INSERT = 1;
	public static final int UPDATE = 2;
	public static final int MOVE = 3;
	
	public int id;
	private ASTNode[] nodes;
	private Action[] actions;
	
    public Match(int id) {
    	this.id = id;
    	this.nodes = new ASTNode[3];
    	this.actions = new Action[4];
    }
    
    public void addNode(ASTNode node, int version) {
    	nodes[version] = node;
    }
    
    public ASTNode base() {
    	return nodes[BASE];
    }
    
    public ASTNode local() {
    	return nodes[LOCAL];
    }
    
    public ASTNode remote() {
    	return nodes[REMOTE];
    }
    
	public void addInsert(ASTNode parent, ASTNode child, int position) {
		actions[INSERT] = new Insert(parent, child, position);
		
	}
	
	public void addDelete(ASTNode parent, ASTNode child, int position) {
		if (actions[UPDATE] != null) {
			throw new RuntimeException("unmergable conflict: node delted and updated");
		}
		actions[DELETE] = new Delete(parent, child, position);
	}

	public void addUpdate(ASTNode before, ASTNode after) {
		if (actions[UPDATE] != null) {
			if (before.getType() == ASTNode.IMPORT) {
				// merge imports
				((Update) actions[UPDATE]).after.label += before.label + after.label;
				return;
			} else if (before.getType() == ASTNode.COMMENT) {
				// keep base comment
				actions[UPDATE] = null;
			} else {
				throw new RuntimeException("unmergable conflict: two updates " + id);
			}
		}
		actions[UPDATE] = new Update(before, after);
	}
	
	public void addMove(Insert ins, Delete del) {
		if (actions[DELETE] != null) {
			throw new RuntimeException("unmergable conflict: node deleted and moved");
		} else {
			actions[MOVE] = new Move(ins, del);
		}
	}
	
	public Action[] actions() {
		return actions;
	}
	
	public String toString() {
		String b = base() == null ? "0" : "1";
		String l = local() == null ? "0" : "1";
		String r = remote() == null ? "0" : "1";

		return "" + id + "(" + b + l + r + ")";
	}
}
