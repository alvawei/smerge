package smerge;

import java.io.File;
import java.io.FileNotFoundException;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.utils.Pair;

public class Parser {
	
	public static Node parse(String file) throws FileNotFoundException {
		return JavaParser.parse(new File(file));
	}
}