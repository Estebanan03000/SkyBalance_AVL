from App.Models.Flight import Flight
from App.Models.AVL import AVL
from App.Models.Stack import Stack
from App.Models.BST import BST
from App.Models.Queue import Queue
import json


class Flight_Service:
    """
    Service class responsible for performing CRUD operations on Flight objects
    using an AVL Tree as the underlying storage structure.

    The AVL tree keeps the flights automatically balanced based on the flight ID
    (used as the key for ordering). This ensures efficient operations with
    O(log n) complexity for insertion, search, and deletion.

    Responsibilities of this class:
    - Insert new flights into the AVL tree
    - Retrieve a flight by its ID
    - Retrieve all flights stored in the AVL tree
    - Update flight attributes
    - Remove flights from the AVL tree
    """

    def __init__(self, mode="Global Balance"):
        """
        Initializes the Flight_Service with an empty AVL tree and an empty Stack to undo operations
        """
        self._history = Stack()
        self._mode = mode
        self._max_depth = None  # It is configured before loading the JSON
        # Initialize the tree according to the mode
        if mode == "Stress":
            self._tree = BST()
        else:
            self._tree = AVL()

    def set_mode(self, mode):
        if mode == "Stress":
            self._tree = BST()
        else:
            # Get all flights in the current tree before changing
            old_flights = self.get_all_flights() or []
            self._tree = AVL()
            for flight in old_flights:
                self._tree.insert(flight)

    # CREATE
    def create_flight(self, flight: Flight):
        """
        Inserts a new Flight object into the AVL tree.

        The AVL tree will automatically handle balancing after insertion.

        Parameters
        ----------
        flight : Flight
            The Flight object to be inserted into the tree.
        """
        self._tree.insert(flight)
        self._history.push(("delete", flight.getValue()))
        self.applyDepthPenalty()  # the new flight could cause depth changes, so we recalculate penalties after each insertion

    # READ (single flight)
    def get_flight(self, flight_id):
        """
        Retrieves a flight from the AVL tree using its unique ID.

        Parameters
        ----------
        flight_id : int
            Unique identifier of the flight.

        Returns
        -------
        Flight or None
            The Flight object if found, otherwise None.
        """
        return self._tree.search(flight_id)

    # READ (all flights)
    def get_all_flights(self):
        """
        Retrieves all flights stored in the AVL tree using an inorder traversal.

        Inorder traversal returns the flights sorted by their ID.

        Returns
        -------
        list[Flight]
            A list containing all Flight objects in sorted order.
        """
        return self._tree.inOrderTraversal()

    # UPDATE
    def update_flight(self, flight_id, **kwargs):

        flight = self.get_flight(flight_id)

        if flight is None:
            raise Exception("Flight not found")

        # Save only the fields that are being modified for undo history.
        old_values = {}

        if "origin" in kwargs:
            old_values["origin"] = flight.getOrigin()
            flight.setOrigin(kwargs["origin"])

        if "destiny" in kwargs:
            old_values["destiny"] = flight.getDestiny()
            flight.setDestiny(kwargs["destiny"])

        if "basePrice" in kwargs:
            old_values["basePrice"] = flight.getBasePrice()
            flight.setBasePrice(kwargs["basePrice"])

        if "finalPrice" in kwargs:
            old_values["finalPrice"] = flight.getFinalPrice()
            flight.setFinalPrice(kwargs["finalPrice"])

        if "passengers" in kwargs:
            old_values["passengers"] = flight.getPassengers()
            flight.setPassengers(kwargs["passengers"])

        # Save to the stack ONLY if there were changes
        if old_values:
            self._history.push(("update", flight_id, old_values))

    # DELETE
    def delete_flight(self, flight_id):
        """
        Removes a flight from the AVL tree.

        Parameters
        ----------
        flight_id : int
            ID of the flight to remove.

        Raises
        ------
        Exception
            If the flight does not exist.
        """
        flight = self.get_flight(flight_id)

        if flight is None:
            raise Exception("Flight not found")

        self._tree.delete(flight_id)
        self._history.push(("insert", flight))

    def undo(self):
        while not self._history.is_empty():
            action = self._history.pop()
            action_type = action[0] if isinstance(action, tuple) and len(action) > 0 else None

            if action_type == "delete":
                # Stored as ("delete", flight_id) to undo an insertion.
                flight_id = action[1] if len(action) > 1 else None
                if flight_id is None:
                    continue
                self._tree.delete(flight_id)
                return ("delete", flight_id)

            if action_type == "insert":
                # Stored as ("insert", flight_obj) to undo a deletion.
                flight = action[1] if len(action) > 1 else None
                if flight is None or not hasattr(flight, "getValue"):
                    continue
                self._tree.insert(flight)
                return ("insert", flight.getValue())

            if action_type == "update":
                # Stored as ("update", flight_id, old_values).
                if len(action) < 3:
                    continue
                flight_id, old_values = action[1], action[2]
                flight = self.get_flight(flight_id)
                if flight:
                    if "origin" in old_values:
                        flight.setOrigin(old_values["origin"])
                    if "destiny" in old_values:
                        flight.setDestiny(old_values["destiny"])
                    if "basePrice" in old_values:
                        flight.setBasePrice(old_values["basePrice"])
                    if "finalPrice" in old_values:
                        flight.setFinalPrice(old_values["finalPrice"])
                    if "passengers" in old_values:
                        flight.setPassengers(old_values["passengers"])
                return ("update", flight_id)

        raise Exception("No hay operaciones válidas para deshacer")

    def multi_inserts(self, flights_list):
        """
        Inserts multiple flights into AVL and returns report list (Flask-friendly)
        """
        report_list = []
        queue = Queue()

        # Queue all incoming flights
        for flight in flights_list:
            queue.enqueue(flight)

        # Process the queue
        while not queue.is_empty():
            flight = queue.dequeue()
            report = self._insert_with_report(flight)
            report_list.append(report)
            self._history.push(("delete", flight.getValue()))

        return report_list

    def _insert_with_report(self, flight):
        """
        Inserts a flight into the AVL tree and generates a report
        based on rotation count changes.
        """

        # 1. Save rotation counters BEFORE insertion (only AVL has them)
        has_rotations = hasattr(self._tree, "getRotationCounts")
        before = self._tree.getRotationCounts().copy() if has_rotations else {}

        # 2. Insert into AVL
        self._tree.insert(flight)

        # 3. Save rotation counters AFTER insertion
        after = self._tree.getRotationCounts() if has_rotations else {}

        # 4. Compare counters to detect if a conflict occurred
        rotation_detected = None

        for rotation_type in ["LL", "RR", "LR", "RL"]:
            if after.get(rotation_type, 0) > before.get(rotation_type, 0):
                rotation_detected = rotation_type
                break

        # 5. Build user-friendly report
        if rotation_detected:
            return {
                "status": "conflict",
                "flight_id": flight.getValue(),
                "origin": flight.getOrigin(),
                "destiny": flight.getDestiny(),
                "conflict_type": rotation_detected,
                "rotation_applied": rotation_detected,
            }
        else:
            return {
                "status": "ok",
                "flight_id": flight.getValue(),
                "origin": flight.getOrigin(),
                "destiny": flight.getDestiny(),
            }
        
    def Auditory_System(self, mode): 
        if mode == "Stress": 
            return self.get_all_flights() 
        return []

    def Auditory_report(self, nodes):
        """
        Generate a detailed report of each node of the three (AVL or BST on stress mode), 
        showing real height, balance factor and the AVL status
        """
        report = []

        for node in nodes:
            # RealHeight calculate in a recursive way 
            realHeight = self._tree.getHeightNode(node)

            # Balance factor calculation
            if isinstance(self._tree, AVL):
                bf = self._tree.getBalanceFactor(node)
            else:
                leftHeight = self._tree.getHeightNode(node.getLeftChild())
                rightHeight = self._tree.getHeightNode(node.getRightChild())
                bf = leftHeight - rightHeight

            # Determinate AVL status
            status = "OK" if abs(bf) <= 1 else "Inconsistente (balance fuera de rango)"

            # Append info of the node to the report
            report.append({
                "Node": node.getValue(),      # ID of the flight
                "Real Height": realHeight,
                "Balance Factor": bf,
                "AVL Status": status,
            })

        return report


    # ==================== EXPORT ====================
    # Method for saving the complete tree as an JSON file.

    def export_tree_to_json(self, filename):
        """
        Exports the entire tree to a JSON file.

        Saves the hierarchical tree structure, including all properties
        for each flight, altitudes, and balance factors (if AVL).

        Parameters:

        filename: Name or path of the file where the JSON will be saved

        Returns:

        bool: True if the export was successful, False if there was an error
        """
        try:
            tree_data = self._tree.serialize_to_dict()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(tree_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting tree: {str(e)}")
            return False

    def applyDepthPenalty(self):
        if self._max_depth is None:
            return

        flights = self.get_all_flights()

        if not flights:  # Avoid processing if there are no flights in the tree
            return

        for flight in flights:
            depth = self._tree.getNodeDepth(flight)

            if depth > self._max_depth:
                flight.setIsCritical(True)
                flight.setFinalPrice(flight.getBasePrice() * 1.25)
            else:
                flight.setIsCritical(False)
                flight.setFinalPrice(flight.getBasePrice())

    def setMaxDepth(self, depth):
        self._max_depth = depth
        self.applyDepthPenalty()  # Recalulate penalties immediately after setting max depth

    def _calculateProfitability(self, flight):
        # Base profitability: passengers multiplied by final price
        profitability = flight.getPassengers() * flight.getFinalPrice()

        # If the flight has an active promotion, subtract it from profitability
        if flight.getPromotion() > 0:
            profitability -= flight.getPromotion()

        # If the node is critical (depth penalty active), subtract the 25% surcharge
        if flight.getIsCritical():
            profitability -= (flight.getFinalPrice() - flight.getBasePrice()) * flight.getPassengers()

        return profitability

    def _findLowestProfitability(self):
        # Get all flights via inorder traversal
        flights = self.get_all_flights()
        if not flights:
            return None

        lowest = None
        for flight in flights:
            # First iteration: set the first flight as the current minimum
            if lowest is None:
                lowest = flight
                continue

            current_profit = self._calculateProfitability(flight)
            lowest_profit = self._calculateProfitability(lowest)

            # Primary criterion: lower profitability wins
            if current_profit < lowest_profit:
                lowest = flight
            elif current_profit == lowest_profit:
                current_depth = self._tree.getNodeDepth(flight)
                lowest_depth = self._tree.getNodeDepth(lowest)

                # Secondary criterion: if profitability is equal, take the deepest node
                if current_depth > lowest_depth:
                    lowest = flight
                elif current_depth == lowest_depth:
                    # Tertiary criterion: if depth is also equal, take the one with the largest ID
                    if flight.getValue() > lowest.getValue():
                        lowest = flight

        return lowest

    def _collectSubtree(self, flight, ids):
        # Base case: if the node is None, stop recursion
        if flight is None:
            return
        # Add the current node's ID to the list
        ids.append(flight.getValue())
        # Recursively collect IDs from the left subtree
        self._collectSubtree(flight.getLeftChild(), ids)
        # Recursively collect IDs from the right subtree
        self._collectSubtree(flight.getRightChild(), ids)

    def _deleteSubtree(self, flight):
        # Collect all IDs in the subtree BEFORE deleting
        # This is necessary because AVL rebalancing after each deletion
        # may move nodes around, making references unreliable
        ids = []
        self._collectSubtree(flight, ids)

        # Delete each node by ID — AVL rebalances automatically after each deletion
        for flight_id in ids:
            node = self._tree.search(flight_id)
            if node:
                self._tree.delete(flight_id)

        # Recalculate depth penalties since tree structure has changed
        self.applyDepthPenalty()

    def deleteLowestProfitability(self):
        # Find the least profitable node using all tiebreaker criteria
        target = self._findLowestProfitability()

        if target is None:
            raise Exception("The tree is empty")

        # Save the ID before deletion to return it to the caller
        target_id = target.getValue()

        # Delete the target node and its entire subtree
        self._deleteSubtree(target)

        # Return the deleted flight ID so the frontend knows which one was removed
        return target_id
