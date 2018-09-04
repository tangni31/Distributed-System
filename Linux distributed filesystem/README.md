# Linux-filesystem
`mata/dataserver.py`: orignal code Author: David Wolinsky  Version: 0.03, 
 
`distributed_file_system.py`: orignal code https://github.com/terencehonles/fusepy/blob/master/examples/memory.py

This is a simple distuributed fuse file system which has one mataserver and multiple data servers.

All data have 3 replicas in different servers.    

## Features

- Data in data servers will be stored in a round robin fashion and using hash function to store loads evenly.

for example: 
    
    if there are 3 servers, each has 3 replicas,
    1.txt with content"11111111222222223333333344444444" may stores like:
                  server 1:   replica 1:'11111111,44444444'  repilca 2:'33333333'  replica 3:'22222222'
                  server 2:   replica 1:'22222222'  repilca 2:'11111111,44444444'  replica 3: '33333333'
                  server 3:   replica 1:'33333333'  repilca 2:'22222222'  replica 3: '11111111,44444444' 
    2.txt with content"aaaaaaaabbbbbbbbccccccccdd" may stores like:
                  server 2:   replica 1:'aaaaaaaa,dd'  replica 2:'cccccccc'  replica 3:'bbbbbbbb'
                  server 3:   replica 1:'bbbbbbbb'  replica 2:'aaaaaaaa,dd'  replica 3:'cccccccc'
                  server 1:   replica 1:'cccccccc'  replica 2:'bbbbbbbb'  replica 3:'aaaaaaaa,dd'    

<img width="500" height="150" src="https://github.com/tangni31/Distributed-System/blob/master/Linux%20distributed%20filesystem/img/f1.png?raw=true"/> 
<img width="500" height="150" src="https://github.com/tangni31/Distributed-System/blob/master/Linux%20distributed%20filesystem/img/f2.png?raw=true"/> 
<img width="500" height="150" src="https://github.com/tangni31/Distributed-System/blob/master/Linux%20distributed%20filesystem/img/f3.png?raw=true"/> 
<img width="500" height="150" src="https://github.com/tangni31/Distributed-System/blob/master/Linux%20distributed%20filesystem/img/f4.png?raw=true"/>  

##### File `/one/1.txt` store in 4 different servers 
    
        
- Data sever can dealing with crash (write data into disk using shelve), and when data in disk is completely lost, server can use replicas from other servers to recover. 

    eg. if data in server 1 is lost, server 1 can be recovered by reading data in server 2 and server 3.    
<img width="500" height="300" src="https://github.com/tangni31/Distributed-System/blob/master/Linux%20distributed%20filesystem/img/data%20lost.png?raw=true"/>     
    
- Server can dealing with data corruption by using `crc16` checksum, server can recover corrupted data by reading replicas from other servers.      
   <img width="500" height="80" src="https://github.com/tangni31/Distributed-System/blob/master/Linux%20distributed%20filesystem/img/corrupt4.png?raw=true"/> 

    
- The reads will be succeed when non-adjacent servers are crashed.  
    
- Writes will be blocked even if a single server is down and system will continue retry:    
             <img width="300" height="200" src="https://github.com/tangni31/Distributed-System/blob/master/Linux%20distributed%20filesystem/img/write_when_down2.png?raw=true"/> 
    
`corrupt.py`  is a function which can simulate data corruption:     
<img width="500" height="100" src="https://github.com/tangni31/Distributed-System/blob/master/Linux%20distributed%20filesystem/img/corrupt1.png?raw=true"/>

    
To run mataserver: `python metaserver.py <port for metaserver>`  

To run dataserver: `python distributedFS.py <fusemount directory> <metaserver port> <dataservers ports separated by spaces>`  
For example:

      (N=4): 
      python metaserver.py 2222 
      python dataserver.py 0 3333 4444 5555 6666 
      python dataserver.py 1 3333 4444 5555 6666 
      python dataserver.py 2 3333 4444 5555 6666 
      python dataserver.py 3 3333 4444 5555 6666
      python distributedFS.py fusemount 2222 3333 4444 5555 6666  
      
To run corrupt: `python corrupt.py <server port> <path> <replica index>`  
For example: to corrupt flie '/a/1.txt' in server 2222's replica 1:
`python corrupt.py 2222 '/a/1.txt' 1`

