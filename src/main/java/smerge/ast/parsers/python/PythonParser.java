package smerge.ast.parsers.python;

import smerge.ast.AST;
import smerge.ast.parsers.Parser;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.Stack;


public class PythonParser implements Parser {
	public static final String[] opens = {"\"\"\"", "'''", "\"", "'", "(", "[", "{"};
	public static final String[] closes = {"\"\"\"", "'''", "\"", "'", ")", "]", "}"};	
		
	// main method used for quick testing
	public static void main(String[] args) throws IOException {
		
		PythonParser p = new PythonParser();
		
		
		File[] files = new File("scripts/test_results/keras_test_results/conflicts").listFiles();
	    
		for (File f : files) {
			System.out.println(f);
			p.parse(f.toString());
		}
		
		
	}
	
	// parses the given python file into a PythonTree
	public AST parse(String filename) throws IOException {
		BufferedReader br = new BufferedReader(new FileReader(new File(filename)));
		
		// holds onto current parents
		Stack<PythonNode> parentStack = new Stack<>();
		
		// initialize tree
		PythonNode root = new PythonNode();
		parentStack.push(root);
	    
		// convert all tokens into PythonNodes
		String token;
		
		while ((token = getNextToken(br)) != null) {
			
			int indentation = getIndentation(token);
			String content = token.trim();
			PythonNode.Type type = getType(content);

			PythonNode node = new PythonNode(indentation, content, type);

			// find parent of this node and add it as a child
			PythonNode parent = parentStack.peek();
			while (indentation <= parent.indentation) {
				parentStack.pop();
				parent = parentStack.peek();
			}
			parent.addChild(node);
			
			// next lines "should" be children
			if (content.endsWith(":")) {
				parentStack.push(node);
			}			
		}
		return new AST(root);
	}
	
	public String getNextToken(BufferedReader br) throws IOException {
		String token = br.readLine();
		if (token == null || token.trim().startsWith("#")) return token;
		
		int index = 0;
		Stack<String> subtokens = new Stack<>();
		
		outerloop:
		while (index < token.length()) {
			
			// append next line if needed
			
			
			String part = token.substring(index);
			
			// check for a closing
			if (!subtokens.isEmpty()) {
				String close = closing(subtokens.peek());
				if (part.startsWith(close)) {
					subtokens.pop();
					index += close.length();
					continue;
				}
			}
			
			// check for an opening if not in a string currently
			if (subtokens.isEmpty() || !isString(subtokens.peek())) {
				for (int i = 0; i < opens.length; i++) {
					if (part.startsWith(opens[i])) {
						subtokens.push(opens[i]);
						index += opens[i].length();
						continue outerloop;
					}
				}
			}
			
			index++;
			// add another line if needed
			if (index == token.length() && (token.trim().endsWith("\\") || !subtokens.isEmpty())) {
				String temp = br.readLine();
				if (temp != null) {
					token += "\n" + temp;
				}
			}
		}		
		return token;
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
	
	// determines the type of the node given the content
	private static PythonNode.Type getType(String lineContent) {
		if (lineContent.startsWith("def")) {
			return PythonNode.Type.METHOD;
		} else if (lineContent.startsWith("if")) {
		    return PythonNode.Type.IF_STATEMENT;
		} else if (lineContent.startsWith("while")) {
			return PythonNode.Type.WHILE_LOOP;
		} else if (lineContent.startsWith("for")) {
			return PythonNode.Type.FOR_LOOP;
		} else if (lineContent.startsWith("return")) {
			return PythonNode.Type.RETURN;
		} else if (lineContent.startsWith("import") || lineContent.startsWith("from")) {
			return PythonNode.Type.IMPORT;
		} else if (lineContent.startsWith("#")) {
			return PythonNode.Type.COMMENT;
		} else if (lineContent.startsWith("\"\"\"") && lineContent.endsWith("\"\"\"")) {
			return PythonNode.Type.BLOCK_COMMENT;
		} else if (lineContent.isEmpty()) {
			return PythonNode.Type.WHITESPACE;
		}
		return null;
	}
	
	private static String closing(String open) {
		return closes[Arrays.asList(opens).indexOf(open)];
	}
	
	private static boolean isString(String s) {
		return s.equals("\"\"\"") || s.equals("'''") || s.equals("\"") || s.equals("'");
	}
}
