# Linux-filesystem
mata/dataserver.py: orignal code Author: David Wolinsky  Version: 0.03, 
 
distributed_file_system.py: orignal code “https://github.com/terencehonles/fusepy/blob/master/examples/memory.py”

this is a distuributed fuse file system which has one mataserver and multiple data servers.

all data have 3 replicas in different servers.

data in data servers will be stored in a round robin fashion and using hash function to store loads evenly.

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

Data sever can dealing with crash (write data into disk using shelve), and when data in disk is completely lost, server can use replicas from other servers to recover. 

    eg. if data in server 1 is lost, server 1 can be recovered by reading data in server 2 and server 3.

Server can dealing with data corruption by using crc16 checksum, server can recover corrupted data by reading replicas from other servers.

corrupt.py  is a function which can simulate data corruption.
