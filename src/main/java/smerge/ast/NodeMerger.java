package smerge.ast;

import java.util.ArrayList;
import java.util.Arrays;

import smerge.Merger;
import smerge.ast.ASTNode.Type;

public class NodeMerger {
	
	// attempts to merge the given nodes
	// return base node
	public static ASTNode merge(ASTNode base, ASTNode local, ASTNode remote) {
		Merger.totalConflicts++;
		
		Type type = base != null ? base.getType() : local.getType();
		
		// merge imports
		if (type == Type.IMPORT) {
			if (base != null) {
				String[] imports = {base.getContent(), local.getContent(), remote.getContent()};
				Arrays.sort(imports);
				base.setContent(imports[0] + "\n" + imports[1] + "\n" + imports[2]);
			} else {
				String[] imports = {local.getContent(), remote.getContent()};
				Arrays.sort(imports);
				base = new ASTNode(local.getType(), imports[0] + "\n" + imports[1], 0);
			}
			Merger.solvedConflicts++;
			return base;
		}
		
		// if there is a comment conflict, keep the base comment by doing nothing
		if (type == Type.COMMENT || type == Type.BLOCK_COMMENT) {
			Merger.solvedConflicts++;
			return base; 
		} 
		
		
		if (base != null) {
			// merge getIndentation() if content if getIndentation() is from one tree's change
			// and content is from the other's
			if (base.getIndentation() == local.getIndentation() && base.getIndentation() != remote.getIndentation() &&
					!base.getContent().equals(local.getContent()) && base.getContent().equals(remote.getContent())) {
				base.setContent(local.getContent());
				base.setIndentation(remote.getIndentation());
				Merger.solvedConflicts++;
				return base;
			} else if (base.getIndentation() == remote.getIndentation() && base.getIndentation() != local.getIndentation() &&
					base.getContent().equals(local.getContent()) && !base.getContent().equals(remote.getContent())) {
				base.setContent(remote.getContent());
				base.setIndentation(local.getIndentation());
				Merger.solvedConflicts++;
				return base;
			}
		} else {
			if (local.getContent().equals(remote.getContent())) {
				base = new ASTNode(local.getType(), local.getContent(), local.getIndentation());
				Merger.solvedConflicts++;
				return base;
			}
		}
		

		String baseContent = base == null ? "" : base.getContent();
		
		// this happens if:
		//    1. users change same line
		//    2. users insert new line at same spot
		
		String conflict = "<<<<<<< REMOTE\n" + 
				remote.getContent() + "\n" +
				"=======\n" + 
				baseContent + "\n" +
				"=======\n" + 
				local.getContent() + "\n" +
				">>>>>>> LOCAL";
		if (base == null) base = new ASTNode(local.getType(), conflict, 0);
		base.setID(local.getID());
		return base;
	}
}
