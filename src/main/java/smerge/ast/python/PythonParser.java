package smerge.ast.python;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class PythonParser {
	
	
	// Testing Method
	public static void main(String[] args) throws IOException {
				
		File base = new File("conflicts/test/test_base.py");
		PythonTree baseTree = parse(base);
		
		File local = new File("conflicts/test/test_local.py");
		PythonTree localTree = parse(local);
		
		File remote = new File("conflicts/test/test_remote.py");
		PythonTree remoteTree = parse(remote);
		
		System.out.println(baseTree);
		System.out.println(localTree);
		System.out.println(remoteTree);
		
	}
	
	// parses the given python file into a PythonTree
	public static PythonTree parse(File file) throws IOException {
		BufferedReader br = new BufferedReader(new FileReader(file));
		
		// holds onto current parents
		// maps indentation -> last node/line read with this indentation
		Map<Integer, PythonTree> parents = new HashMap<>();
		
		// keeps track of current whitespace
		String whitespace = "";
		
		// initialize root of tree
		PythonTree root = new PythonTree();
		parents.put(-1, root);
	    
		// build AST
		String line = br.readLine();
		while (line != null) {
			if (line.isEmpty()) {
				// keep track of whitespace
				whitespace += "\n";
			} else {
				int indentation = countIndents(line);
				PythonTree node = new PythonTree(indentation, line.trim());

				// set as last seen node with this indentation
				parents.put(indentation, node);
				
				// find parent of this node
				PythonTree parent = parents.get(indentation - 1);
				if (!whitespace.isEmpty()) {
					// preappend whitespace node
					PythonTree whitespaceNode = new PythonTree(0, whitespace);
					parent.children().add(whitespaceNode);
					whitespaceNode.setParent(parent);	
					whitespace = "";
				}
				parent.children().add(node);
				node.setParent(parent);	
			}
			
			line = br.readLine();
		}
		return root;
	}
	
	// counts indentation of the given line
	// currently only uses four spaces as an indentation
	private static int countIndents(String line) {
		int indentation = 0;
		while (line.startsWith("    ", indentation * 4)) {
			indentation += 1;
		}
		return indentation;
	}

}
