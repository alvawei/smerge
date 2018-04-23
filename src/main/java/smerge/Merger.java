package smerge;

import java.io.FileNotFoundException;

import com.github.javaparser.ast.Node;

import conflerge.tree.TreeMerger;

/**
 * Runs Smerge
 */
public class Merger {
	
    
    /**
     * @param args [BASE, LOCAL, REMOTE, MERGED] files
     * @throws FileNotFoundException 
     */
    public static void main(String[] args) throws FileNotFoundException {

        String base = "conflicts/test/Simple_Base.java"; // args[0];
        String local = "conflicts/test/Simple_Local.java"; // args[1];
        String remote = "conflicts/test/Simple_Remote.java"; // args[2];
        // String merged = args[3];
        
        

        
       String resolution = conflerge(base, local, remote);
       System.out.println(resolution);
    }
    
    public static String conflerge(String base, String local, String remote) throws FileNotFoundException {        
        TreeMerger merger = new TreeMerger(base, local, remote);
        Node mergedTree = merger.merge();         
        if (mergedTree == null) {
        	return null;
        }
        return mergedTree.toString();
    }
}
