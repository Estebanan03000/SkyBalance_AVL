# Metrics_Service provides real-time metrics for the current flight tree.
# It calculates leaf count, tree height, rotation totals, and massive cancellation totals.


class Metrics_Service:

    def __init__(self, flight_service):
        self._Service = flight_service
        self._cancelations = []

    def LeavesCounter(self):
        """Return the number of leaf nodes in the current tree."""
        leaves = 0
        flights = self._Service.get_all_flights()

        for flight in flights:
            if flight.getLeftChild() is None and flight.getRightChild() is None:
                leaves += 1

        return leaves

    def RotationCounter(self):
        """Return the rotation counts from the underlying tree implementation."""
        rotations = self._Service._tree.getRotationCounts()
        print("Rotation counts:")
        for rot_type, count in rotations.items():
            print(f"{rot_type}: {count}")
        return rotations

    def TreeHeight(self):
        """Return the height of the current tree."""
        root = self._Service._tree._root
        return self._Service._tree.getHeightNode(root)

    def massiveCancelation(self, node):
        """Delete the subtree rooted at the given node and track massive cancellations."""
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

    def _getChilds(self, currentNode, result):
        """Collect all nodes in a subtree in depth-first order."""
        if currentNode is None:
            return

        if currentNode.getLeftChild() is not None:
            self._getChilds(currentNode.getLeftChild(), result)

        if currentNode.getRightChild() is not None:
            self._getChilds(currentNode.getRightChild(), result)

        result.append(currentNode)

    def total_flights_canceled_massively(self):
        """Return the cumulative count of massive cancellation events."""
        return sum(self._cancelations)

    def getRealTimeMetrics(self):
        """Return a dictionary with the current tree metrics for the frontend."""
        return {
            "leaves": self.LeavesCounter(),
            "height": self.TreeHeight(),
            "rotations": self.RotationCounter(),
            "massive_cancelations": self.total_flights_canceled_massively(),
        }

        



