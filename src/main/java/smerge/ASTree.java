package smerge;

import java.io.FileNotFoundException;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.utils.Pair;


public class ASTree {
	
	private Node root;
	
	public ASTree(String file) throws FileNotFoundException {
		this.root = JavaParser.parse(new File(file));
	}
	
	
}