package smerge.test;

import static org.junit.Assert.*;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

import org.junit.Test;

import smerge.ast.AST;
import smerge.parsers.PythonParser;

public class TestPythonParser {
	
	public static final String SIMPLE = "conflicts/test/test_remote.py";
	
	@Test
	public void TestSimple() throws IOException {
		File f = new File(SIMPLE);
		String fileContent = readFile(f);
		AST tree = new PythonParser().parse(SIMPLE);
		
		System.out.println(fileContent);
		System.out.println(tree);
		
		assertEquals(fileContent.trim(), tree.toString().trim());
		
	}
	
	 public static String readFile(File file) {
		    StringBuffer stringBuffer = new StringBuffer();
		    if (file.exists())
		        try {
		            //read data from file
		            FileInputStream fileInputStream = new FileInputStream(file);
		            int c;
		            while ((c = fileInputStream.read()) != -1){
		                stringBuffer.append((char) c);
		            }
		            fileInputStream.close();
		        } catch (IOException e) {
		            e.printStackTrace();
		        }
		    return stringBuffer.toString();
		}
}
