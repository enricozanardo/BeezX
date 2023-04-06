# Technical documentation Beez blockchain
In this documentation the basic functionality and communication of the single components in the Beez blockchain will be described.

## Node
The Node resembles the central module which manages all different components of the system.
For communication it holds instances of the socket communication module and the API.
Furthermore, it holds an instance to the local blockchain as well as to it's local transaction pool.
The Node also holds its own wallet which is used to sign f.e. new blocks which are being forged by this Node.

### BasicNode
Base Node class.
It only defines the base parameters for the constructor as general methods used by all types of nodes in the system.

### Seed node
This type of Node is used to orchestrate the digital asset manager (DAM).
What's special about this node is, that it is not concerned with the blockchain itself and thus does not hold instances to a local blockchain or a local transaction pool. The main purpose of a Seed node is to manage the digital assets. Therefore it implements methods to receive digital assets, split them up in chunks and push/pull them to/from normal Beez nodes.
A dedicated hearthbeat thread iteratively checks the health status of all connected Beez nodes. This is especially important in cases where nodes are not reachable anymore but there are digital asset chunks stored on this specific node. To prevent situations where a digital asset cannot be pulled anymore, all chunks are going to be backed up by the Beez nodes neighbor Beez node. Details on how the backup mechanism works will be discussed in the Beez node part of this documentation. The important bit of information is though, that upon node outages, the Seed node knows about dead nodes and upon digital asset download attempts knows which node to ask for specific chunks also, if the primary node is not working at that point in time.

### Beez node
This type of node is used to handle the `normal` blockchain. It is used to receive, validate and add transactions to the transaction pool and later on to the blockchain. If the node has some staked token, it will be chosen to forge blocks in a proportional to stake but random way. Furthermore, upon digital asset uploads, the Seed node might push asset chunks to this kind of nodes as well. In this case, the node stores the chunks and waits until the Seed node requests them back in a later point in time. Every Beez node has a corresponding adjacent neighbor node. This neighbor node is used to backup all digital asset chunks pushed from the Seed node to the Beez nodes. So everytime a Beez node gets a new digital asset chunk, it also pushes the chunk to its neighbor so the chunk is stored twice in the network.

## Socket Communication
The entire intra-network communication between nodes is done using socket connections. This is what this module implements. Every node holds a socket communication instance which is used for that communication. Messages received via the socket communication module is forwareded to the node which handles the messages. This could either be to split a digital asset between multiple Beez nodes, validating and adding new transfer transactions to the transaction pool, validating and appending a new block to the blockchain or even sending the entire blockchain state to another node.

### BaseSocketCommunication
This is the base class used by all types of socket communication. It implements the very basic methods used to start the socket communication as well as sending messages to a given node and also broadcasting messages to all connected nodes.

### SeedSocketCommunication
This socket communication module is used by Seed nodes. The propose of the SeedSocketCommunication module is to provide new nodes a list of available nodes in the network which can further on be used to calculate the nodes adjacent neighbor and connect to that node. The second purpose is to keep track of the Beez nodes health status. In a separate thread, the SeedSocketCommunication module asks the connected Beez nodes about their current health status. This metric is being calculated based on the free disk space and the upload and download performance of the node. The results are being saved in the SeedSocketCommunication module. The third purpose of the SeedSocketCommunication module is to handle the communication for the digital asset manager. It therefore implements the methods required to push digital asset chunks to specific Beez nodes and keeps track of whether the Beez nodes could successfully store the chunks or not. Furthermore it also implements the methods to receive digital asset chunks back from Beez nodes.

### SocketCommunication
The SocketCommunication module is used by Beez nodes and implements all the methods required to handle transactions on the blockchain as well as the logic to handle messages from the Seed node which are about saving or receiving digital asset chunks.

## Node API
The Node API is used for external communication with the blockchain. A typical usecase for such a communication is a BeezY, the wallet for the Beez blockchain.
The API provides the endpoints to get information like the current blockchain state, the current node connections etc. Furthermore it also provides endpoints to send transactions to the blockchain or upload/download digital assets.

### BaseNodeApi
Base class which handles the connection from the API to the Node instance.

### Seed nodeApi
The Seed nodeApi is used by the Seed node and implementes endpoints required for digital asset management like uploading and downloading digital assets.
Furthermore, it implements an endpoint to get information about the current cluster health status based on the metrics stored on the SeedSocketCommunication module.

### NodeApi
The NodeApi is used by the Beez nodes and implements informational endpoints on the one hand, such as getting the current blockchain state, the current transactions in the transaction pool, etc. On the other hand, it also implements endpoints to send transactions to the blockchain.


# How does the blockchain work
The following paragraphs describe how the Beez blockchain network components work together.

### Startup a network

#### Starting a Seed node
When starting a Node, whether this is a Seed node or a Beez node, one has to decide which Node to start. This can be done via an env variable which defines the type of the node to start. As the central part of peer discovery is the Seed node and the Seed node is the first node Beez nodes connect to, the Seed node has to be startet first. In the current version of the blockchain, there must only be one Seed node in the network.

#### Starting a Beez node
Once the Seed node is started on a defined IP and port, for both the socket communication and the node API, both of them need a different port to serve on, the Seed node keeps track of all nodes in the network. Once a Beez node joins the network, it automatically connects to the Seed node of the network. The IP and port of the Seed node the Beez node has to connect to, will also be defined using an env variable. If the connection to the Seed node is established, the Seed node adds the just connected node to its list of available nodes and from now on also monitors its health status (dedicated thread in SeedSocketCommunication module). 

### Peer discovery - Connecting to the adjacent neighbors
Upon connection from a Beez node to the Seed node, the Seed node answers the connecting Beez node with a list of all connected nodes. Once the Beez node gets the list of network nodes from the Seed node, the Beez node calculates its adjacent neighbor. The adjacent neighbor is the node prior to this node in the list of nodes coming from the Seed node. This list is sorted, so every Beez node gets the available nodes in the same order. If the node receiving the list of available nodes is the very first node in this list, it connects to the last node in the list. If there is no other node other then the requesting node available, there is no adjacent neighbor available the Beez node could connect to. To make sure every node is always connected to the corrent neighbor, everytime a new node joins the network, all nodes get the list of available nodes again. If the adjacent neighbor changed for one of the nodes previously connected to the network, it also reconnects to the new, correct adjacent neihbor.

### Handle node outages and reconnect and backup digital asset chunks
If a node outage occurs, the Seed node will notice this via the healthchecks it sends to all connected nodes. Once a node does not respond to the healthchecks for a predefined amount of time, the Seed node removes the node of the list of available nodes and re-broadcasts the new list if available peers to all connected nodes and thus triggers a reconnection of all nodes to their new, correct adjacent neighbors.

### Beez Addresses
Every member of the Beez blockchain is going to be identified based on a beez address. The address is a transformation of a Ed25519 public key. In detail it is constructed the following way: `bzx` + first 42 digits of the hash of the public key. The node API provides an endpoint which is used to register new addresses. The node receiving the request is storing a mapping between the address and the public key and also broadcasts this mapping to all connected nodes. This way every is going to get all address mappings in the network. If a node requires the public key of a certain address later on, for example to validate a signature, it looks up the public key based on the address and can then use it for its validation.

### Sending transactions
To send a transaction to the beez blockchain, the node API also provides a corresponding endpoint. Once a transaction occurs on a Beez node, it checks if the transaction is valid, the funds are covered by the sender, the signature is valid and whether the transaction is already in the local transaction pool or even part of the blockchain. If the transaction is new and valid, the Beez node will add the transaction to its local transaction pool and broadcasts it to its connections.

### Proof of stake
The beez blockchain implements a proof of stake consensus mechanism. Each node is able to stake a certain amount of token, its stake. Everytime a new block is required, the nodes calculate the next forger. The algorithm therefore creates lots. A lot is simply a hash based on the latest block and the nodes public key. For every staked token, a lot is being generated for that node using hash chaining. Once all lots for all stakers are generated, the lot with the least amount of offset compared to the last block hash is chosen as winner lot. The node to which the winner lot corresonds to is the next forger and thus allowed to forge the next block.

### Forging a new block
Currently, blocks are being forged if a predefined number of transactions are waiting for a new block. This means there are a certain amount of transactions waiting in the transaction pool. If that's the case, the node calculates the next forging node and itself is the forging node creates a new block and broadcasts it to the network. The nodes receiving the new block again check if the block is valid, signature is valid, transactions in the block are valid and if the forger is valid. If so, the block is being appended to the blockchain and the block is further broadcasted to the network.

### Uploading digital assets
To upload a digital asset, the Seed node API provides a corresponding endpoint. The endpoint expects two parameters, first of all the digital asset to store and secondly a corresponding upload transaction. If these parameters are provided, the Seed node splits the digital asset into a predefined number of chunks depending on the size of the digital asset. If the digital asset is split up, the Seed node pushes the chunks to the connected Beez nodes. Currently the Beez node selection to save the digitial assets on is done round robin, later on it should be based on the nodes health metric as well.

When the Beez nodes receive a new asset chunk, they save the chunk to its local memory and reply to the Seed node with an acknowledge message. Furthermore, the nodes backup the chunk to their neighbor node. Once the Seed node got the acknowledgement for all chunks, the digital asset is successfully uploaded. The Seed node keeps track of the uploaded digital assets locally by storing the information about the digital asset and which Beez nodes hold which chunks.

The last step is to broadcast the upload transaction to the blockchain and return a success message to the sending user.

### Downloading digital assets
Again, the Seed node provides a corresponding API endpoint to download digital assets. The endpoint expects to get the name of the digital asset to download. If that parameter is given, the Seed node can lookup the meta information about that digital asset, knows which nodes store the chunks and send a chunk request to the nodes. Once the Beez nodes receive the chunk request, they load the digital asset chunk and send them back to the Seed node. If the Seed node received all chunks, it concatenates them in the correct order to reassemble the original digital asset and returns it. Additionally, a download transaction is being broadcasted to the network.

### Digital assets on node failures
If a node failure occurs and the nodes receive the updated list of available nodes from the Seed node, they notice if their neighbor node which stores a backup of their digital asset chunks are down. Therefore, these nodes backup all their digital asset chunks on their new neighbor node. If on the other hand, a node notices, that the node which this node backs up is dead, it considers its own backups as primary chunks and backs up the chunks on its own neighbor node. This way all chunks are stored redundantly again.