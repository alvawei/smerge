package smerge;

import java.io.IOException;
import java.io.PrintWriter;

import smerge.ast.AST;
import smerge.ast.Differ;
import smerge.ast.MergeException;
import smerge.ast.actions.ActionSet;
import smerge.ast.parsers.python.PythonParser;

public class Test {
	
	// i just run this main method for easy testing

	public static void main(String[] args) throws IOException, MergeException {
		String base = "conflicts/test/test_base.py"; // args[0];
        String local = "conflicts/test/test_local.py"; // args[1];
        String remote = "conflicts/test/test_remote.py"; // args[2];
        String merged = "conflicts/test/test_merged.py"; // args[3];
        
        // have to figure out which parser to use somehow
        // may be able to take it in as an additional git mergetool input
        System.out.println("Parsing files...");
        PythonParser p = new PythonParser();
        AST baseTree = p.parse(base);
        AST localTree = p.parse(local);
        AST remoteTree = p.parse(remote);
                
        System.out.println(baseTree);
        
        System.out.println();
        
        System.out.println(localTree);
        
        System.out.println();
        
        System.out.println(remoteTree);
        
        System.out.println("Matching trees...");
        Differ differ = new Differ(baseTree, localTree, remoteTree);
        System.out.println(baseTree.debugTree());
        System.out.println(localTree.debugTree());
        System.out.println(remoteTree.debugTree());
                       
        System.out.println("Generating tree diffs...");
        try {
            ActionSet actions = differ.diff(baseTree, localTree, remoteTree);

        	System.out.println(actions);

        	System.out.println("Merging changes...");
            actions.apply();
            
            System.out.println(baseTree);
            System.out.println(baseTree.debugTree());
            
            // write baseTree to merged
            System.out.println("Writing result to " + merged);
            String result = baseTree.toString();
            
            // write result -> merged
            PrintWriter out = new PrintWriter(merged);
            out.println(result);
            out.close();
            
        } catch (RuntimeException e) {
        	e.printStackTrace();
        	System.out.println("Failed to merge.");
        }
	}

}
