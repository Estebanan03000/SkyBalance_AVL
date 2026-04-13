"""Service helpers for computing tree metrics and mass-cancellation statistics."""


class Metrics_Service:
    """Expose real-time metrics for the active flight tree."""

    def __init__(self, flight_service):
        """Store the shared flight service and initialize cancellation tracking."""
        self._Service = flight_service
        self._cancelations = []

    def LeavesCounter(self):
        """Count how many leaf nodes currently exist in the tree."""
        flights = self._Service.get_all_flights()
        if not flights:
            return 0

        leaves = 0
        for flight in flights:
            if flight.getLeftChild() is None and flight.getRightChild() is None:
                leaves += 1
        return leaves

    def RotationCounter(self):
        """Return rotation counters only when AVL balancing is active."""
        if self._Service._mode == "Stress":
            return None
        return self._Service._tree.getRotationCounts()

    def TreeHeight(self):
        """Return the height of the current tree."""
        root = self._Service._tree._root
        return self._Service._tree.getHeightNode(root)

    def massiveCancelation(self, node):
        """Delete an entire subtree and record the event if it is large enough."""
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
        """Collect all nodes under the given subtree in depth-first order."""
        if currentNode is None:
            return

        if currentNode.getLeftChild() is not None:
            self._getChilds(currentNode.getLeftChild(), result)

        if currentNode.getRightChild() is not None:
            self._getChilds(currentNode.getRightChild(), result)

        result.append(currentNode)

    def total_flights_canceled_massively(self):
        """Return the cumulative number of flights removed by mass cancellations."""
        return sum(self._cancelations)

    def getRealTimeMetrics(self):
        """Return the current metrics dictionary consumed by the frontend."""
        return {
            "mode": self._Service._mode,
            "leaves": self.LeavesCounter(),
            "height": self.TreeHeight(),
            "rotations": self.RotationCounter(),
            "massive_cancelations": self.total_flights_canceled_massively(),
        }

