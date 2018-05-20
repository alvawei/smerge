package smerge.ast.actions;

import java.util.Comparator;
import java.util.Iterator;
import java.util.Set;
import java.util.TreeSet;

import smerge.ast.ASTNode;

public class ChildrenSet implements Iterable<ASTNode> {
	// TreeSet children
	private TreeSet<ASTNode> children;
	
	public ChildrenSet() {
        children = new TreeSet<ASTNode>((a, b) -> a.getPosition().compareTo(b.getPosition()));
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
