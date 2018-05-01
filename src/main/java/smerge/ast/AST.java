package smerge.ast;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

public class AST {
	
	private ASTNode root;
	private int id;
	
	public AST() {
		this(null);
	}
	
	public AST(ASTNode root) {
		this.root = root;
	}
	
	public int getID() {
		return id;
	}
	
	public void setID(int id) {
		this.id = id;
	}
	
	// create an encoding of the tree
	public Map<Integer, ArrayList<Integer>> encode() {
		Map<Integer, ArrayList<Integer>> encoding = new HashMap<>();
		encode(root, encoding);
		return encoding;
	}
	
	// recursively encode the tree
	private void encode(ASTNode current, Map<Integer, ArrayList<Integer>> encoding) {
		if (!current.getChildren().isEmpty()) {
			ArrayList<Integer> childrenIDList = new ArrayList<>();
			for (ASTNode child : current.getChildren()) {
				childrenIDList.add(child.getID());
				encode(child, encoding);
			}
			encoding.put(current.getID(), childrenIDList);
		}
	}
	
}
