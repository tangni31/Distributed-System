# Topology Management in Peer-to-Peer Systems  
## Jelasity and Babaoglu’s algorithm  

Opreating System: ubuntu-16.04  
Lanuage: Java 8  
Compiler Version: 1.8.0_161  

`TMAN.java` contains 3 classes: `TMAN`, `Node` and `Img`  
Class `TMAN` contains the main method, it implements [Jelasity and Babaoglu's algorithm](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.80.664&rep=rep1&type=pdf).  
`Node` defines all the nodes in the network.
`Img` is used for producing the node graph files.   
Other details are commented in the codes.  

For `b-topology`, use command line arguments: `java TMAN N k B`  
For `spectacles topology`, use command line arguments: `java TMAN N k S`  
where N is the total number of nodes, k is the number of neighbors each node maintains, B represents b-topology, S represents spectacles topology.  
For example: `java TMAN 1000 25 B`
