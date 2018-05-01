package smerge.ast;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;


public class ASTDiffer {
	
	// possible solution:
	// generate a Map<Integer, Set/List<Integer>> for each tree, mapping node.getID() -> node.children().getID()
	// run line based diffing on each set
	
}
