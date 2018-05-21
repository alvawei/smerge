package smerge.ast;

import java.util.Arrays;

import smerge.ast.ASTNode.Type;

public class NodeMerger {
	
	// attempts to merge the given nodes
	// return true iff the merge is resolved
	public static boolean merge(ASTNode base, ASTNode local, ASTNode remote) {
		Type type = base.getType();
		
		// merge imports
		if (type == Type.IMPORT) {
			// merge imports
			String[] imports = {base.getContent(), local.getContent(), remote.getContent()};
			Arrays.sort(imports);
			base.setContent(imports[0] + "\n" + imports[1] + "\n" + imports[2]);
			return true;
		}
		
		// if there is a comment conflict, keep the base comment by doing nothing
		if (type == Type.COMMENT || type == Type.BLOCK_COMMENT) {
			return true; 
		} 
		
		// merge getIndentation() if content if getIndentation() is from one tree's change
		// and content is from the other's
		if (base.getIndentation() == local.getIndentation() && base.getIndentation() != remote.getIndentation() &&
				!base.getContent().equals(local.getContent()) && base.getContent().equals(remote.getContent())) {
			base.setContent(local.getContent());
			base.setIndentation(remote.getIndentation());
			return true;
		} else if (base.getIndentation() == remote.getIndentation() && base.getIndentation() != local.getIndentation() &&
				base.getContent().equals(local.getContent()) && !base.getContent().equals(remote.getContent())) {
			base.setContent(remote.getContent());
			base.setIndentation(local.getIndentation());
			return true;
		}
		
		// unresolvable conflict
		String conflict = "<<<<<<< REMOTE\n" + 
				remote.getContent() + "\n" +
				"=======\n" + 
				base.getContent() + "\n" +
				"=======\n" + 
				local.getContent() + "\n" +
				">>>>>>> LOCAL";
		base.setContent(conflict);
		base.setIndentation(0);
		return false;
	}
}
