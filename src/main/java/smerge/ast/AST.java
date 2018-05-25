package smerge.ast;

import java.util.Iterator;

import smerge.parsers.Parser;

/**
 * This class represents a generic Abstract Syntax Tree. It is a wrapper
 * around a root ASTNode.
 * 
 * @author Jediah Conachan
 */
public class AST implements Iterable<ASTNode> {
	
	// this is held onto for the toString() method
	private Parser parser;
	private ASTNode root;
	
	/**
	 * Constructs an AST
	 * @param root ASTNode
	 * @param parser used to parse this AST
	 */
	public AST(ASTNode root, Parser parser) {
		this.root = root;
		this.parser = parser;
	}
	
	/**
	 * Returns the root node of this tree
	 * @return ASTNode root
	 */
	public ASTNode getRoot() {
		return root;
	}	
	
	/**
	 * Returns a pre-order iterator over the nodes of this tree
	 * @return ASTNode Iterator
	 */
	public Iterator<ASTNode> iterator() {
		return root.preOrder();
	}

	/**
	 * Unparses this tree into a String representation of source code.
	 * Equivalent to Parser.unparse()
	 * @return String representation of this AST's source code
	 */
	public String toString() {
		return parser.unparse(this);
	}
	
	// used for debugging purposes
	public String debugTree() {
		StringBuilder sb = new StringBuilder();
		root.debugTree(sb, "");
		return sb.toString();
	}
}
