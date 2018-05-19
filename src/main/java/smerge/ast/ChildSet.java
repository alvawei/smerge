package smerge.ast;

import java.util.Iterator;
import java.util.SortedSet;
import java.util.TreeSet;

public class ChildSet implements Iterable<ASTNode> {
	
	private SortedSet<ASTNode> set;
	private Double prevPos = -1.0D;
	private Double nextPos = 1.0D;
	
	public ChildSet() {
		// sort by node position
		set = new TreeSet<>((a, b) -> a.getPosition().compareTo(b.getPosition()));
	}
	
	// adds the given child with the given position
	public void add(double position, ASTNode child) {
		child.setPosition(position);
		set.add(child);
	}
	
	// adds child between prev and next
	public void add(ASTNode prev, ASTNode child, ASTNode next) {
		if (next == null) {
			// add to end
			add(nextPos++, child);
		} else if (prev == null) {
			// add to beginning
			add(prevPos--, child);
		} else {
			// add between the two nodes
			double average = (prev.getPosition() + next.getPosition()) / 2;
			add(average, child);
		}
	}
	
	// removes the given child
	public void remove(ASTNode child) {
		set.remove(child);
	}
	
	public Iterator<ASTNode> iterator() {
		return set.iterator();
	}

}
