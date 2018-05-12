package smerge.ast;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.Iterator;
import java.util.LinkedList;

public abstract class ASTNode {
	
	
	public static final int ROOT = -2;
	public static final int CLASS = 1;
	public static final int METHOD = 2;
	public static final int ASSIGNMENT = 3;
	public static final int RETURN = 4;
	public static final int IF_STATEMENT = 5;
	public static final int WHILE_LOOP = 6;
	public static final int FOR_LOOP = 7;
	public static final int WHITESPACE = 8;
	public static final int IMPORT = 9;
	public static final int COMMENT = 10;
	public static final int BLOCK_COMMENT = 11;
	
	private int id;
	public int indentation;
	
	protected int type;
	public String label;
	protected ASTNode parent;
	protected List<ASTNode> children;
	
	public ASTNode() {
		this.type = ROOT;
		this.children = new ArrayList<>();
	}
	
	// used for matching
	public int getID() {
		return id;
	}
	
	// used for matching
	public void setID(int id) {
		this.id = id;
	}
	
	// returns the direct list of this node's children
	public List<ASTNode> children() {
		return children;
	}
	
	public ASTNode getParent() {
		return this.parent;
	}
	
	public void setParent(ASTNode parent) {
		this.parent = parent;
	}
	
	public void addChild(ASTNode child) {
		children.add(child);
		child.parent = this;
	}
	
	public String getLabel() {
		return label;
	}
	
	public int getType() {
		return type;
	}
	
	public Iterator<ASTNode> preOrder() {
		return new NodeIterator(this);
	}
	
	// used for update action
	public void update(ASTNode other) {
		// handeled in PythonNode
	}
	
	public void debugTree(StringBuilder sb, String indent) {
		sb.append(indent + "(" +  id + ") " + label);
		for (ASTNode child : children) {
			child.debugTree(sb, indent + "    ");
		}
	}
		
	public void idTree(StringBuilder sb, String indent) {
		sb.append(indent + id + "\n");
		for (ASTNode child : children) {
			child.idTree(sb, indent + " ");
		}
	}
	
	public boolean isRoot() {
		return type == ROOT;
	}
	
	public boolean isLeafNode() {
		return children.isEmpty();
	}
	
	// pre-order iterator starting with the given root
	private class NodeIterator implements Iterator<ASTNode> {
		
		private Queue<ASTNode> queue;
		
		public NodeIterator(ASTNode node) {
	        queue = new LinkedList<>();
			queue.add(node);
		}

		@Override
		public boolean hasNext() {
			return !queue.isEmpty();
		}

		@Override
		public ASTNode next() {
			ASTNode node = queue.remove();
			for (ASTNode child : node.children()) {
				queue.add(child);
			}
			return node;

		}
		
	}
}
