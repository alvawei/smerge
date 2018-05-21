package smerge.ast;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;
import java.util.Stack;
import java.util.Iterator;
import java.util.LinkedList;

/*
 * This abstract class is extended by language specific nodes (see smerge.ast.parsers)
 * Language specific nodes may be unecessary if unparsing is not done per node
 */

public class ASTNode {
	
	// two nodes can be matched only if they share the same type
	public enum Type {
		ROOT, IMPORT, WHITESPACE,
		CLASS, METHOD,
		IF_STATEMENT, WHILE_LOOP, FOR_LOOP,
		ASSIGNMENT, RETURN,
		COMMENT, BLOCK_COMMENT
	}
	
	protected Type type;
	protected String content;
	protected int indentation; 
	
	protected ASTNode parent;
	protected List<ASTNode> children;
	
	private int id;
	
	public ASTNode(Type type, String content, int indentation) {
		this.type = type;
		this.content = content;
		this.indentation = indentation;
		
		this.children = new ArrayList<>();
		this.id = -1;
	}

	// creates a root node
	public ASTNode() {
		this(Type.ROOT, "@root", -1);
	}
	
	// returns the direct list of this node's children
	public List<ASTNode> children() {
		return children;
	}
	
	// adds the given child to this node ands sets this node as its parent
	// removes the child node from its original parent
	public void addChild(ASTNode child) {
		if (child.parent != null) child.parent.children.remove(child);
		children.add(child);
		child.parent = this;
	}
	
	public ASTNode getParent() {
		return parent;
	}
	
	public int getIndentation() {
		return indentation;
	}
	
	public void setParent(ASTNode parent) {
		this.parent = parent;
	}
	

	
	public String getContent() {
		return content;
	}
	
	public void setContent(String content) {
		this.content = content;
	}
	
	public void setIndentation(int indentation) {
		this.indentation = indentation;
	}
	
	public Type getType() {
		return type;
	}

	public boolean isRoot() {
		return indentation == -1;
	}
	public boolean isLeafNode() {
		return children.isEmpty();
	}
	
	
	public int getID() {
		return id;
	}

	public void setID(int id) {
		this.id = id;
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
			// must add children in reverse order
			for (int i = node.children().size() - 1; i >= 0; i--) {
				stack.push(node.children().get(i));
			}
			return node;
		}
	}
	
	public String debugNode() {
		return "(" + id + ")" + indentation + content;
	}
	
	public void debugTree(StringBuilder sb, String indent) {
		String idString = "(" + id;
		if (parent != null) {
			idString += ":" + parent.getID() + "[" + parent.children.indexOf(this) + "]";
		}
		idString += ")";
		for (int i = 0; i < 15 - idString.length(); i++) idString += " ";

		sb.append(idString + indent + content + "\n");
		for (ASTNode child : children) {
			child.debugTree(sb, indent + "    ");
		}
	}
	
	@Override
	public boolean equals(Object o) {
		if (o instanceof ASTNode) {
			return id == ((ASTNode) o).getID();
		}
		return false;
	}
	
	public String toString() {
		return "" + id;
	}
}
