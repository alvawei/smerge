package smerge.ast;

import java.util.Arrays;

import smerge.Merger;
import smerge.ast.ASTNode.Type;

public class NodeMerger {
	
	// attempts to merge the given nodes
	// return base node
	public static ASTNode merge(ASTNode base, ASTNode local, ASTNode remote) {
		Merger.totalConflicts++;
		
		if (base != null) {
			Type type = base.getType();
			// merge imports
			if (type == Type.IMPORT) {
				// merge imports
				String[] imports = {base.getContent(), local.getContent(), remote.getContent()};
				Arrays.sort(imports);
				base.setContent(imports[0] + "\n" + imports[1] + "\n" + imports[2]);
				return base;
			}
			
			// if there is a comment conflict, keep the base comment by doing nothing
			if (type == Type.COMMENT || type == Type.BLOCK_COMMENT) {
				return base; 
			} 
			
			// merge getIndentation() if content if getIndentation() is from one tree's change
			// and content is from the other's
			if (base.getIndentation() == local.getIndentation() && base.getIndentation() != remote.getIndentation() &&
					!base.getContent().equals(local.getContent()) && base.getContent().equals(remote.getContent())) {
				base.setContent(local.getContent());
				base.setIndentation(remote.getIndentation());
				return base;
			} else if (base.getIndentation() == remote.getIndentation() && base.getIndentation() != local.getIndentation() &&
					base.getContent().equals(local.getContent()) && !base.getContent().equals(remote.getContent())) {
				base.setContent(remote.getContent());
				base.setIndentation(local.getIndentation());
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
		return base;
	}
}
