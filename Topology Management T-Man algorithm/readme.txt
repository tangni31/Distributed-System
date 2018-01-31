Opreating System: ubuntu-16.04.3 x64
Lanuage: Java 8
Compiler Version: 1.8.0_161

TMAN.java contains 3 class TMAN, Node and Img
Class TMAN contains the main method, it implements Jelasity and Babaoglu's algorithm.
Node defines all the nodes in the network.
Img is used for producing the node graph files. 
Other details are commented in the codes.

for b-topology, use command line arguments: java TMAN N k B
for spectacles topology, use command line arguments: java TMAN N k S
where N is the total number of nodes, k is the number of neighbors each node maintains, B represents b-topology, S represents spectacles topology.
