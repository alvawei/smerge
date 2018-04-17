package smerge;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Arrays;

public class Conflict {
	
	public static final int BASE = 0;
	public static final int LOCAL = 1;
	public static final int REMOTE = 2;
	
	private File[] files;
	
	public Conflict(String base, String local, String remote) {
		files = new File[]{
			new File(base), 
			new File(local), 
			new File(remote)
		};
	}
	
	public File getFile(int file) {
		return files[file];
	}
}