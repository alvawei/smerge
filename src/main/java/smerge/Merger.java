package smerge;

import smerge.ast.AST;
import smerge.ast.Differ;
import smerge.ast.actions.ActionSet;
import smerge.ast.parsers.Parser;

import java.io.IOException;
import java.io.PrintWriter;


/**
 * Runs Smerge
 */
public class Merger {
	
	public static int totalConflicts = 0;
	public static int solvedConflicts = 0;
	
    
    /**
     * @param args [BASE, LOCAL, REMOTE, MERGED] files
     * @throws IOException 
     * @throws MergeException 
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
        Differ differ = new Differ(baseTree, localTree, remoteTree);
        
        System.out.println("Merging changes...");
        ActionSet actions = differ.diff();
        actions.apply();
        
        System.out.println("Writing result to " + merged);
        String result = baseTree.toString();
        
        // write result -> merged
        PrintWriter out = new PrintWriter(merged);
        out.println(result);
        out.close();
        
        System.out.println("Merge conflicts resolved: " + solvedConflicts + "/" + totalConflicts);
    }
}
