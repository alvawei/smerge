package smerge;

import java.io.IOException;
import java.util.List;

import com.github.gumtreediff.*;
import com.github.gumtreediff.actions.ActionGenerator;
import com.github.gumtreediff.actions.model.Action;
import com.github.gumtreediff.client.Run;
import com.github.gumtreediff.gen.Generators;
import com.github.gumtreediff.matchers.Matcher;
import com.github.gumtreediff.matchers.Matchers;
import com.github.gumtreediff.tree.ITree;

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

	}

}
