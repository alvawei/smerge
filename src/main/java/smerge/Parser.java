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

	public static ASTree[] parseFiles(Conflict conflict) throws FileNotFoundException {
		ASTree[] trees = new ASTree[3];
		
		trees[Conflict.BASE] = parse(conflict.getFile(Conflict.BASE));
		trees[Conflict.LOCAL] = parse(conflict.getFile(Conflict.LOCAL));
		trees[Conflict.REMOTE] = parse(conflict.getFile(Conflict.REMOTE));

		return trees;
	}
}