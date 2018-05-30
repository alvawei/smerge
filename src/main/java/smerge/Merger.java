package smerge;

import smerge.actions.ActionMerger;
import smerge.actions.ActionSet;
import smerge.ast.AST;
import smerge.diff.Differ;
import smerge.parsers.Parser;

import java.io.IOException;
import java.io.PrintWriter;

/**
 * This class provides the main method to run our tool.
 * 
 * @author Jediah Conachan
 */
public class Merger {
    
    /**
     * @param args [BASE, LOCAL, REMOTE, MERGED] filenames
     * @throws IOException if there is a problem reading files
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
        Parser parser = Parser.getInstance(merged);
        
        System.out.println("Parsing merge conflict files...");
        AST baseTree = parser.parse(base);
        AST localTree = parser.parse(local);
        AST remoteTree = parser.parse(remote);        
        
        // TREE DIFFING
        System.out.println("Generating AST diffs...");
        Differ differ = new Differ(baseTree, localTree, remoteTree);
        ActionSet localActions = new ActionSet();
        ActionSet remoteActions = new ActionSet();
        differ.diff(localActions, remoteActions);
           
        
        // MERGING
        System.out.println("Merging changes...");
        ActionMerger merger = new ActionMerger(localActions, remoteActions, parser);
        merger.merge();
        
        
        // OUTPUT
        System.out.println("Writing result to " + merged);
        String result = parser.unparse(baseTree);
        PrintWriter out = new PrintWriter(merged);
        out.println(result);
        out.close();
        System.out.println();
        
        
        // CONFLICT COUNTS
        System.out.println("Merge conflicts resolved: " + 
        		(merger.totalConflicts - merger.unsolvedConflicts) + "/" + merger.totalConflicts);
    }
}
