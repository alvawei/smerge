package smerge.unparser;

import java.io.IOException;

import com.github.gumtreediff.client.Run;
import com.github.gumtreediff.gen.Generators;
import com.github.gumtreediff.tree.ITree;

/*
 * Unparses a GumTree ITree back into Java code
 */

public class JavaUnparser {
	
	// for testing
	public static void main(String[] args) throws UnsupportedOperationException, IOException {
		String base = "conflicts/test/Simple_Base.java";

		// generate tree
		Run.initGenerators();
		ITree baseTree = Generators.getInstance().getTree(base).getRoot();
		
		// unparse
		System.out.println(unparse(baseTree));
		
		System.out.println(baseTree.toTreeString());

	}
	
	public static String unparse(ITree root) {
		String result = "";
		
		for (ITree node : root.preOrder()) {
			result += node.getLabel() + node.getType() + "\n";
			
			
			
		}
		
		return result;
	}

}
