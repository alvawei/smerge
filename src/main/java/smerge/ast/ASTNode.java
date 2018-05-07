package smerge.ast;

import java.util.ArrayList;
import java.util.List;
import java.util.Stack;
import java.util.Iterator;

public class ASTNode {
	
	private int id;
	
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
	
	public Iterator<ASTNode> preOrder() {
		return new NodeIterator(this);
	}
	
	// pre-order iterator starting with the given root
	private class NodeIterator implements Iterator<ASTNode> {
		
		private Stack<ASTNode> stack;
		
		public NodeIterator(ASTNode node) {
	        stack = new Stack<>();
			stack.push(node);
		}

		@Override
		public boolean hasNext() {
			return !stack.isEmpty();
		}

		@Override
		public ASTNode next() {
			ASTNode node = stack.pop();
			for (ASTNode child : node.children()) {
				stack.push(child);
			}
			return node;

		}
		
	}
	
	/* ignore this
	private void encode(Map<Integer, ArrayList<Integer>> encoding) {
		if (!children.isEmpty()) {
			ArrayList<Integer> childrenIDList = new ArrayList<>();
			for (ASTNode child : children) {
				childrenIDList.add(child.getID());
				encode(child, encoding);
			}
			encoding.put(current.getID(), childrenIDList);
		}
	} */
	
}
