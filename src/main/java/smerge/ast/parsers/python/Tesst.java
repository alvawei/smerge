package smerge.ast.parsers.python;

import java.io.File;
import java.io.IOException;
import java.util.Scanner;

import smerge.ast.AST;

public class Tesst {
	public static void main(String[] args) throws IOException {
		PythonParser p = new PythonParser();
		
		String badFile = "scripts/test_results/flask_test_results/conflicts/12_test_cli_local.py";
		AST tree = p.parse(badFile);
		System.out.println(tree);
		
		
		
		
		/*
		File[] files = new File("scripts/test_results/flask_test_results/conflicts").listFiles();
	    
		for (File f : files) {
			System.out.println(f);
			p.parse(f.toString());
		}
		*/
	}

}
