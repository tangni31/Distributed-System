## Multi-threading

This is a simple program that using multi-threading to find a consecutive sequence that its sum of squares is a perfect square.    
For example: `1^2 + 2^2 + ... + 24^2 = 70^2`    
So, `1,2,3...24` is a consecutive sequence we want to find. 
    
This program has two types of threads: `master` and `worker` thread.    
The master thread will divide the problem into work units(sub-problems) and assign it as tasks to the slave threads.     
The slave threads work on the “work units” and return the result to the master.     
The master keeps track of the slave threadsand aggregates the result from the worker threads and computes if the final sum is a perfect square.
    
To run the program: `java prefsquares N k`   
Where N is max starting number.(The starting number of the sequences will be 1,2,3...N)   
k is the length of the sequence.   
The output of the program is the first number in the sequence for each solution.   
For example: run `java prefsquares 3 2`   
             With the start point between 1 and 3 and sequence of length 2, the valid
sequences are {1,2}, {2,3} and {3,4}. The solution is {3,4} since 3^2 + 4^2 = 5^2.    
![sample](https://raw.githubusercontent.com/tangni31/Distributed-System/master/multi-threading/1.png)
