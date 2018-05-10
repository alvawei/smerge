package smerge.ast;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class ASTMatcher {
	
	public static final int BASE = 0;
	public static final int LOCAL = 1;
	public static final int REMOTE = 2;
	
	public class Match {
		private ASTNode[] nodes;
		
	    public Match() {
	    	this.nodes = new ASTNode[3];
	    }
	    
	    public void addNode(ASTNode node, int version) {
	    	nodes[version] = node;
	    }
	    
	    public ASTNode base() {
	    	return nodes[BASE];
	    }
	    
	    public ASTNode local() {
	    	return nodes[LOCAL];
	    }
	    
	    public ASTNode remote() {
	    	return nodes[REMOTE];
	    }
	}
	
	private List<Match> matches;
	
	//private static final double SIM_THRESHOLD = 0.8;
	//private static final double LEAF_THRESHOLD = 0.8;
	private int localMatchId = 0;
	private int remoteMatchId = 0;
	private int baseId = 0;	
	// traverse all the trees, match the nodes between the same trees with a unique id
	public ASTMatcher(ASTNode base, ASTNode local, ASTNode remote) {
		matches = new ArrayList<>();
		
		// label base
		int id = 0;
		Iterator<ASTNode> it = base.preOrder();
		while (it.hasNext()) {
			ASTNode next = it.next();
			next.setID(id);
			matches.add(new Match());
			matches.get(id).addNode(next, BASE);
			id++;
		}
		
		// compare and label local
		baseId = id;
		localMatchId = match(local, base, id, LOCAL);
		remoteMatchId = match(remote, base, id, REMOTE);
		
	}
	
	// match t1 to t2
	// precondition: t2 is labeled
	// return the max id used + 1
	private int match(ASTNode t1, ASTNode t2, int id, int version) {
		Iterator<ASTNode> it1 = t1.preOrder();
		ASTNode root = it1.next();
		root.setID(0);
		matches.get(0).addNode(root, version);
		while (it1.hasNext()) {
			ASTNode next1 = it1.next();
			boolean isLeaf1 = next1.children().isEmpty();
			Iterator<ASTNode> it2 = t2.preOrder();
			it2.next();
			while (it2.hasNext()) {
				ASTNode next2 = it2.next();
				boolean isLeaf2 = next2.children().isEmpty();
				if (isLeaf1 && isLeaf2) {
					if (compareLeaf(next1, next2)) {
						next1.setID(next2.getID());
						matches.get(next1.getID()).addNode(next1, version);
						break;
					}
				} else if (!isLeaf1 && !isLeaf2) {
					if (compareInner(next1, next2)) {
						next1.setID(next2.getID());
						matches.get(next1.getID()).addNode(next1, version);
						break;
					}
				}
			}
			if (next1.getID() == 0) {
				matches.add(new Match());
				matches.get(id).addNode(next1, version);
				next1.setID(id++);
			}
		}
		return id;
	}
	
	private boolean compareLeaf(ASTNode n1, ASTNode n2) {
		return n1.getType() == n2.getType() && n1.getLabel().equals(n2.getLabel());
	}
	
	// in the future change to comparing nodes?
	private boolean compareInner(ASTNode n1, ASTNode n2) {
		return n1.getType() == n2.getType() && n1.getLabel().equals(n2.getLabel());
	}

	public int getBaseId() {
		return baseId;
	}

	public int getLocalId() {
		return localMatchId;
	}

	public int getRemoteId() {
		return remoteMatchId;
	}
	
	public List<Match> matches() {
		return matches;
	}
}
