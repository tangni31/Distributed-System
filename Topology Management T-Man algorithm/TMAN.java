import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.awt.Color;
import java.awt.Graphics;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

public class TMAN {
	public static double PI = Math.PI;
	public static File fileDistance;
	public static int N;//total nodes
	public static int k;//number of neighbors
	public static String topology;
	public static BufferedWriter outputDistance;
	public static BufferedWriter outputNeighbor;
	
	public static void main(String[] args) throws IOException  {
		N = Integer.valueOf(args[0]);
		k = Integer.valueOf(args[1]);
		topology = args[2];
		Node[] nodeList = new Node[N];
		if (topology.equals("B")){  // b-topology initialize
			fileDistance = new File("B_N" + N + "_k" + k + ".txt" ); //node total distance file.txt
			fileDistance.createNewFile();
			outputDistance = new BufferedWriter(new FileWriter(fileDistance));
			nodeList = bInitalize(); //initialize
		}
		else if (topology.equals("S")){ //spectacles topology initialize
			fileDistance = new File("S_N" + N + "_k" + k + ".txt" );//node total distance file.txt
			fileDistance.createNewFile();
			outputDistance = new BufferedWriter(new FileWriter(fileDistance));
			nodeList = spectaclesInitalize();	
		}
		else {
			System.out.println("intput error! Please using the command line arguments as below: ");
			System.out.println(" java TMAN N k topology ");
			System.out.println(" topology = B or S");
		}
		for(int i = 0; i < 40; i++){  //begin 40 cycles running
			double distanceSum = 0;
			for (Node node : nodeList){  //update each node
				int selectedNeighbor = node.selectNeighbor();//randomly select 1 neighbor
				Node neighbor = nodeList[selectedNeighbor-1];
				Map <Integer,Double> nodeId = node.sendIdentifier(); //get node's neighbor list
				Map <Integer,Double> neighborId = neighbor.sendIdentifier(); //get selected neighbor's neighbor list
				node.receiveIdentifier(neighbor.getIndex(),neighborId,nodeList);  //exchange and update neighbor list
				neighbor.receiveIdentifier(node.getIndex(),nodeId,nodeList);
				distanceSum += node.distanceSum(); //total distance between all nodes and their neighbors
			}
			System.out.println("sum of distances:" + distanceSum);// sum of distances of neighboring nodes after each running cycle
			outputDistance.write(i+1 + ": sum of distances:" + distanceSum +"\r\n"); //write distance into a .txt file  
			outputDistance.flush();
			if (i == 1 || i == 5 || i == 10 || i == 15){
				Img img = new Img();	
				if (topology.equals("B")){ 
					File fileImage = new File("B_N" + N + "_k" + k + "_" + i+ "." + img.picType);//B = b-topology
					img.writeImage(img.bi, img.picType, fileImage, nodeList, N, topology);//node graph files.png
					File fileNeighbor = new File("B_N" + N + "_k" + k + "_" + i+ ".txt" );
					writeNeighbor(fileNeighbor, nodeList);
				}
				else{
					File fileImage = new File("S_N" + N + "_k" + k + "_" + i+ "." + img.picType); //S = spectacles topology
					img.writeImage(img.bi, img.picType, fileImage, nodeList, N, topology); //node graph files.png
					File fileNeighbor = new File("S_N" + N + "_k" + k + "_" + i+ ".txt" ); //node neighbor list files.txt
					writeNeighbor(fileNeighbor, nodeList);
				}	
			}
		}
		outputDistance.close();//close file
	}
	
	public static void writeNeighbor(File fileNeighbor, Node[] nodeList) throws IOException{ //write all nodes' neighbor lists into file
		fileNeighbor.createNewFile();
		outputNeighbor = new BufferedWriter(new FileWriter(fileNeighbor));
		for (Node node: nodeList){
			outputNeighbor.write("node: " + node.getIndex() + "  neighbor list: " + node.sendIdentifier().keySet() + "\r\n");  
			outputNeighbor.flush();
		}
		outputNeighbor.close();
	}
	
	public static Node[] spectaclesInitalize() throws IOException{ //spectacles initialize, initialize all nodes, return a node array includes all N nodes
		Node[] nodeList = new Node[N];
		double distanceSum = 0;
		int N1 = (int) 2*N/5; //number of nodes in the left circle of spectacles: 2N/5
		int N2 = (int) 2*N/5; //number of nodes in the right circle of spectacles: 2N/5
		int N3 = N - N1 -N2;  //number of nodes in the semi-circle: N/5
		for (int i = 1; i <= N1; i++) {  //initialize nodes in left circle
			double theta = (PI - (i-1) * 2*PI/(N1-2)); //-PI <=theta <= PI;  
			nodeList[i-1] = new Node(i, k, N, theta, topology);
		}
		for (int i = 1; i <= N2; i++) {  //initialize nodes in right circle
			double theta = (PI - (i-1) * 2*PI/(N2-2)); //-PI <=theta <= PI
			nodeList[i+N1-1] = new Node(i+N1, k, N, theta, topology);
		}
		for (int i = 1; i <= N3; i++) {  //initialize nodes in semi-circle
			double theta = - (PI - (i-1) * PI/(N3-2)); // PI/2 <=theta <= PI
			nodeList[i+N1+N2-1] = new Node(i+N1+N2, k, N, theta, topology);
		}
		for (int j = 0; j <N; j++){
			nodeList[j].getNeighbors(nodeList);
			distanceSum += nodeList[j].distanceSum();
		}
		System.out.println("sum of distances:" + distanceSum);
		outputDistance.write("initialize" + ": sum of distances:" + distanceSum +"\r\n"); //write distance into a .txt file 
		outputDistance.flush();
		return nodeList;
	}
	
	public static Node[] bInitalize() throws IOException{ //b-topology initialize, initialize all nodes, return a node array includes all N nodes
		Node[] nodeList = new Node[N];
		Node n0 = new Node(N, k, N, PI/2, topology); //initialize node N
		nodeList[N-1] = n0;
		for (int i = 1; i < N; i++) {  //initialize node 1 ~ N-1
			double theta = (PI/2 - (i-1) * PI/(N-2));
			nodeList[i-1] = new Node(i, k, N, theta, topology);
		}
		double distanceSum = 0;
		for (int j = 0; j <N; j++){
			nodeList[j].getNeighbors(nodeList);
			distanceSum += nodeList[j].distanceSum();
		}
		System.out.println("sum of distances:" + distanceSum);// sum of distances of neighboring nodes during the initialization
		outputDistance.write("initialize" + ":sum of distances:" + distanceSum +"\r\n");   
		outputDistance.flush();
		return nodeList;	
	}
}



class Node {//class Node define nodes in the network
	private Map <Integer,Double> neighborMap = new HashMap<Integer,Double>();
	private int nodeIndex;
	private int k;
	private int N;
	private double theta;
	private String topology;
	public Node(int nodeIndex,int k, int N, double theta,String topology){ 
		this.nodeIndex = nodeIndex;
		this.N = N;
		this.k = k;
		this.theta = theta;
		this.topology = topology;
	}
	
	public int getIndex(){//get nodes' index
		return this.nodeIndex;
	}	

	public void getNeighbors(Node[] nodeList){ //randomly choose k neighbors from N nodes
		this.neighborMap.put(this.nodeIndex, (double) 0); //add node itself into its neighbor list, node's distance to itself = 0
		double distance;
		if (this.topology.equals("B")){//to make sure node N has node1 and nodeN-1, add node1 and nodeN-1 to all nodes' neighbor list at initialization 
			Node node1 = nodeList[0]; //node1
			Node nodeN_1 = nodeList[N-2];//node N-1
			double distanceNode_1 = this.computeDistanceB(this,node1);
			double distanceNodeN_1 = this.computeDistanceB(this,nodeN_1);
			this.neighborMap.put(1,distanceNode_1); 
			this.neighborMap.put(N-1,distanceNodeN_1);
		}
		while(true){ 
			int neighborIndex = (int)(Math.random() * this.N);//random select an index
			Node node = nodeList[neighborIndex];//use index get node
			if (this.topology.equals("B")){
				distance = this.computeDistanceB(this,node);//compute distance
			}
			else{
				distance = this.computeDistanceSpect(this, node);//compute distance
			}
			this.neighborMap.put(neighborIndex+1,distance);//put node index and distance into neighbor list
			if (neighborMap.size()==this.k+1){//node's neighbor list has k neighbors and node itself
				break;
			}
		}	
	}
			
	public Integer selectNeighbor(){ //randomly select 1 neighbor from k neighbors
		int rn = (int)(Math.random() * neighborMap.size()); //randomly pick an index
        int i = 0;  
        for (Integer key : neighborMap.keySet()) {  
            if(i==rn){  
            	if (neighborMap.get(key) == (double) 0){ //distance = 0, selected itself
            		return  selectNeighbor(); //try again
            	}
            	else{
            		return key;  //return neighbor's index
            	}
            }  
            i++;  
        }  
        return null;  
    }  
			
	public double computeDistanceSpect(Node a, Node b){ //spectacles topology compute distance
		int N1 = (int) 2*N/5; //number of nodes in the left circle of spectacles: 2N/5
		int N2 = (int) 2*N/5; //number of nodes in the right circle of spectacles: 2N/5
		int N3 = N - N1 -N2;  //number of nodes in the semi-circle: N/5
		if((1<a.nodeIndex && a.nodeIndex<N1)&& b.nodeIndex>=N1){
			return 1e40;//use 1e40 to represent inf 
		}//nodes from left circle are not allowed to connected to nodes from semi-circle and right circle(except intersection node)
		else if	((N1+2<a.nodeIndex && a.nodeIndex<N1+N2) && (b.nodeIndex<=N1 || b.nodeIndex>=N1+N2)){
			return 1e40;	
		}//nodes from right circle are not allowed to connected to nodes from semi-circle and left circle(except intersection node)
		else if (N1+N2<a.nodeIndex && b.nodeIndex<=N1+N2){
			return 1e40;
		}//nodes from semi-circle are not allowed to connected to nodes from left circle and right circle(except intersection node)
		
		else{
			double x = a.computeX() - b.computeX();
			double y = a.computeY() - b.computeY();
			return Math.sqrt((Math.pow(x,2)+ Math.pow(y,2))); //compute distance	
		}
	}
	
	public double computeDistanceB(Node a, Node b){  //b-topology compute distance
		if (a.nodeIndex == b.nodeIndex){ //nodeindex = itself, distance = 0
			return (double) 0;
		}
		if  (a.nodeIndex == this.N) { //if node a = node N,exchange node a and node b
			Node temp = a;
			a = b;
			b = temp;
		}
		if(b.nodeIndex == this.N){
			if (1 == a.nodeIndex || a.nodeIndex == this.N - 1 ){	
			
				return (double) 1;
			}
			else{
				return 1.0e40; //inf
			}
		}
		else{
			double x = Math.cos(a.theta)-Math.cos(b.theta);
			double y = Math.sin(a.theta)-Math.sin(b.theta);
			return Math.sqrt((Math.pow(x,2)+ Math.pow(y,2)));
		}
	}
	
	public double distanceSum(){ //compute the sum of distance to all its neighbors
		double sum = 0;
		for(Integer key : this.neighborMap.keySet()){
			if(this.neighborMap.get(key) == 1.0e40 ){ //distance=inf, discard
				sum += 0;
			}
			else{
			sum += this.neighborMap.get(key);
			}
		}
		return sum;	
	}
	
	private int findLargestKey(){ //find the neighbor with largest distance in the map
		double largestDistance = 0;
		int largestKey = 0;
		for (Integer k : this.neighborMap.keySet()){
			if (this.neighborMap.get(k) > largestDistance){
				largestDistance = this.neighborMap.get(k);
				largestKey = k;
			}	
		}	
		return largestKey;		
	}
	
	public void receiveIdentifier(int neighborIndex, Map <Integer,Double> neighborInform, Node[] nodeList){ //receive list from other neighbor and update 
		double distance;
		for (int key:neighborInform.keySet()){ 	//compute every new neighbor's distance, if it less than the largest distance in the map, add it to map	
			if (this.neighborMap.containsKey(key) == false){
				Node newNode = nodeList[key-1];
				if (this.topology.equals("B")){
					distance = this.computeDistanceB(this, newNode);
				}
				else {
					distance = this.computeDistanceSpect(this, newNode);
				}
				int largestKey = this.findLargestKey(); //get the neighbor with largest distance in map
				if (distance < this.neighborMap.get(largestKey)){ //new neighbor's distance less than the largest distance in map
					this.neighborMap.remove(largestKey); //remove the old neighbor with largest distance in map
					this.neighborMap.put(newNode.nodeIndex, distance); //add new neighbor
				}
			}
		}	
	}
	
	public Map <Integer,Double> sendIdentifier(){
			return this.neighborMap;	
	}
	
	public double computeX(){ //computer node's x
		if (this.topology.equals("B")){
				return Math.cos(this.theta);
			}		
		else{
			int N1 = (int) 2*N/5; //number of nodes in the left circle of spectacles
			int N2 = (int) 2*N/5; //number of nodes in the right circle of spectacles
			if (1 <= this.nodeIndex && this.nodeIndex < N1){ //a in left circle, x add -2
				return Math.cos(this.theta) - 2;		
			}
			else if (1+N1 <= this.nodeIndex && this.nodeIndex <= N2+N1){ //a in right circle, x add 2
				return Math.cos(this.theta) + 2;
			}
			else {  
				return Math.cos(this.theta); //a in semi-circle
			}	
		}	
	}
	
	public double computeY(){ //computer node's y
		if (this.topology.equals("B")){
			if (this.nodeIndex == N){//Node N in b-topology
				return (double) -2;
			}
			else{
				return Math.sin(this.theta);
			}
		}
		else{
			return Math.sin(this.theta);
		}
	}
}
 
 

class Img {//class Img is used for plot node graph files
 	public int N;
 	BufferedImage bi = new BufferedImage(1000, 1000, BufferedImage.TYPE_INT_BGR);
 	String picType = "png";
 	
 	public boolean writeImage(BufferedImage bi, String picType, File file, Node[] nodeList, int n, String topology)  {
 	   N = n;
 	   double nodeX = 0;
 	   double nodeY = 0;
 	   double neighborX = 0;
 	   double neighborY = 0;
 	   Graphics g = bi.getGraphics();
 	   g.fillRect(0,0, 1000, 1000); //change background color
        g.setColor(Color.BLACK);
  	   for (Node node : nodeList){
  		   nodeX = node.computeX() * 100 + 500; //adjust figure's position
  		   nodeY = node.computeY() * 100 + 500;
  		   for (Integer k : node.sendIdentifier().keySet()){
  			   if (node.sendIdentifier().get(k) == 1.0e40){ //inf, discard
  				   continue;
  			   }
  			   else{
  				   neighborX = nodeList[k-1].computeX() * 100 + 500;
  				   neighborY = nodeList[k-1].computeY() * 100 + 500;
  				   g.drawLine((int)nodeX, (int)nodeY, (int)neighborX, (int)neighborY); //draw lines between nodes and its neighbors
  			   }
  		   }
  	   }
  		g.dispose();
         boolean val = false;
         try {
         	val = ImageIO.write(bi, picType, file);
         }catch (IOException e) {
             e.printStackTrace();
         }
         return val;
     }       
 }
 	