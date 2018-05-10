package smerge.ast.python;

import smerge.ast.AST;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Stack;


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

		
		File remote = new File("scripts/test_results/flask_test_results/conflicts/1___init___base.py");
		AST remoteTree = parse(remote);
		System.out.println(remoteTree);
		
	}
	
	// parses the given python file into a PythonTree
	public static AST parse(File file) throws IOException {
		BufferedReader br = new BufferedReader(new FileReader(file));
		
		// holds onto current parents
		// maps indentation -> last node/line read with this indentation
		Map<Integer, PythonNode> parents = new HashMap<>();
		
		// initialize tree
		PythonNode root = new PythonNode();
		parents.put(-4, root);
		AST tree = new AST(root);
	    
		// build AST
		String line = br.readLine();
		while (line != null) {
			if (line.endsWith("\\")) {
				line += "\n" + br.readLine();
				continue;
			}
			
			// read entire block comment
			if (line.contains("\"\"\"")) {
				int firstIndex = line.indexOf("\"\"\"");
				String s = line.substring(firstIndex + 3);
				while (!s.contains("\"\"\"")) {
					s += "\n" + br.readLine();
				}
				line = line.substring(0, firstIndex + 3) + s;
			}
			
			int indentation = getIndentation(line);
			String lineContent = line.trim();
			int type = getType(lineContent);
			
			
			
			
			PythonNode node = new PythonNode(indentation, lineContent + "\n", type);

			// set as last seen node with this indentation
			parents.put(indentation, node);
			
			// find parent of this node and add it as a child
			PythonNode parent = indentation > 0 ? parents.get(indentation - 4) : root;
			parent.addChild(node);
			
			line = br.readLine();
		}
		return tree;
	}
	
	private static int getType(String lineContent) {
		if (lineContent.startsWith("def")) {
			return PythonNode.METHOD;
		} else if (lineContent.startsWith("if")) {
		    return PythonNode.IF_STATEMENT;
		} else if (lineContent.startsWith("while")) {
			return PythonNode.WHILE_LOOP;
		} else if (lineContent.startsWith("for")) {
			return PythonNode.FOR_LOOP;
		} else if (lineContent.startsWith("return")) {
			return PythonNode.RETURN;
		} else if (lineContent.startsWith("import") || lineContent.startsWith("from")) {
			return PythonNode.IMPORT;
		} else if (lineContent.startsWith("#")) {
			return PythonNode.COMMENT;
		} else if (lineContent.startsWith("\"\"\"") && lineContent.endsWith("\"\"\"")) {
			return PythonNode.BLOCK_COMMENT;
		} else if (lineContent.isEmpty()) {
			return PythonNode.WHITESPACE;
		}
		return -1;
	}
	
	// returns the number of spaces at the beginning of line (tabs = 4 spaces)
	private static int getIndentation(String line) {
		int indentation = 0;
		boolean tab = false;
		while (line.startsWith(" ", indentation) ||
			   (tab = line.startsWith("\t", indentation))) {
			indentation += tab ? 4 : 1;
		}
		return indentation;
	}

}
