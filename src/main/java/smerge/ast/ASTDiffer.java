package smerge.ast;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;


public class ASTDiffer {
	
	private AST oldTree;
	private AST newTree;
  
	public ASTDiffer(AST oldTree, AST newTree) {
		this.oldTree = oldTree;
		this.newTree = newTree;
	}
	
	public void encodeDiff() {
		Map<Integer, ArrayList<Integer>> oldEncoding = oldTree.encode();
		Map<Integer, ArrayList<Integer>> newEncoding = newTree.encode();
		
		Set<Change> changes = new HashSet<>();
		
		// find deletions
		for (Integer id : oldEncoding.keySet()) {
			if (!newEncoding.containsKey(id)) {
				// deletion or relabel
			}
		}
		
		// find additions
		for (Integer id : newEncoding.keySet()) {
			if (!oldEncoding.containsKey(id)) {
				// addition or relabel
			}
		}
	}
	
}
