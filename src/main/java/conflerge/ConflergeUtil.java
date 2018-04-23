package conflerge;

import java.io.IOException;
import java.io.PrintWriter;

/**
 * Globally useful definitions.
 */
public class ConflergeUtil {
    
    /**
     * The number of expected command-line arguments.
     */
    static final int NUM_ARGS = 4;
    
    /**
     * true iff a conflict has been detected.
     */
    public static boolean conflict = false;
    
    /**
     * true iff a conflict has been detected in comments.
     */
    public static boolean commentConflict = false;
    
    /**
     * Reports the detection of a conflict.
     */
    public static void reportConflict() {
        ConflergeUtil.conflict = true;
    }
    
    /**
     * Reports the detection of a conflict in comments.
     */
    public static void reportCommentConflict() {
        ConflergeUtil.commentConflict = true;
    }
    
    
    /**
     * Writes mergedFile to mergedFileDest.
     * @param mergedFile
     * @param mergedFileDest
     */
     static void writeFile(String fileContents, String fileDest) {
        try {            
            PrintWriter writer = new PrintWriter(fileDest, "UTF-8");
            writer.println(fileContents);
            writer.close();
            System.out.println("SUCCESS");
            if (commentConflict) {
                System.out.println("Conflicting comments remaining: please resolve these manually.");
            }            
        } catch (IOException e) {
            fail("Unexpected error writing to file");
        }
    }

    /**
     * Display a failure message.
     */
    static void fail(String message) {
        System.out.println("FAILURE");
        System.err.println(message);
    }
}
