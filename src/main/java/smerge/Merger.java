package smerge;

import java.io.FileNotFoundException;

/**
 * Runs Smerge
 */
public class Merger {
	
    
    /**
     * @param args [BASE, LOCAL, REMOTE, MERGED] files
     */
    public static void main(String[] args) {
        if (args.length != 4) {
            throw new RuntimeException("Expected args: BASE LOCAL REMOTE MERGED");
        } 
        
        try {
            Conflict conflict = new Conflict(args[0], args[1], args[2]);
            Resolution res = ASTreeMerger.merge(conflict);
            res.writeFile(args[3]);
        } catch (FileNotFoundException e) {
            // fail("Files not found");
        } catch (Exception e) {
            // fail("Unexpected failure");
        }
    }
}
