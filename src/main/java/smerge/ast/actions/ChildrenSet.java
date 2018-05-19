package smerge.ast.actions;

import java.util.Comparator;
import java.util.Iterator;
import java.util.Set;
import java.util.TreeSet;

import smerge.ast.ASTNode;

public class ChildrenSet {
	// TreeSet children
	private TreeSet<ASTNode> children;
	
	public ChildrenSet() {
        Set<ASTNode> sorted = new TreeSet<ASTNode>(new Comparator<ASTNode>() {
			// sorts set of children by their position field
        	@Override
			public int compare(ASTNode node1, ASTNode node2) {
        		return Double.compare(node1.getPosition(), node2.getPosition());
			}
        });
	}
	
	public void add(ASTNode child) {
		children.add(child);
	}
	
	public void remove(ASTNode child) {
		children.remove(child);
	}
	
	public int size() {
		return children.size();
	}
	
	public void clear() {
		for (ASTNode node : children) {
			this.remove(node);
		}
	}
	
	public boolean isEmpty() {
		return children.isEmpty();
	}
	
	public boolean contains(ASTNode node) {
		return children.contains(node);
	}
	
	public Iterator<ASTNode> iterator() {
		return children.iterator();
	}
}
