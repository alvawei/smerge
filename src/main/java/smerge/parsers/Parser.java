package smerge.parsers;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.Scanner;

import smerge.ast.AST;

public abstract class Parser {
	
	public static Parser getInstance(String filename) {
		// if filename.endsWith(".py")?
		return new PythonParser();
	}
	
	public abstract AST parse(String filename) throws IOException;
	public abstract String unparse(AST tree);
	
	
	// returns a string with the given number of spaces
	public String indent(int numSpaces) {
		String s = "";
		for (int i = 0; i < numSpaces; i++) {
			s += " ";
		}
		return s;
	}
}
