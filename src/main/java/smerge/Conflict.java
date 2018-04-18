package smerge;

import java.io.File;
import java.io.FileNotFoundException;



/**
 * A Conflict object stores merge conflict files
 *
 */
public class Conflict {
	
	private File base, local, remote;
	
	// create File objects from the given filenames
	public Conflict(String base, String local, String remote) {
		this.base = new File(base);
		this.local = new File(local);
		this.remote = new File(remote);
	}
	
	// return the base file
	public File getBaseFile() {
		return base;
	}
	
	// return the local file
	public File getLocalFile() {
		return local;
	}
	
	// return the remote file
	public File getRemoteFile() {
		return remote;
	}
}