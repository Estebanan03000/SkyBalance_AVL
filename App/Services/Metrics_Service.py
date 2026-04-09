#Metrics_Service is the service in charge to give in real time the metrics related to the tree, like deep traversals
#Amount of leaves, etc.


class Metrics_Service:

    """
    A service class that provides real-time metrics and operations
    related to the flight tree maintained by Flight_Service.

    Attributes
    ----------
    _Service : Flight_Service
        The flight service containing the AVL or BST tree.
    _cancelations : list[int]
        Tracks the number of flights canceled in massive cancelation events.
    """

    def __init__(self, flight_service):
        self._Service = flight_service
        self._cancelations = []

    #Method that counts and show the amount of nodes type leaf that exist on the tree
    #Returns: int (number of leaf nodes)
    def LeavesCounter(self):
        leaves = 0
        flights = self._Service.get_all_flights()

        for flight in flights:
            if flight.getLeftChild() is None and flight.getRightChild() is None:
                leaves += 1
        
        return leaves
    
    #Retrieves the count of rotations that have occurred in the tree.
    #Return Retrieves the count of rotations that have occurred in the tree.
    def RotationCounter(self):
        rotations = self._Service._tree.getRotationCounts()
        print("Rotation counts:")
        for rot_type, count in rotations.items():
            print(f"{rot_type}: {count}")
        return rotations
    
    #Calculate the tree height from the root node
    def TreeHeight(self):
        root = self._Service._tree._root
        return self._Service._tree.getHeightNode(root)

    """
    Deletes a node and all of its descendant flights from the tree.
    Tracks the event if 4 or more flights were canceled.

    Parameters
        ----------
        node : Node
            The node from which to start the mass cancelation.

    Returns
        -------
        int
            Total number of flights canceled in this operation.

    Raises
        ------
        Exception
            If the node does not exist.
    
    """
    def massiveCancelation(self, node):
        if node is None:
            raise Exception("Node to delete doesn't exist on the tree")
        
        result = []
        self._getChilds(node, result)

        for flight in result:
            self._Service.delete_flight(flight.getValue())

        deleted_count = len(result)

        if deleted_count >= 4:
            self._cancelations.append(deleted_count)

        return deleted_count    

    """
        Recursively collects all child nodes of a given node.

        Parameters
        ----------
        currentNode : Node
            Node whose descendants are to be collected.
        result : list
            List to store collected nodes.
    """
    def _getChilds(self, currentNode, result):
        if currentNode is None:
            return

        if currentNode.getLeftChild() is not None:
            self._getChilds(currentNode.getLeftChild(), result)

        if currentNode.getRightChild() is not None:
            self._getChilds(currentNode.getRightChild(), result)

        result.append(currentNode)

    """
        Recursively collects all child nodes of a given node.

        Parameters
        ----------
        currentNode : Node
            Node whose descendants are to be collected.
        result : list
            List to store collected nodes.
    """

    def total_flights_canceled_massively(self):
        return sum(self._cancelations)
    
    """
        Returns a dictionary with key metrics of the tree for real-time analysis.

        Returns
        -------
        dict
            Dictionary containing:
            - 'leaves': Number of leaf nodes
            - 'height': Height of the tree
            - 'rotations': Dictionary of rotations
            - 'massive_cancelations': Total massive flight cancellations
    """

            """
        Returns a dictionary with key metrics of the tree for real-time analysis.

        Returns
        -------
        dict
            Dictionary containing:
            - 'leaves': Number of leaf nodes
            - 'height': Height of the tree
            - 'rotations': Dictionary of rotations
            - 'massive_cancelations': Total massive flight cancellations
        """

    def getRealTimeMetrics(self):
        return {
            "leaves": self.LeavesCounter(),
            "height": self.TreeHeight(),
            "rotations": self.RotationCounter(),
            "massive_cancelations": self.total_flights_canceled_massively()
        }

        



