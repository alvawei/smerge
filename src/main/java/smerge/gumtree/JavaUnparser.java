package smerge.gumtree;

import java.io.IOException;
import java.util.List;

import org.eclipse.jdt.core.dom.CompilationUnit;

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
		
		StringBuilder sb = new StringBuilder();
		
		for (ITree node : root.getChildren()) {
			unparse(node, sb, 0);
		}
		
		return sb.toString();
	}
	
	public static void unparse(ITree next, StringBuilder sb, int indentation) {
		List<ITree> children = next.getChildren();
		switch (next.getType()) {
			case 55: // class
				String access = children.remove(0).getLabel();
				String name = children.remove(0).getLabel();
				sb.append(access + " class " + name + " {\n");
				for (ITree node : children) {
					unparse(node, sb, indentation + 1);
				}
				sb.append("}\n");
				break;
						
			case 31: // method declaration
				boolean firstParameter = true;
				sb.append(indent(indentation));
				for (ITree node : children) {
					
					if (node.getType() == 83) { // public/static options
						sb.append(node.getLabel() + " ");
					} else if (node.getType() == 42) { // method name
						sb.append(node.getLabel() + "(");
					} else if (node.getType() == 44) { // parameter
						// check if comma is needed
						if (firstParameter) {
							firstParameter = false;
						} else {
							sb.append(", ");
						}
						unparse(node, sb, indentation);
					}
				}
				sb.append(") ");
				unparse(children.get(children.size() - 1), sb, indentation);
				break;
				
			case 8: // method body
				sb.append("{\n");
				for (ITree node : children) {
					unparse(node, sb, indentation + 1);
				}
				sb.append(indent(indentation) + "}\n");
				
				
			case 44: // method parameters?
				sb.append(children.get(0).getLabel() + " " + children.get(1).getLabel());
				break;
				
			case 60: // variable declaration?
				sb.append(indent(indentation));
				for (ITree node : children) {
					unparse(node, sb, indentation);
				}
				sb.append(";\n");
				break;
			
			case 59: // variable assignment?
				sb.append(children.get(0).getLabel() + " = " + children.get(1).getLabel());
				break;
				
			default: 
				sb.append(next.getLabel() + " ");
				break;
		}
	}
	
	private static String indent(int indentation) {
		String res = "";
		for (int i = 0; i < indentation; i++) {
			res += "    ";
		}
		return res;
	}

}