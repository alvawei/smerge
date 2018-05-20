package smerge.ast;

import java.util.Iterator;
import java.util.SortedSet;
import java.util.TreeSet;

public class ChildrenSet implements Iterable<ASTNode> {
	// TreeSet children
	private SortedSet<ASTNode> children;
	private double prevPos;
	private double nextPos;
	
	public ChildrenSet() {
        children = new TreeSet<ASTNode>((a, b) -> a.getPosition().compareTo(b.getPosition()));
        prevPos = -1.0D;
        nextPos = 1.0D;
	}
	
	
	// adds child such that prev.position < child.position < next.position
	public void add(ASTNode prev, ASTNode child, ASTNode next) {
		if (next == null) {
			// send child to end of set
			child.setPosition(nextPos++);
		} else if (prev == null) {
			// send child to front of set
			child.setPosition(prevPos--);
		} else {
			child.setPosition(avg(prev, next));
		}
		children.add(child);
		
	}
	
	// add the given child to the end of the set
	public void add(ASTNode child) {
		add(null, child, null);
	}
	
	private double avg(ASTNode a, ASTNode b) {
		return (a.getPosition() + b.getPosition()) / 2;
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
