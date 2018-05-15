package smerge;

import smerge.ast.AST;
import smerge.ast.Differ;
import smerge.ast.MergeException;
import smerge.ast.actions.ActionSet;
import smerge.ast.parsers.Parser;

import java.io.IOException;
import java.io.PrintWriter;


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
        try {
            ActionSet actions = Differ.diff(baseTree, localTree, remoteTree);
            actions.apply();
            // write baseTree to merged
            System.out.println("Writing result to " + merged);
            String result = baseTree.unparse();
            
            // write result -> merged
            PrintWriter out = new PrintWriter(merged);
            out.println(result);
            out.close();
            
        } catch (MergeException e) {
        	e.printStackTrace();
        	System.out.println("Failed to merge.");
        }

    }
}
