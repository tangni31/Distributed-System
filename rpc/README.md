## Remote Procedure Call (RPC)

This is a simple server and client example. The time server returns the current time. The server will also be printing 
the address of the client, the client will invoke the remote procedure and will print the value returned by the server.

Please install rpcbind before running the codes: `sudo apt-get install rpcbind` and running rpcbind: `sudo rpcbind`  

To run server: `./server`   
To run client: `./client localhost`   

![sample](https://raw.githubusercontent.com/tangni31/Distributed-System/master/rpc/1.png)  

### Reference:
[ONC+ Developer's Guide](https://docs.oracle.com/cd/E23824_01/pdf/821-1671.pdf)
