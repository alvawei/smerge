package smerge;

import java.io.FileNotFoundException;
import com.github.javaparser.ast.Node;

public class ASTree {
	
	private Node root;
	
	public ASTree(Node root) throws FileNotFoundException {
		this.root = root;
	}
	
	
}