package smerge.ast;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Matcher {
	
	// smaller similarity = good
	private static final double SIM_THRESHOLD = 0.3;

		
	private List<Match> matches;
	private int nextID; // the next id to be given to a new matching

	public Matcher(AST baseTree, AST localTree, AST remoteTree) throws MergeException {	
		matches = new ArrayList<>();
		
		labelBaseTree(baseTree);
		match(baseTree, localTree, true);
		match(baseTree, remoteTree, false);
	}
	
	// match editTree's nodes to baseTree's
	// editTree is localTree if isLocal, otherwise editTree is remoteTree
	public void match(AST baseTree, AST editTree, boolean isLocal) throws MergeException {
		Set<Integer> matchedIDs = new HashSet<Integer>();
		matches.get(0).setEditNode(editTree.getRoot(), isLocal);
		matchedIDs.add(0);
		
		// compare each node in the baseTree to each node in editTree
		for (ASTNode edit : editTree) {
			if (edit.getID() == 0) continue;
			for (ASTNode base : baseTree) {
				
				// can't be matched, skip
				if (matchedIDs.contains(base.getID()) || base.getType() != edit.getType()) 
					continue;
				
				if ((base.isLeafNode() && compareLeafNodes(base, edit)) ||
						(!base.isLeafNode() && compareInnerNodes(base, edit))) {
					// it's a match
					int id = base.getID();
					matches.get(id).setEditNode(edit, isLocal);
					matchedIDs.add(id);
					
					// do this now to detect conflicting actions early
					// Differ.detectActions(matches, id, isLocal);					
				}	
				
			}
			if (edit.getID() == -1) {
				// no possible match found, create new one
				matches.add(new Match(nextID++).setEditNode(edit, isLocal));
			}
		}
	}
	
	private void labelBaseTree(AST baseTree) {
		nextID = 0;
		for (ASTNode node : baseTree) {
			matches.add(new Match(nextID++).setBaseNode(node));
		}
	}
	
	// return true iff these leaf nodes should be matched
	private boolean compareLeafNodes(ASTNode n1, ASTNode n2) {
		double similarity = (double) distance(n1.getContent(), n2.getContent()) / Math.max(n1.getContent().length(), n2.getContent().length());
		return similarity <= SIM_THRESHOLD;
	}
	
	// return true iff these non-leaf nodes should be matched
	// in the future change to comparing nodes?
	private boolean compareInnerNodes(ASTNode n1, ASTNode n2) {
		return  n1.getContent().equals(n2.getContent());
	}
	
	// calculates Levenshtein distance between two strings
	private static int distance(String a, String b) {
	    a = a.toLowerCase();
	    b = b.toLowerCase();
	    // i == 0
	    int [] costs = new int [b.length() + 1];
	    for (int j = 0; j < costs.length; j++) {
	        costs[j] = j;
	    }
	    for (int i = 1; i <= a.length(); i++) {
	        // j == 0; nw = lev(i - 1, j)
	        costs[0] = i;
	        int nw = i - 1;
	        for (int j = 1; j <= b.length(); j++) {
	            int cj = Math.min(1 + Math.min(costs[j], costs[j - 1]), a.charAt(i - 1) == b.charAt(j - 1) ? nw : nw + 1);
	            nw = costs[j];
	            costs[j] = cj;
	        }
	    }
	    return costs[b.length()];
	}
	
	public List<Match> matches() {
		return matches;
	}
}
