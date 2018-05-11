package smerge.ast.python;

import smerge.ast.AST;
import smerge.ast.ASTDiffer;
import smerge.ast.ASTMatcher;
import smerge.ast.actions.ActionSet;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Map;
import java.util.Stack;


public class PythonParser {
	
	
	// Testing Method
	public static void main(String[] args) throws IOException {
		// String file = "scripts/test_results/keras_test_results/conflicts/35_setup_base.py";
		String file = "scripts/test_results/flask_test_results/conflicts/1___init___base.py";
		AST tree = parse(new File(file));
		System.out.println(tree);
			
		
		/*File base = new File("scripts/test_results/flask_test_results/conflicts/1___init___base.py");		
		File local = new File("scripts/test_results/flask_test_results/conflicts/1___init___local.py");
		File remote = new File("scripts/test_results/flask_test_results/conflicts/1___init___remote.py");
				

		
        System.out.println("Parsing files...");
        AST baseTree = PythonParser.parse(base);
        AST localTree = PythonParser.parse(local);
        AST remoteTree = PythonParser.parse(remote);
        
        ASTDiffer diff = new ASTDiffer(baseTree, localTree, remoteTree);

        System.out.println(baseTree.debugTree());
        
        System.out.println();
        
        System.out.println(localTree.debugTree());
        
        
        System.out.println();
        System.out.println(remoteTree.debugTree());
               

        
        
        System.out.println("Generating tree diffs...");
        try {
            ActionSet actions = diff.diff();
            actions.apply();
            
            System.out.println(baseTree);
            System.out.println(baseTree.debugTree());
            
            // write baseTree to merged
            //System.out.println("Writing result to " + merged);
            String result = baseTree.toString();
            
            // write result -> merged
            //PrintWriter out = new PrintWriter(merged);
            //out.println(result);
            
        } catch (RuntimeException e) {
        	e.printStackTrace();
        	System.out.println("Failed to merge.");
        } */
		
	}
	
	// parses the given python file into a PythonTree
	public static AST parse(File file) throws IOException {
		BufferedReader br = new BufferedReader(new FileReader(file));
		
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
		while (line.endsWith("\\") || line.endsWith(",")) {
			line += "\n" + br.readLine();
		}
		
		// (, {, [, """, ''', etc.
		Stack<String> unclosedTokens = new Stack<>();
		String closing = null;
		boolean inString = false;
		int index = 0;
		
		while (index < line.length()) {
			String part = line.substring(index);
			if (closing != null) {
				// find closing character
				index += closing.length();
				if (part.startsWith(closing)) {
					closing = null;
					continue;
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
