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
        if (args.length != 4) {
            throw new RuntimeException("Expected args: BASE LOCAL REMOTE MERGED");
        }
        
        String base = args[0];
        String local = args[1];
        String remote = args[2];
        String merged = args[3];
        
        

        
       String resolution = conflerge(base, local, remote);
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
