package temp;

import java.io.IOException;
import java.io.PrintWriter;

import smerge.actions.ActionMerger;
import smerge.actions.ActionSet;
import smerge.ast.AST;
import smerge.diff.Differ;
import smerge.parsers.Parser;

// this is a class used for testing -- a small scale test, only tests one
// file at a time for conflicts

public class Test {
	
	public static void main(String[] args) throws IOException {

		String init = "scripts/test_results/pipenv_test_results/files/8_utils";
		String base = init + "_base.py";
		String local = init + "_local.py";
		String remote = init + "_remote.py";
		String merged = "tmp/temp_out.py";
        
        // get the correct parser (pass in filename for file extension/type?)
        Parser parser = Parser.getInstance(merged);
        
        // PARSING
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
        
        System.out.println(baseTree.debugTree());
        System.out.println(localTree.debugTree());
        System.out.println(remoteTree.debugTree());
        
        System.out.println("Local Minimized Actions:");
        System.out.println(localActions);
        
        System.out.println("Remote Minimized Actions:");
        System.out.println(remoteActions);
        
        // MERGING
        System.out.println("Merging changes...");
        ActionMerger merger = new ActionMerger(localActions, remoteActions, parser);
        merger.merge();
        
        System.out.println(baseTree.debugTree());
        
        // OUTPUT
        System.out.println("Writing result to " + merged);
        String result = baseTree.toString();
        PrintWriter out = new PrintWriter(merged);
        out.println(result);
        out.close();
        
        // CONFLICTS
        System.out.println("Merge conflicts resolved: " + 
        		(merger.totalConflicts - merger.unsolvedConflicts) + "/" + merger.totalConflicts);
	}

}
