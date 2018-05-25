package smerge.ast;

import java.util.ArrayList;
import java.util.List;
import java.util.Stack;
import java.util.Iterator;

/**
 * An ASTNode object represents a node of an abstract syntax tree.
 * Each ASTNode encapsulates a type, source code content, and source code indentation.
 * 
 * @author Jediah Conachan
 */

public class ASTNode {
	
	/**
	 * Enum Type for representing the type of an ASTNode.
	 */
	public enum Type {
		ROOT, IMPORT, WHITESPACE,
		CLASS, METHOD,
		IF_STATEMENT, WHILE_LOOP, FOR_LOOP,
		ASSIGNMENT, RETURN,
		COMMENT, BLOCK_COMMENT, PLACEHOLDER
	}
	
	private Type type;
	private String content;
	private int indentation;

	private ASTNode parent;
	private List<ASTNode> children;
	
	private int id;
	
	/**
	 * Constructs an ASTNode with the given type, content, and indentation
	 * @param type ASTNode.Type of the node
	 * @param content from the source file
	 * @param indentation from the source file
	 */
	public ASTNode(Type type, String content, int indentation) {
		this.type = type;
		this.content = content;
		this.indentation = indentation;
		this.children = new ArrayList<>();
		this.id = -1;
	}

	/**
	 * Constructs an empty root ASTNode
	 */
	public ASTNode() {
		this(Type.ROOT, "@root", -1);
	}
	
	/**
	 * Returns a direct list of this node's children. 
	 * Modifying the returned list also modifies the children of this node.
	 * @return a List of ASTNode objects
	 */
	public List<ASTNode> children() {
		return children;
	}
	
	/**
	 * Adds the given child as the last child of this node.
	 * @param child to be added
	 */
	public void addChild(ASTNode child) {
		if (child.parent != null) child.parent.children.remove(child);
		children.add(child);
		child.parent = this;
	}
	
	/**
	 * Returns the parent of this node (null if root)
	 * @return ASTNode parent
	 */
	public ASTNode getParent() {
		return parent;
	}
	
	public int getIndentation() {
		return indentation;
	}
	
	public String getContent() {
		return content;
	}
	
	public void setParent(ASTNode parent) {
		this.parent = parent;
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
	
	public boolean isPlaceHolder() {
		return this.type == Type.PLACEHOLDER;
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
	
	public int getPosition() {
		return parent.children.indexOf(this);
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
	
	// debugging method
	public String debugNode() {
		return "(" + id + ")" + indentation + content;
	}
	
	// debugging method
	public void debugTree(StringBuilder sb, String indent) {
		String idString = "(" + id;
		if (parent != null) {
			idString += ":" + parent.getID() + "[" + parent.children.indexOf(this) + "]";
		}
		idString += ")";
		for (int i = 0; i < 15 - idString.length(); i++) idString += " ";

		sb.append(idString + indent + content + "\n");
		if (children == null) {
			System.out.println(debugNode());
			throw new RuntimeException("why u null");
		}
		for (ASTNode child : children) {
			if (child.getID() == 0) {
				System.out.println(id);
				throw new RuntimeException("why u root");
			}
			child.debugTree(sb, indent + "    ");
		}
	}
}
