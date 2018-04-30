package smerge.unparser;

import java.io.IOException;
import java.util.List;

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
		System.out.println(baseTree.toTreeString());

		System.out.println(unparse(baseTree));
		

	}
	
	public static String unparse(ITree root) {
		// TYPES
		// 55 = class
		// 31 = method?
		
		String result = "";
		
		for (ITree node : root.getChildren()) {
			result = unparse(node, result, 0);
		}
		
		return result;
	}
	
	public static String unparse(ITree next, String result, int indentation) {
		List<ITree> children = next.getChildren();
		switch (next.getType()) {
			case 55: // class
				String access = children.remove(0).getLabel();
				String name = children.remove(0).getLabel();
				result += access + " class " + name + " {\n";
				for (ITree node : children) {
					result = unparse(node, result, indentation + 1);
				}
				result += "}\n";
				break;
						
			case 31: // method
				boolean firstParameter = true;
				result += indent(indentation);
				for (ITree node : children) {
					
					if (node.getType() == 83) { // public/static options
						result += node.getLabel() + " ";
					} else if (node.getType() == 42) { // method name
						result += node.getLabel() + "(";
					} else if (node.getType() == 44) { // parameter
						// check if comma is needed
						if (firstParameter) {
							firstParameter = false;
						} else {
							result += ", ";
						}
						result = unparse(node, result, indentation);

					} else if (node.getType() == 8) { // close method header
						result += ") {\n";
					}
					unparse(node, result, indentation + 1);
				}
				result += indent(indentation) + "}\n";
				break;
				
			case 44: // method parameters?
				result += children.get(0) + " " + children.get(1);
				break;
				
			case 59: // variable declaration/assignment?
				break;
				
			default: 
				result += next.getLabel() + " ";
				break;
		}
		return result;
	}
	
	private static String indent(int indentation) {
		String res = "";
		for (int i = 0; i < indentation; i++) {
			res += "    ";
		}
		return res;
	}

}
