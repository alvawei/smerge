package smerge;

import smerge.ast.AST;
import smerge.ast.ASTDiffer;
import smerge.ast.ASTMatcher;
import smerge.ast.actions.Action;
import smerge.ast.actions.ActionSet;
import smerge.ast.python.PythonParser;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;


/**
 * Runs Smerge
 */
public class Merger {
	
    
    /**
     * @param args [BASE, LOCAL, REMOTE, MERGED] files
     * @throws IOException 
     * @throws DiffException 
     */
    public static void main(String[] args) throws IOException {
    	if (args.length != 4) {
    		throw new RuntimeException("Expected arguments: $BASE, $LOCAL, $REMOTE, $MERGED");
    	}

        String base = args[0];
        String local = args[1];
        String remote = args[2];
        String merged = args[3];
        
        // have to figure out which parser to use somehow
        // will create Parser interface later
        // may be able to take in file name parameter as an additional git mergetool input
        
        System.out.println("Parsing base file...");
        AST baseTree = PythonParser.parse(new File(base));
        
        System.out.println("Parsing local file...");
        AST localTree = PythonParser.parse(new File(local));
        
        System.out.println("Parsing remote file...");
        AST remoteTree = PythonParser.parse(new File(remote));
        
        System.out.println("Generating tree diffs...");
        boolean success = true;
        try {
            ActionSet actions = new ASTDiffer(baseTree, localTree, remoteTree).diff();
            actions.apply();
            // write baseTree to merged
            System.out.println("Writing result to " + merged);
            String result = baseTree.toString();
            
            // write result -> merged
            PrintWriter out = new PrintWriter(merged);
            out.println(result);
            
        } catch (RuntimeException e) {
        	e.printStackTrace();
        	System.out.println("Failed to merge.");
        }

    }
}
