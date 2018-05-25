package smerge.actions;

/**
 * An Action object represents a change in a node from one tree (base) to another (edit, local or remote).
 * 
 * Different actions are defined as follows:
 * 
 * 		Delete: a node existing in the base tree does not exist in the edit tree
 * 		Insert: a node existing in the edit tree does not exist in the base tree
 * 		Update: a node's content differs between the base and edit versions
 * 
 * 		TODO Move/Shifts
 * 
 * @author Jediah Conachan
 */
public interface Action {
	
	/**
	 * Applies this action onto the base tree.
	 * This method is called by an ActionMerger object.
	 */
	public void apply();

}
