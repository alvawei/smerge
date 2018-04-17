package smerge;

import java.io.FileNotFoundException;


/**
 * Runs Smerge
 */
public class Merger {
	
	public static final int BASE = 0;
	public static final int LOCAL = 1;
	public static final int REMOTE = 2;
    
    /**
     * @param args [BASE, LOCAL, REMOTE, MERGED] files
     */
    public static void main(String[] args) {
        if (args.length != 4) {
            throw new RuntimeException("Expected args: BASE LOCAL REMOTE MERGED");
        } 
        
        try {
            Conflict conflict = new Conflict(args[0], args[1], args[2]);
            
            ASTree base = conflict.getTree(BASE);
            ASTree local = conflict.getTree(LOCAL);
            ASTree remote = conflict.getTree(REMOTE);
            
            ASTreeMerger treeMerger = new ASTreeMerger(base, local, remote);
            Resolution res = treeMerger.merge();
        
            


            /*

            Copied from Conflerge
    
            
            TreeMerger merger = new TreeMerger(args[0], args[1], args[2]);
            Node mergedTree = merger.merge();         
            if (mergedTree == null) {
                fail("Conflict encountered");
                return;
            }
            writeFile(mergedTree.toString(), args[3]);


            */
        } catch (FileNotFoundException e) {
            // fail("Files not found");
        } catch (Exception e) {
            // fail("Unexpected failure");
        }
    }
}
