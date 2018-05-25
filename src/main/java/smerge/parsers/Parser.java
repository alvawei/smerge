package smerge.parsers;

import java.io.IOException;

import smerge.ast.AST;


/**
 * This class acts as an interface for all Parser classes (see PythonParser), and as
 * an abstract class for helper methods.
 * 
 * @author Jediah Conachan
 */

public abstract class Parser {
	
	/**
	 * @param filename
	 * @return the correct parser
	 */
	public static Parser getInstance(String filename) {
		if (filename.endsWith(".py")) return new PythonParser();
		throw new IllegalArgumentException("Parsing is not supported for this file type: " + filename);
	}
	
	/**
	 * Parses the given file into an AST
	 * @param filename - the filename of the file to parse
	 * @return an AST representation of the file's source code
	 * @throws IOException if there is an error reading the file
	 */
	public abstract AST parse(String filename) throws IOException;
	
	/**
	 * Unparses the given AST back into source code
	 * @param tree - the AST to be unparsed
	 * @return a String representation of source code
	 */
	public abstract String unparse(AST tree);
	
	
	/**
	 * Helper method.
	 * @param numSpaces - number of spaces
	 * @return a String with the given number of spaces
	 */
	public String indent(int numSpaces) {
		String s = "";
		for (int i = 0; i < numSpaces; i++) {
			s += " ";
		}
		return s;
	}
}
