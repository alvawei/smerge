package smerge.ast.python;

import smerge.ast.AST;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;


public class PythonParser {
	
	
	// Testing Method
	public static void main(String[] args) throws IOException {
			
		/*
		File base = new File("conflicts/test/test_base.py");
		AST baseTree = parse(base);
		System.out.println(baseTree);
		
		File local = new File("conflicts/test/test_local.py");
		AST localTree = parse(local);
		System.out.println(localTree);
		*/

		
		File remote = new File("conflicts/test/test_remote.py");
		AST remoteTree = parse(remote);
		System.out.println(remoteTree);
		
	}
	
	// parses the given python file into a PythonTree
	public static AST parse(File file) throws IOException {
		BufferedReader br = new BufferedReader(new FileReader(file));
		
		// holds onto current parents
		// maps indentation -> last node/line read with this indentation
		Map<Integer, PythonNode> parents = new HashMap<>();
		
		// keeps track of current whitespace
		String whitespace = "";
		
		// initialize tree
		PythonNode root = new PythonNode();
		parents.put(-1, root);
		AST tree = new AST(root);
	    
		// build AST
		String line = br.readLine();
		while (line != null) {
			if (line.startsWith("import") || line.startsWith("from")) {
				tree.imports().add(line.trim());
			} else if (line.isEmpty()) {
				whitespace += "\n";
			} else {
				int indentation = countIndents(line);
				PythonNode node = new PythonNode(indentation, line.trim() + "\n");

				// set as last seen node with this indentation
				parents.put(indentation, node);
				
				// find parent of this node
				PythonNode parent = parents.get(indentation - 1);
				
				if (!whitespace.isEmpty()) {
					// preappend whitespace node
					PythonNode whitespaceNode = new PythonNode(0, whitespace);
					parent.children().add(whitespaceNode);
					whitespaceNode.setParent(parent);	
					whitespace = "";
				}
				
				// insert node into tree
				parent.children().add(node);
				node.setParent(parent);	
			}
			line = br.readLine();
		}
		return tree;
	}
	
	// counts indentation of the given line
	// currently only uses four spaces as an indentation
	private static int countIndents(String line) {
		int indentation = 0;
		while (line.startsWith("    ", indentation * 4) ||
			   line.startsWith("\t", indentation)) {
			indentation += 1;
		}
		return indentation;
	}

}
