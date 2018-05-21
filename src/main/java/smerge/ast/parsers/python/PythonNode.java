package smerge.ast.parsers.python;

import java.util.Arrays;

import smerge.ast.ASTNode;


// A PythonTree just holds onto the root PythonNode
// Primarily acts as an "unparser" through the toString() method
public class PythonNode extends ASTNode {
	
	public static final String INDENT = "    ";
			
	public PythonNode() {
		this(-1, "@root", Type.ROOT);
	}
	
	public PythonNode (int indentation, String content, Type type) {
		super();
		this.indentation = indentation;
		this.content = content;
		this.type = type;
	}
	
	// unparse this node and it's children
	public void unparse(StringBuilder sb) {
		if (!this.isRoot()) {
			indent(indentation, sb);
			sb.append(content + "\n");
		}
		for (ASTNode child : children) {
			child.unparse(sb);
		}
	}
	
	// appends indentation to the given string builder
	private void indent(int indentation, StringBuilder sb) {
		for (int i = 0; i < indentation; i++) {
			sb.append(" ");
		}
	}

	// merges this (base) with n1 and n2 (local and remote or vice versa)
	@Override
	public boolean merge(ASTNode n1, ASTNode n2) {
		if (type == Type.IMPORT) {
			// keep n1 and n2 imports
			String[] imports = {this.content, n1.getContent(), n2.getContent()};
			Arrays.sort(imports);
			this.content = imports[0] + "\n" + imports[1] + "\n" + imports[2];
			return true;
		} else if (type == Type.COMMENT || type == Type.BLOCK_COMMENT) {
			// keep base comment for now
			return true; 
		}
		if (indentation == n1.indentation && indentation != n2.indentation &&
				!content.equals(n1.getContent()) && content.equals(n2.getContent())) {
			content = n1.getContent();
			indentation = n2.indentation;
			return true;
		} else if (indentation == n2.indentation && indentation != n1.indentation &&
				content.equals(n1.getContent()) && !content.equals(n2.getContent())) {
			content = n2.getContent();
			indentation = n1.indentation;
			return true;
		}
		return false;
	}
	
	public void update(ASTNode edit) {
		this.content = edit.getContent();
		this.indentation = edit.indentation;
	}
	
	@Override
	public boolean equals(Object o) {
		if (o instanceof PythonNode) {
			return getID() == ((PythonNode) o).getID();
		}
		return false;
	}
}
