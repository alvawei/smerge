package smerge;

import java.io.FileNotFoundException;

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
        
        

    }
}
