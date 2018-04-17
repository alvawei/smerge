package smerge;

import java.io.FileNotFoundException;

public class ASTreeMerger {
	
	public static Resolution merge(Conflict conflict) throws FileNotFoundException {		
		ASTree base = Parser.parse(conflict.getFile(Conflict.BASE));
		ASTree local = Parser.parse(conflict.getFile(Conflict.LOCAL));
		ASTree remote = Parser.parse(conflict.getFile(Conflict.REMOTE));
		return null;
	}
	
}