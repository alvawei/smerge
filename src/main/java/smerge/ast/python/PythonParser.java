package smerge.ast.python;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class PythonParser {
	
	public static void main(String[] args) throws IOException {
		File base = new File("test_base.py");
		PythonTree baseTree = parse(base);
		
		File local = new File("test_local.py");
		PythonTree localTree = parse(local);
		
		File remote = new File("test_remote.py");
		PythonTree remoteTree = parse(remote);
		
		System.out.println(baseTree);
		System.out.println(localTree);
		System.out.println(remoteTree);
		
	}
	
	public static PythonTree parse(File file) throws IOException {
		BufferedReader br = new BufferedReader(new FileReader(file));
		
		Map<Integer, PythonNode> parents = new HashMap<>();
		PythonNode root = new PythonNode();
		parents.put(-1, root);
		
		PythonNode prev = null;
		// build AST
	    int lineNum = 0;
		String line;
		while ((line = br.readLine()) != null) {
			if (!line.isEmpty()) {
				int indentation = countIndents(line);
				PythonNode node = new PythonNode(lineNum, indentation, line.trim());
				parents.put(indentation, node);
				
				if (indentation == 0) {
					node.setParent(root);
				} else {
					node.setParent(parents.get(indentation - 1));
				}

				prev = node;
			}
			lineNum++;
		}
		return new PythonTree(root);
	}
	
	private static int countIndents(String line) {
		int indentation = 0;
		while (line.startsWith("    ", indentation * 4)) {
			indentation += 1;
		}		
		return indentation;
	}

}
