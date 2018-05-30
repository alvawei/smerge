package temp;

import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import smerge.Merger;


public class BiggerTest {
	

	// this is a temporary class for testing
	
	public static void main(String[] args) throws IOException {
		Set<String> filenames = new HashSet<>();
		Set<String> dirnames = new HashSet<>();
		
		dirnames.add("scripts/test_results/ansible_test_results/files");
		dirnames.add("scripts/test_results/flask_test_results/files");
		dirnames.add("scripts/test_results/keras_test_results/files");
		dirnames.add("scripts/test_results/models_test_results/files");
		dirnames.add("scripts/test_results/pipenv_test_results/files");
		dirnames.add("scripts/test_results/scikit-learn_test_results/files");
		dirnames.add("scripts/test_results/XX-Net_test_results/files");






		
		for (String dirname : dirnames) {
			// get filenames
			File[] files = new File(dirname).listFiles();
			for (File f : files) {
				String filename = f.toString();
				filenames.add(filename.substring(0, filename.lastIndexOf('_')));
			}
		}		
		
		for (String f : filenames) {
			try {
				System.out.println("Merging " + f + ".py");
				Merger.main(new String[]{
						f + "_base.py",
						f + "_local.py",
						f + "_remote.py",
						"tmp/out.py"});
				System.out.println();
			} catch (Exception e) {
				System.out.println("Error: file not found.");
				System.out.println();
			}
		}
	}
}
