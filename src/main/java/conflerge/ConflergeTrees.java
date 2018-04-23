package conflerge;

import static conflerge.ConflergeUtil.*;

import java.io.FileNotFoundException;

import com.github.javaparser.ast.Node;

import conflerge.tree.TreeMerger;

/**
 * Runs Conflerge with an AST-based merging strategy.
 */
public class ConflergeTrees {
    
    /**
     * @param args [BASE, LOCAL, REMOTE, MERGED] files
     */
    public static void main(String[] args) {
        if (args.length != NUM_ARGS) {
            fail("Expected args: BASE LOCAL REMOTE MERGED");
            return;
        } 
        
        try {
            TreeMerger merger = new TreeMerger(args[0], args[1], args[2]);
            Node mergedTree = merger.merge();         
            if (mergedTree == null) {
                fail("Conflict encountered");
                return;
            }
            writeFile(mergedTree.toString(), args[3]);
        } catch (FileNotFoundException e) {
            fail("Files not found");
        } catch (Exception e) {
            fail("Unexpected failure");
        }
    }
}
