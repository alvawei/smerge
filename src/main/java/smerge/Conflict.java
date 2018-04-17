package smerge;

import java.io.FileNotFoundException;

public class Conflict {
	
	private String[] files;
	
	public Conflict(String base, String local, String remote) {
		files = new String[]{base, local, remote};
	}
	
	public ASTree getTree(int file) throws FileNotFoundException {
		return new ASTree(files[file]);
	}
}