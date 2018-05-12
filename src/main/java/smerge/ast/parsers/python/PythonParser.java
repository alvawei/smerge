package smerge.ast.parsers.python;

import smerge.ast.AST;
import smerge.ast.parsers.Parser;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.Stack;


public class PythonParser implements Parser {
		
	// main method used for quick testing
	public static void main(String[] args) throws IOException {
		String filename = "scripts/test_results/keras_test_results/conflicts/35_setup_base.py";
		// String filename = "scripts/test_results/flask_test_results/conflicts/1___init___base.py";
		
		Parser parser = new PythonParser();
		AST tree = parser.parse(filename);
		System.out.println(tree);
		
	}
	
	// parses the given python file into a PythonTree
	public AST parse(String filename) throws IOException {
		BufferedReader br = new BufferedReader(new FileReader(new File(filename)));
		
		// holds onto current parents
		// maps indentation -> last node/line read with this indentation
		// Map<Integer, PythonNode> parents = new HashMap<>();
		Stack<PythonNode> parentStack = new Stack<>();
		
		// initialize tree
		PythonNode root = new PythonNode();
		// parents.put(-4, root);
		parentStack.push(root);
		AST tree = new AST(root);
	    
		// build AST
		String line = br.readLine();
		while (line != null) {
			
			line = ensureEnclosed(line, br);

			
			int indentation = getIndentation(line);
			String lineContent = line.trim();
			int type = getType(lineContent);

			PythonNode node = new PythonNode(indentation, lineContent + "\n", type);

			// set as last seen node with this indentation
			//parents.put(indentation, node);
	
			
			// find parent of this node and add it as a child
			PythonNode parent = parentStack.peek();
			while (indentation <= parent.indentation) {
				parentStack.pop();
				parent = parentStack.peek();
			}
			parent.addChild(node);
			
			if (lineContent.endsWith(":")) {
				parentStack.push(node);
			}
			
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
	
	// reads more lines if it is a multilined comment, list, etc...
	private static String ensureEnclosed(String line, BufferedReader br) throws IOException {
		while (line.endsWith("\\")) {
			line += "\n" + br.readLine();
		}
		
		// (, {, [, """, ''', etc.
		String closing = null;
		int index = 0;
		
		while (index < line.length()) {
			String part = line.substring(index);
			if (closing != null) {
				// find closing character
				index += closing.length();
				if (part.startsWith(closing)) {
					closing = null;
				} else if (index >= line.length()) {
					// have to read next line
					line += "\n" + br.readLine();
				}
			} else {
				if (part.startsWith("\"\"\"")) {
					closing = "\"\"\"";
				} else if (part.startsWith("\'\'\'")) {
					closing = "\'\'\'";
				} else if (part.startsWith("\"")) {
					closing = "\"";
				} else if (part.startsWith("'")) {
					closing = "'";
				} else if (part.startsWith("(")) {
					closing = ")";
				} else if (part.startsWith("{")) {
					closing = "}";
				} else if (part.startsWith("[")) {
					closing = "]";
				}
				index += (closing == null ? 1 : closing.length() - 1);
				if (closing != null && index >= line.length()) {
					line += "\n" + br.readLine();
				}
			}
			
			
		}
		
		return line;
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
