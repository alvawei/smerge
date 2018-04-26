package smerge;

import java.io.File;
import java.io.FileNotFoundException;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.ImportDeclaration;
import com.github.javaparser.ast.Node;
import com.github.javaparser.utils.Pair;

import com.github.gumtreediff.*;
import com.github.gumtreediff.actions.ActionGenerator;
import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.client.Run;
import com.github.gumtreediff.gen.Generators;
import com.github.gumtreediff.matchers.Matcher;
import com.github.gumtreediff.matchers.Matchers;
import com.github.gumtreediff.tree.ITree;

import java.util.List;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;


public class Parser {
	
	public static void main(String[] args) throws UnsupportedOperationException, IOException {
		Run.initGenerators();
		String file1 = "TestBase.java";
		String file2 = "TestLocal.java";
		ITree src = Generators.getInstance().getTree(file1).getRoot();
		ITree dst = Generators.getInstance().getTree(file2).getRoot();
		
		System.out.println(src.toTreeString());
		System.out.println(dst.toTreeString());
		Matcher m = Matchers.getInstance().getMatcher(src, dst); // retrieve the default matcher
		m.match();
		ActionGenerator g = new ActionGenerator(src, dst, m.getMappings());
		g.generate();
		List<Action> actions = g.getActions(); // return the actions
		
		for (Action a : actions) {
			System.out.println(a.toString());
		}
	}
	
	public static ASTree parse(File file) throws FileNotFoundException {
		Node root = JavaParser.parse(file);
		return new ASTree(root);
	}
}