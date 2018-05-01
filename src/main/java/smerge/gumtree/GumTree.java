package smerge.gumtree;

import java.io.IOException;
import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;

import com.github.gumtreediff.actions.ActionGenerator;
import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.actions.model.Insert;
import com.github.gumtreediff.actions.model.Delete;
import com.github.gumtreediff.actions.model.Update;
import com.github.gumtreediff.actions.model.Move;
import com.github.gumtreediff.actions.ActionUtil;

import com.github.gumtreediff.client.Run;
import com.github.gumtreediff.gen.Generators;
import com.github.gumtreediff.matchers.Matcher;
import com.github.gumtreediff.matchers.Matchers;
import com.github.gumtreediff.tree.ITree;
import com.github.gumtreediff.tree.TreeContext;

public class GumTree {
	
	public static void main(String[] args) throws UnsupportedOperationException, IOException {
		String base = "conflicts/test/Simple_Base.java";
		String local = "conflicts/test/Simple_Local.java";
		String remote = "conflicts/test/Simple_Remote.java";
		
		gumtree(base, local, remote);
	}
	
	public static void gumtree(String base, String local, String remote) throws UnsupportedOperationException, IOException {
		Run.initGenerators();
		
		ITree baseTree = Generators.getInstance().getTree(base).getRoot();
		ITree localTree = Generators.getInstance().getTree(local).getRoot();
		ITree remoteTree = Generators.getInstance().getTree(remote).getRoot();
		
		Matcher m1 = Matchers.getInstance().getMatcher(baseTree, localTree); // retrieve the default matcher
		Matcher m2 = Matchers.getInstance().getMatcher(baseTree, remoteTree); // retrieve the default matcher
		
		m1.match();
		m2.match();
		
		ActionGenerator g1 = new ActionGenerator(baseTree, localTree, m1.getMappings());
		ActionGenerator g2 = new ActionGenerator(baseTree, remoteTree, m2.getMappings());

		g1.generate();
		g2.generate();
		
		List<Action> actions1 = g1.getActions(); // return the actions
		List<Action> actions2 = g2.getActions(); // return the actions
		
		
		System.out.println(baseTree.toTreeString());
		System.out.println(localTree.toTreeString());
		System.out.println(remoteTree.toTreeString());
		
		System.out.println(baseTree.toTreeString());
		
		System.out.println(actions1);
		System.out.println(actions2);
		
		
		actions1.addAll(actions2);
		
		/*
		// applies actions
		for (Action a: actions1) {
            if (a instanceof Insert) {
                Insert action = ((Insert) a);
                action.getParent().insertChild(action.getNode(), action.getPosition());
            } else if (a instanceof Update) {
                Update action = ((Update) a);
                action.getNode().setLabel(action.getValue());
            } else if (a instanceof Move) {
                Move action = ((Move) a);
                action.getNode().getParent().getChildren().remove(action.getNode());
                action.getParent().insertChild(action.getNode(), action.getPosition());
            } else if (a instanceof Delete) {
                Delete action = ((Delete) a);
                action.getNode().getParent().getChildren().remove(action.getNode());
            } else throw new RuntimeException("No such action: " + a );
		}
		*/
		
		// traverse base tree, applying actions (this isn't even close to correct)
		List<ITree> nodes = new ArrayList<>();
		for (ITree node : baseTree.breadthFirst()) nodes.add(node);
		System.out.println(nodes);

		// might have to match nodes beyond id
		
		for (ITree node : nodes) {
			for (Action a : actions1) {
				if (a.getNode().getId() == node.getId()) {
					if (a instanceof Insert) {
		                Insert action = ((Insert) a);
		                if (action.getPosition() < node.getChildren().size())
		                	node.insertChild(action.getNode(), action.getPosition());
		                
		            } else if (a instanceof Update) {
		                Update action = ((Update) a);
		                node.setLabel(action.getValue());
		                
		            } else if (a instanceof Move) {
		                Move action = ((Move) a);
		                node.getParent().getChildren().remove(action.getNode());
		                node.getParent().insertChild(action.getNode(), action.getPosition());
		                
		            } else if (a instanceof Delete) {
		                Delete action = ((Delete) a);
		                node.getParent().getChildren().remove(action.getNode());
		                
		            } else throw new RuntimeException("No such action: " + a );
				}
			}
		}
		
		
		
		System.out.println(baseTree.toTreeString());
	}

}
