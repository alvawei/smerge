package temp;

import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import smerge.Merger;


public class BiggerTest {
	
	public static final String DIR = "scripts/test_results/keras_test_results/files";

	// this is a temporary class for testing
	
	public static void main(String[] args) throws IOException {
		Set<String> filenames = new HashSet<>();
		
		
		// get filenames
		File[] files = new File(DIR).listFiles();
		for (File f : files) {
			String filename = f.toString();
			filenames.add(filename.substring(0, filename.lastIndexOf('_')));
		}
		
		for (String f : filenames) {
			System.out.println("Merging " + f + ".py");
			Merger.main(new String[]{
					f + "_base.py",
					f + "_local.py",
					f + "_remote.py",
					"tmp/out.py"});
			System.out.println();
		}
	}
}
