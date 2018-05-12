package smerge.ast;

// should be thrown when an unmergable conflict is detected
// this should allow us to tell the user specifically why a merge can't be performed

@SuppressWarnings("serial")
public class MergeException extends Exception {
	
	private Match match;
	
	public MergeException(Match match) {
		this.match = match;
	}
	
	// an example of how to trace back information
	public String info() {
		return match.toString();
	}

}
