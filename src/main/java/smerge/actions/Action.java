package smerge.actions;

public interface Action {
	
	// applies the action to the base tree
	// note that the there should be an order of which types of actions are applied first
	// this is because actions rely on position of children
	
	// maybe:
	//     DELETE
	//     INSERT
	//     MOVE
	//
	//     UPDATE
	public void apply();

}
