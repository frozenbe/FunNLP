

import java.io.*;
import java.util.*;


/**
 * @author Felix Rosenberg
 *
 *Solution for task given by Maluuba
 *
 *A program to provide suggestions for typing. Uses a TST data structure to store the words after reading in the file.
 *Dependencies:
TST.java 
Queue.java, 
In.java

Publicly available at:
http://algs4.cs.princeton.edu/code/
 *
 */
public class autoComplete {


	public static void main(String[] args) throws Exception{

		//initializs a ternary search tree
		TST<Integer> st = new TST<Integer>();

		//timestamp for measuring performance
		long startTime = System.currentTimeMillis();
		try {
			//text file containing word, one word per each line. Assumed to be located in the same folder
			In in = new In("./data.txt");
			System.out.println("Reading in file");
			//iterate over words in file and store new words in the TST
			for (int i=0; !in.isEmpty(); i++) {
				String key = in.readString();
				//input words reasonable in length, fixes stack overflow for 's[o^29]'
				if (key.length()>0 && key.length()<25 && !st.contains(key))
				{
					st.put(key, i);
					//System.out.println(key);
				}
			}
		}
		catch (Exception e) { System.out.println(e); }

		long endTime   = System.currentTimeMillis();
		long totalTime = endTime - startTime;
		System.out.println("Ternery search trie created in "+ (totalTime/1000) + " seconds.");	

		Scanner scanner = new Scanner (System.in);
		System.out.println("Please type the prefix of a word: Type '/exit' to terminate");
		String prefix = scanner.next();
		//prompts the user until typed '/exit'
		while(!prefix.equalsIgnoreCase("/exit"))
		{
			startTime = System.currentTimeMillis();	
			//retrieves suggestions from TST
			for (String s : st.prefixMatch(prefix))
				System.out.println(s);
			   	endTime   = System.currentTimeMillis();
			   	totalTime = endTime - startTime;
				System.out.println("Suggestions retrieved in "+ (totalTime/1000) + " seconds.");	
			   	
				System.out.println("Please type the prefix of a word: Type '/exit' to terminate");
				prefix = scanner.next();
		}
		


	}

}