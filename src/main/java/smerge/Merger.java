package smerge;

import smerge.actions.ActionSet;
import smerge.ast.AST;
import smerge.ast.ActionMerger;
import smerge.ast.Differ;
import smerge.parsers.Parser;

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
        
        // PARSING
        // TODO: get the correct parser (pass in filename for file extension/type?), change "null"
        Parser parser = Parser.getInstance(null);
        
        System.out.println("Parsing base file...");
        AST baseTree = parser.parse(base);
        
        System.out.println("Parsing local file...");
        AST localTree = parser.parse(local);
        
        System.out.println("Parsing remote file...");
        AST remoteTree = parser.parse(remote);
        
        
        // TREE DIFFING
        System.out.println("Generating tree diffs...");
        Differ differ = new Differ(baseTree, localTree, remoteTree);
        ActionSet localActions = new ActionSet();
        ActionSet remoteActions = new ActionSet();
        differ.diff(localActions, remoteActions);
           
        
        // MERGING
        System.out.println("Merging changes...");
        ActionMerger merger = new ActionMerger(localActions, remoteActions);
        merger.merge();
        
        
        // OUTPUT
        System.out.println("Writing result to " + merged);
        String result = baseTree.toString();
        PrintWriter out = new PrintWriter(merged);
        out.println(result);
        out.close();
        
        
        // CONFLICT COUNTS
        System.out.print("Merge conflicts resolved: ");
        System.out.println(merger.solvedConflicts + "/" + merger.totalConflicts);
    }
}
