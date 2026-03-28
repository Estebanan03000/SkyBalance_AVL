#Metrics_Service is the service in charge to give in real time the metrics related to the tree, like deep traversals
#Amount of leaves, etc.

class Metrics_Service:

    def __init__(self, flight_service):
        self._Service = flight_service

    #Method that counts and show the amount of nodes type leaf that exist on the tree
    def LeavesCounter(self):
        leaves = 0
        flights = self._Service.get_all_flights()

        for flight in flights:
            if flight.getLeftChild() is None and flight.getRightChild() is None:
                leaves += 1
        
        return leaves

    def RotationCounter(self):
        rotations = self._service._tree.getRotationCounts()
        print("Rotation counts:")
        for rot_type, count in rotations.items():
            print(f"{rot_type}: {count}")
        return rotations


