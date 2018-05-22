package smerge;

import java.io.IOException;
import java.io.PrintWriter;

import smerge.ast.AST;
import smerge.ast.Differ;
import smerge.ast.actions.ActionSet;
import smerge.ast.parsers.Parser;

public class Test {
	
	// i just run this main method for easy testing

	public static void main(String[] args) throws IOException {
		/*
		String base = "conflicts/test/test_base.py"; // args[0];
        String local = "conflicts/test/test_local.py"; // args[1];
        String remote = "conflicts/test/test_remote.py"; // args[2];
        String merged = "conflicts/test/test_merged.py"; // args[3];
        */
		
		String base = "scripts/test_results/keras_test_results/conflicts/1_image_test_base.py";
		String local = "scripts/test_results/keras_test_results/conflicts/1_image_test_local.py";
		String remote = "scripts/test_results/keras_test_results/conflicts/1_image_test_remote.py";
		String merged = "tmp/temp_out.py";
        
        // get the correct parser (pass in filename for file extension/type?)
        Parser parser = Parser.getInstance(null);
        
        
        // parse files into ASTs
        System.out.println("Parsing base file...");
        AST baseTree = parser.parse(base);
        
        System.out.println("Parsing local file...");
        AST localTree = parser.parse(local);
        
        System.out.println("Parsing remote file...");
        AST remoteTree = parser.parse(remote);
        

        
        // merge trees
        System.out.println("Generating tree diffs...");
        Differ differ = new Differ(baseTree, localTree, remoteTree);
        
        System.out.println(baseTree.debugTree());
        System.out.println(localTree.debugTree());
        System.out.println(remoteTree.debugTree());
        
        System.out.println("Merging changes...");
        ActionSet actions = differ.diff();
        System.out.println(actions);
        actions.apply();
        
        System.out.println(baseTree.debugTree());
        System.out.println("Writing result to " + merged);
        String result = baseTree.toString();
        
        // write result -> merged
        PrintWriter out = new PrintWriter(merged);
        out.println(result);
        out.close();
        
        System.out.print("Merge conflicts resolved: ");
        System.out.println(Merger.solvedConflicts + "/" + Merger.totalConflicts);
	}

}
