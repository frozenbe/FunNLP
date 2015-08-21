
import java.io.*;
import java.util.*;

import com.maluuba.*;

import static java.lang.Math.*;


/**
 * @author Feliks Rozenberg
 * 
 * A knn classifier with k=1 for handwritten digits
 * 
 * For the following task:
 * Your task is to write a handwriting recognizer for the digits 0 through 9. Given a bitmap
of a particular digit, the completed system should be able to classify it as one of the ten
digits with a reasonable degree of accuracy.
To aid you in this task, you will be given a file containing nearly 2000 correctly-labelled
instances of hand-written digits, evenly distributed among all ten classes. You are free to
train with this data set using any algorithm you think is best-suited to the task. Your
submission should contain the code and compiled models necessary for us to read and
execute the system against our own evaluation set.
 * 
 */
public class recognizer {
	
	//a helper method to compute the euclidean distance between a single test and train instance
	private static double EucDistance (Digit instanceTest, Digit instanceTrain)
	{
		double dist=0;
		
		int classificationLabel = instanceTrain.getClassification();
		
		double[][] instanceTestFeatures =  instanceTest.getBitmap();
		double[][] instanceTrainFeatures =  instanceTrain.getBitmap();
		
		for (int i=0; i< instanceTestFeatures.length; i++)
			for(int j=0; j<instanceTestFeatures[i].length; j++)
				dist+= pow(instanceTestFeatures[i][j]-instanceTrainFeatures[i][j]   ,2.0);
			
		
		return sqrt(dist);
	}
	
	//a helper method that takes a map of computed distances and respective labels in the train set and returns the label 
	//corresponding to the train instance with the smallest distance to the test instance
	private static int classifyBySmallestDist (HashMap<Double, Integer> distancesAndRespectiveLabels, int k) 
	{
		//tree map to have the distances sorted
		Map<Double, Integer> sortedByDistance = new TreeMap<Double, Integer>(distancesAndRespectiveLabels); 
		HashMap<Integer, Integer> labelsAndCounters = new HashMap<Integer, Integer>(k); 
		
        Set set = sortedByDistance.entrySet();
        Iterator iterator = set.iterator();
        
        int classificationLabel=-1;
		
        //store the labels for k closest instances and count their occurrences
        for(int i=0;i<k;i++)
        {
        	Map.Entry smallestDistance = (Map.Entry)iterator.next();
        	int labelKey = (Integer) smallestDistance.getValue();
        	
        	//update counters for classification labels
        	if (labelsAndCounters.containsKey(labelKey)) {
        		int oldValue = labelsAndCounters.get(labelKey);
        		labelsAndCounters.put(labelKey, oldValue + 1);
        	} else {
        		labelsAndCounters.put(labelKey, 1);
        	}
        }
        
        //sort labelsAndCounters Map by value to return the label corresponding to the largest counter
        HashMap<Integer, Integer> map = sortByValues(labelsAndCounters); 
        
        Set set2 = map.entrySet();
        Iterator iterator2 = set2.iterator();
        while(iterator2.hasNext()) {
             Map.Entry me2 = (Map.Entry)iterator2.next();
             classificationLabel= (Integer) me2.getKey(); 
             
        }
        
        if (classificationLabel==-1) System.out.println("Something went wrong. Classification cannot be '-1'.");
        
		return classificationLabel;
	}
	
	//a helper method to sort the k closest training instances by their label counters
	private static HashMap sortByValues(HashMap map) { 
	       List list = new LinkedList(map.entrySet());
	       // Defined Custom Comparator here
	       Collections.sort(list, new Comparator() {
	            public int compare(Object o1, Object o2) {
	               return ((Comparable) ((Map.Entry) (o1)).getValue())
	                  .compareTo(((Map.Entry) (o2)).getValue());
	            }
	       });

	       // Here I am copying the sorted list in HashMap
	       // using LinkedHashMap to preserve the insertion order
	       HashMap sortedHashMap = new LinkedHashMap();
	       for (Iterator it = list.iterator(); it.hasNext();) {
	              Map.Entry entry = (Map.Entry) it.next();
	              sortedHashMap.put(entry.getKey(), entry.getValue());
	       } 
	       return sortedHashMap;
	  }
	
	public static void main(String[] args) throws Exception{

		//data structures initialization
		List<Digit> listOfDigits = new ArrayList<Digit>();
		double counterIncorrectClassification=0;
		double errorRate=0;
		double counterClassificationsMade=0;
		
		
		System.out.println("Please input k value: ");
		
		Scanner scanner = new Scanner (System.in);
		
		//knn classification where k=
		int k= scanner.nextInt ();
		
		System.out.println("Reading in arff file...");
		//parse digit data into list 
		try {
			listOfDigits  = Digit.parseFile("train-digits.arff");
		} 

		catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		int numberOfElements = listOfDigits.size();
		
		//split into training and testing sets
		List<Digit> train = listOfDigits.subList(0, (int) (0.6*numberOfElements));
	    List<Digit> test = listOfDigits.subList((int) (0.6*numberOfElements), numberOfElements);
		
		System.out.println("number of elements in training set " + train.size());
		System.out.println("number of elements in test set " + test.size());
		
		System.out.println("Do you want to print out classification results and correct classification? yes/no ");
		
		String ans = scanner.next();
		
		//K closest neighbour classification. K=1
		//iterate over test data
		Iterator<Digit> iteratorForTestDigits = test.iterator();
		

		while (iteratorForTestDigits.hasNext()) {

			Digit instanceTest = iteratorForTestDigits.next();
			int correctClassification = instanceTest.getClassification();
			//hashmap to find the label for smallest distance. Key is computed distance, value is label
			HashMap<Double, Integer> distancesAndRespectiveLabels = new HashMap<Double, Integer>(train.size());
				
			Iterator<Digit> iteratorForTrainDigits = train.iterator();
			//iterate over train data, compute distance and store distances and respective label
			//in a map in order to find label for smallest distance
			while (iteratorForTrainDigits.hasNext()) {	
			
			Digit instanceTrain = iteratorForTrainDigits.next();	
			double eucDistance= EucDistance (instanceTest, instanceTrain);
			distancesAndRespectiveLabels.put(eucDistance, instanceTrain.getClassification());
			}
			
			
			int classificatioResult =classifyBySmallestDist (distancesAndRespectiveLabels,k); 
			
			counterClassificationsMade++;
			
			if (classificatioResult!=correctClassification) counterIncorrectClassification++;
			
			
			
			if (ans.equalsIgnoreCase("yes"))
			System.out.println("Classifier result for current test instance: " + classificatioResult + " correct classification: " + correctClassification );		
		}

		
	
		errorRate= counterIncorrectClassification/counterClassificationsMade;
		System.out.println("Error rate in percents: " + (errorRate*100));

	}

}