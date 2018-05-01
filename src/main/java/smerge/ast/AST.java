package smerge.ast;

import java.util.ArrayList;
import java.util.List;

public class AST {
	
	private int id;
	
	protected AST parent;
	protected List<AST> children;
	
	public AST() {
		this.children = new ArrayList<>();
	}
	
	// used for matching
	public int getID() {
		return id;
	}
	
	// used for matching
	public void setID(int id) {
		this.id = id;
	}
	
	public List<AST> children() {
		return children;
	}
	
	public void setParent(AST parent) {
		this.parent = parent;
	}
	
	/* ignore this
	private void encode(Map<Integer, ArrayList<Integer>> encoding) {
		if (!children.isEmpty()) {
			ArrayList<Integer> childrenIDList = new ArrayList<>();
			for (ASTNode child : children) {
				childrenIDList.add(child.getID());
				encode(child, encoding);
			}
			encoding.put(current.getID(), childrenIDList);
		}
	} */
	
}
