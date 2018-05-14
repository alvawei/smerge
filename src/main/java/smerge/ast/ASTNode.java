package smerge.ast;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.Iterator;
import java.util.LinkedList;

public abstract class ASTNode {
	
	public enum Type {
		ROOT, IMPORT, WHITESPACE,
		CLASS, METHOD,
		IF_STATEMENT, WHILE_LOOP, FOR_LOOP,
		ASSIGNMENT, RETURN,
		COMMENT, BLOCK_COMMENT
	}
	
	private int id;
	public int indentation;
	
	protected Type type;
	public String label;
	protected ASTNode parent;
	protected List<ASTNode> children;
	
	public ASTNode() {
		this.type = Type.ROOT;
		this.children = new ArrayList<>();
		this.id = -1;
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
		return parent;
	}
	
	public void setParent(ASTNode parent) {
		this.parent = parent;
	}
	
	// adds the given child to this node ands sets this node as its parent
	// removes the child node from its original parent
	public void addChild(ASTNode child) {
		if (child.parent != null) child.parent.children.remove(child);
		children.add(child);
		child.parent = this;
	}
	
	public String getLabel() {
		return label;
	}
	
	public Type getType() {
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
