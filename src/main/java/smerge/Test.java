package smerge;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

import smerge.ast.AST;
import smerge.ast.ASTDiffer;
import smerge.ast.ASTMatcher;
import smerge.ast.actions.Action;
import smerge.ast.python.PythonParser;

public class Test {
	
	// i just run this main method for easy testing

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
        System.out.println(baseTree.idTree());
        System.out.println(baseTree.debugTree());
        
        System.out.println();
        
        System.out.println(localTree);
        System.out.println(localTree.idTree());
        System.out.println(localTree.debugTree());
        
        System.out.println();
        
        System.out.println(remoteTree);
        System.out.println(remoteTree.idTree());
        System.out.println(remoteTree.debugTree());
               
        
        
        ASTDiffer diff = new ASTDiffer(baseTree, localTree, remoteTree);
        
        List<Action> actions = diff.mergedDiff();
        

        
        // write baseTree to merged
        String result = baseTree.toString();
        // System.out.println(result);
        
        // write result -> merged
        PrintWriter out = new PrintWriter(merged);
        out.println(result);

	}

}
