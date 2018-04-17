package smerge;

import java.io.FileNotFoundException;
import com.github.javaparser.ast.Node;





public class ASTree {
	
	private Node root;
	
	public ASTree(String file) throws FileNotFoundException {
		this.root = Parser.parse(file);
	}
	
	
}