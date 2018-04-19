package smerge;

import java.io.File;
import java.io.FileNotFoundException;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.utils.Pair;

public class Parser {
	public static ASTree parse(File file) throws FileNotFoundException {
		Node root = JavaParser.parse(file);
		return new ASTree(root);
	}
}