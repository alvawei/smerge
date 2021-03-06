package smerge.diff;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import smerge.ast.AST;
import smerge.ast.ASTNode;

/**
 * A Matcher object matches nodes between the given base, local, and remote trees.
 * 
 * @author Alva Wei, Jediah Conachan
 */
public class Matcher {
	
	// smaller similarity = good
	private static final double SIM_THRESHOLD = 0.2;

		
	private List<Match> matches;
	private int nextID; // the next id to be given to a new matching

	/**
	 * Constructs a new Matcher object and produces a list of matched nodes.
	 * 
	 * @param baseTree
	 * @param localTree
	 * @param remoteTree
	 */
	public Matcher(AST baseTree, AST localTree, AST remoteTree) {	
		matches = new ArrayList<>();
		
		labelBaseTree(baseTree);
		match(baseTree, localTree, true);
		match(baseTree, remoteTree, false);
	}
	
	/**
	 * Returns a listing of the matched nodes
	 * @return list of Match objects
	 */
	public List<Match> matches() {
		return matches;
	}
	
	/**
	 * Matches nodes between two trees, base and edit (which is either local or remote)
	 * 
	 * @param baseTree
	 * @param editTree
	 * @param isLocal - true iff editTree == localTree, false iff editTree == remoteTree
	 */
	private void match(AST baseTree, AST editTree, boolean isLocal) {
		Set<Integer> matchedIDs = new HashSet<Integer>();
		matches.get(0).setEditNode(editTree.getRoot(), isLocal);
		matchedIDs.add(0);
		
		// compare each node in the baseTree to each node in editTree
		for (ASTNode edit : editTree) {
			if (edit.getID() == 0) continue; // skip root
			double minSimilarity = 1.0;
			ASTNode bestMatch = null;
			for (ASTNode base : baseTree) {
				
				// can't be matched, skip
				if (matchedIDs.contains(base.getID()) || base.getType() != edit.getType()) 
					continue;
				
				if (base.getType() == ASTNode.Type.WHITESPACE) {
					int id = base.getID();
					matches.get(id).setEditNode(edit, isLocal);
					matchedIDs.add(id);
					break;
				}
				
				if (base.isLeafNode() && compareLeafNodes(base, edit) < minSimilarity) {
					minSimilarity = compareLeafNodes(base, edit);
					bestMatch = base;
				}
				
				if (!base.isLeafNode() && compareInnerNodes(base, edit) < minSimilarity) {
					minSimilarity = compareInnerNodes(base, edit);
					bestMatch = base;
				}
				
				/*if ((base.getType() == ASTNode.Type.WHITESPACE) || 
						(base.isLeafNode() && compareLeafNodes(base, edit)) ||
						(!base.isLeafNode() && compareInnerNodes(base, edit))) {
					// it's a match
					int id = base.getID();
					matches.get(id).setEditNode(edit, isLocal);
					matchedIDs.add(id);
					break;
				}*/	
				
			}
			if (minSimilarity <= SIM_THRESHOLD) {
				int id = bestMatch.getID();
				matches.get(id).setEditNode(edit, isLocal);
				matchedIDs.add(id);
			} else if (edit.getID() < 0) {
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
	private double compareLeafNodes(ASTNode n1, ASTNode n2) {
		return (double) distance(n1.getContent(), n2.getContent()) / Math.max(n1.getContent().length(), n2.getContent().length());
	}
	
	// return true iff these non-leaf nodes should be matched
	// in the future change to comparing nodes?
	private double compareInnerNodes(ASTNode n1, ASTNode n2) {
		return (double) distance(n1.getContent(), n2.getContent()) / Math.max(n1.getContent().length(), n2.getContent().length());
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
}
