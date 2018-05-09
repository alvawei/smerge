package smerge;

import smerge.ast.AST;
import smerge.ast.ASTDiffer;
import smerge.ast.ASTMatcher;
import smerge.ast.actions.Action;
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
     */
    public static void main(String[] args) throws IOException {

        String base = "conflicts/test/test_base.py"; // args[0];
        String local = "conflicts/test/test_local.py"; // args[1];
        String remote = "conflicts/test/test_remote.py"; // args[2];
        String merged = "conflicts/test/test_merged.py"; // args[3];
        
        // have to figure out which parser to use somehow
        // may be able to take it in as an additional git mergetool input
        AST baseTree = PythonParser.parse(new File(base));
        AST localTree = PythonParser.parse(new File(local));
        AST remoteTree = PythonParser.parse(new File(remote));
        
        ASTMatcher matcher = new ASTMatcher(baseTree.getRoot(), localTree.getRoot(), remoteTree.getRoot());
        System.out.println(baseTree);
        System.out.println(baseTree.debugTree());
        
        
        ASTDiffer diff = new ASTDiffer(baseTree, localTree, remoteTree);
        
        List<Action> actions = diff.mergedDiff();
        
        // baseTree.apply(actionns);
        
        // merge imports
        Set<String> imports = mergeImports(baseTree.imports(), localTree.imports(), remoteTree.imports());
        baseTree.imports().clear();
        baseTree.imports().addAll(imports);
        
        // write baseTree to merged
        String result = baseTree.toString();
        // System.out.println(result);
        
        // write result -> merged
        PrintWriter out = new PrintWriter(merged);
        out.println(result);
    }
    
    // combines imports from all three files
    // uses TreeSet to maintain some sort of order
    public static Set<String> mergeImports(List<String> base, List<String> local, List<String> remote) {
    	Set<String> importSet = new TreeSet<>();
    	importSet.addAll(base);
    	importSet.addAll(local);
    	importSet.addAll(remote);
    	return importSet;
    }
}
