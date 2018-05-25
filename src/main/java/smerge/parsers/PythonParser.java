package smerge.parsers;

import smerge.ast.AST;
import smerge.ast.ASTNode;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.Stack;

/**
 * This class is responsible for parsing Python 3 files (note it may work with Python 2, 
 * but it is not guaranteed).
 * See the Parser abstract class.
 * 
 * @author Jediah Conachan
 */
public class PythonParser extends Parser {
	
	// these are used to complete tokens
	public static final String[] opens = {"\"\"\"", "'''", "\"", "'", "(", "[", "{"};
	public static final String[] closes = {"\"\"\"", "'''", "\"", "'", ")", "]", "}"};	
	
	/**
	 * Parses the given file into an AST
	 * @param filename - the filename of the file to parse
	 * @return an AST representation of the file's source code
	 * @throws IOException if there is an error reading the file
	 */
	public AST parse(String filename) throws IOException {
		BufferedReader br = new BufferedReader(new FileReader(new File(filename)));
		
		// holds onto current parents
		Stack<ASTNode> parentStack = new Stack<>();
		
		// initialize tree
		ASTNode root = new ASTNode();
		parentStack.push(root);
	    
		// convert all tokens into ASTNodes
		String token;
		int id = -1;
		
		while ((token = getNextToken(br)) != null) {			
			int indentation = getIndentation(token);
			String content = token.trim();
			ASTNode.Type type = getType(content);

			ASTNode node = new ASTNode(type, content, indentation);
			node.setID(id--);
			
			if (type == ASTNode.Type.WHITESPACE) {
				root.addChild(node);
				continue;
			}
			// find parent of this node and add it as a child
			ASTNode parent = parentStack.peek();
			while (indentation <= parent.getIndentation()){
				parentStack.pop();
				parent = parentStack.peek();
			}
			parent.addChild(node);
			
			// next lines "should" be children
			if (content.endsWith(":")) {
				parentStack.push(node);
			}			
		}
		return new AST(root, this);
	}
	
	/**
	 * Unparses the given AST back into source code
	 * @param tree - the AST to be unparsed
	 * @return a String representation of source code
	 */
	public String unparse(AST tree) {
		StringBuilder sb = new StringBuilder();
		for (ASTNode child : tree.getRoot().children()) {
			unparse(child, sb);
		}
		
		return sb.toString();
	}
	
	// recursively unparse a subtree
	private void unparse(ASTNode node, StringBuilder sb) {
		if (!node.isPlaceHolder()) {
			sb.append(indent(node.getIndentation()));
			sb.append(node.getContent() + "\n");
			for (ASTNode child : node.children()) {
				unparse(child, sb);
			}
		}
	}
	
	// read the next token
	private String getNextToken(BufferedReader br) throws IOException {
		String token = br.readLine();
		if (token == null || token.trim().startsWith("#")) return token;
		
		int index = 0;
		Stack<String> subtokens = new Stack<>();
		
		outerloop:
		while (index < token.length()) {
			String part = token.substring(index);
			
			// check for a closing character
			if (!subtokens.isEmpty()) {
				String close = closing(subtokens.peek());
				if (part.startsWith(close)) {
					subtokens.pop();
					index += close.length();
					continue;
				}
			}
			
			// check for an opening character if not in a string currently
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
		int index = 0;
		boolean tab = false;
		while (line.startsWith(" ", index) ||
			   (tab = line.startsWith("\t", index))) {
			indentation += tab ? 4 : 1;
			index++;
		}
		return indentation;
	}
	
	// determines the type of the node given the content
	private static ASTNode.Type getType(String lineContent) {
		if (lineContent.startsWith("def")) {
			return ASTNode.Type.METHOD;
		} else if (lineContent.startsWith("if")) {
		    return ASTNode.Type.IF_STATEMENT;
		} else if (lineContent.startsWith("while")) {
			return ASTNode.Type.WHILE_LOOP;
		} else if (lineContent.startsWith("for")) {
			return ASTNode.Type.FOR_LOOP;
		} else if (lineContent.startsWith("return")) {
			return ASTNode.Type.RETURN;
		} else if (lineContent.startsWith("import") || lineContent.startsWith("from")) {
			return ASTNode.Type.IMPORT;
		} else if (lineContent.startsWith("#")) {
			return ASTNode.Type.COMMENT;
		} else if (lineContent.startsWith("\"\"\"") && lineContent.endsWith("\"\"\"")) {
			return ASTNode.Type.BLOCK_COMMENT;
		} else if (lineContent.isEmpty()) {
			return ASTNode.Type.WHITESPACE;
		} else if (lineContent.contains(" = ")) {
			return ASTNode.Type.ASSIGNMENT;
		}
		return null;
	}
	
	// returns the closing character that matches the given opening character
	// example: "(" -> ")"
	private static String closing(String open) {
		return closes[Arrays.asList(opens).indexOf(open)];
	}
	
	// returns if the given opening/closing character is a string type
	private static boolean isString(String s) {
		return s.equals("\"\"\"") || s.equals("'''") || s.equals("\"") || s.equals("'");
	}
}
