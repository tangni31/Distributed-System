import java.util.ArrayList;
import java.util.Iterator;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

class Task implements Runnable{
	private int N,k;
	
	public Task(int num, int range){
		this.N = num;
		this.k = range;
	}
	private long computeSquarSum(int N,int k){//compute (N^2 + (N+1)^2 +...+(N+k-1)^2
		long sum = 0; //(N^2 + (N+1)^2 +...+(N+k)^2 = (1+2^2+..+(N+k-)^2) - (1^2+2^2+..+N^2) + N^2
		sum = computSumConsecutive(N+k-1)-computSumConsecutive(N) + N*N;
		return sum;
	}
	
	private long computSumConsecutive(int N){ //compute (1^2+2^2+3^2+...+n^2)
		long sum = 0;
		long n = (long) N;
		sum = n*(n+1)*(2*n+1)/6;
		return sum;
	}
	
	
	private boolean isPref(long sum){
		double sqrt = Math.sqrt(sum);
		int x = (int) sqrt;
		if(Math.pow(sqrt, 2) == Math.pow(x, 2)) return true;
		else return false;
	}
	
	@Override
	public void run() {
		// TODO Auto-generated method stub
		long sum;
		boolean pref;
		sum = computeSquarSum(N,k);
		pref = isPref(sum);
		if(pref){
			prefsquares.addResult(N);
		}
	}
}


public class prefsquares {
	
	public static ArrayList<Integer> result = new ArrayList<Integer>();
	public static synchronized void addResult(int num){
		result.add(num);
	}

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		int N = Integer.parseInt(args[0]);
		int k = Integer.parseInt(args[1]);
		
		Runtime rt = Runtime.getRuntime();
		int processors = rt.availableProcessors();//how many processors we have?
		
		ThreadPoolExecutor executor = new ThreadPoolExecutor(processors-1, processors-1, 0L, TimeUnit.MILLISECONDS, new LinkedBlockingQueue<Runnable>());
		
		for(int i=1;i<=N;i++){
			Task task = new Task(i,k);
			executor.execute(task);
		}
		
		executor.shutdown();//previously submitted tasks are executed,no new tasks will be accepted
		
		while(!executor.isTerminated()){ //wait all tasks to complete
		
		}
		if(result.size()==0){ //no such perfect square
			System.out.format("No such result for %d consecutive numbers for each starting number limited by %d, such that the sum of squares is itself a perfect square.\n",k,N);
		}
		Iterator<Integer> resIter = result.iterator();
		while(resIter.hasNext()){
			System.out.println(resIter.next());
		}
		System.out.println("finished!");
	}

}
