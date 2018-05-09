package smerge.ast;

import java.util.Iterator;

public class ASTMatcher {
	
	//private static final double SIM_THRESHOLD = 0.8;
	//private static final double LEAF_THRESHOLD = 0.8;
	private int localMatchId = 0;
	private int remoteMatchId = 0;
	private int baseId = 0;	
	// traverse all the trees, match the nodes between the same trees with a unique id
	public ASTMatcher(ASTNode base, ASTNode local, ASTNode remote) {
		
		// label base
		int id = 0;
		Iterator<ASTNode> it = base.preOrder();
		while (it.hasNext()) {
			it.next().setID(id++);
		}
		// compare and label local
		baseId = id;
		localMatchId = match(local, base, id);
		remoteMatchId = match(remote, base, id);
		
	}
	
	// match t1 to t2
	// precondition: t2 is labeled
	// return the max id used + 1
	private int match(ASTNode t1, ASTNode t2, int id) {
		Iterator<ASTNode> it1 = t1.preOrder();
		it1.next().setID(0);
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
						break;
					}
				} else if (!isLeaf1 && !isLeaf2) {
					if (compareInner(next1, next2)) {
						next1.setID(next2.getID());
						break;
					}
				}
			}
			if (next1.getID() == 0) {
				next1.setID(id++);
			}
		}
		return id;
	}
	
	private boolean compareLeaf(ASTNode n1, ASTNode n2) {
		return n1.getType() == n2.getType() && n1.getLabel().equals(n1.getLabel());
	}
	
	// in the future change to comparing nodes?
	private boolean compareInner(ASTNode n1, ASTNode n2) {
		return n1.getType() == n2.getType() && n1.getLabel().equals(n1.getLabel());
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
}
