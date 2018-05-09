package smerge.ast;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Stack;
import java.util.Iterator;
import java.util.LinkedList;

public class ASTNode {
	
	public static final int CLASS = 1;
	public static final int METHOD = 2;
	public static final int ASSIGNMENT = 3;
	public static final int RETURN = 4;
	public static final int IF_STATEMENT = 5;
	public static final int WHILE_LOOP = 6;
	public static final int FOR_LOOP = 7;
	public static final int WHITESPACE = 8;
	
	private int id;
	
	protected int type;
	protected String label;
	protected ASTNode parent;
	protected List<ASTNode> children;
	
	public ASTNode() {
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
	
	public String getLabel() {
		return label;
	}
	
	public int getType() {
		return type;
	}
	
	public Iterator<ASTNode> preOrder() {
		return new NodeIterator(this);
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
	
	public void encode(Map<Integer, ArrayList<Integer>> encoding) {
		if (!children.isEmpty()) {
			ArrayList<Integer> childrenIDList = new ArrayList<>();
			for (ASTNode child : children) {
				childrenIDList.add(child.getID());
				child.encode(encoding);
			}
			encoding.put(id, childrenIDList);
		}
	}
	
}
