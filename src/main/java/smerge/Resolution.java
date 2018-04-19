package smerge;

import java.io.IOException;
import java.io.PrintWriter;

public class Resolution {
	
	private String fileContents;
	
	public Resolution() {
		
	}
	
	// writes final file to disk, smerge should end after
	public void writeFile(String fileDest) {
		try {
            PrintWriter writer = new PrintWriter(fileDest, "UTF-8");
            writer.println(fileContents);
            writer.close();
        } catch (IOException e) {
        	System.out.println("Error writing file");
        }
	}
}
