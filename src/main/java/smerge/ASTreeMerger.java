package smerge;

import java.io.FileNotFoundException;


/**
 * Attempts to produce a merge conflict resolution through merging abstract syntax tree
 *
 */
public class ASTreeMerger {
	
	public static Resolution merge(Conflict conflict) throws FileNotFoundException {		
		ASTree base = Parser.parse(conflict.getBaseFile());
		ASTree local = Parser.parse(conflict.getLocalFile());
		ASTree remote = Parser.parse(conflict.getRemoteFile());
		
		
		return null;
	}
	
}