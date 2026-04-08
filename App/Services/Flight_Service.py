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
            old_flights = self.get_all_flights()
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

        # 🔹 Guardar valores anteriores SOLO de los campos que se van a modificar
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
        if self._history.is_empty():
            raise Exception("The history is empty")

        action = self._history.pop()

        if action[0] == "delete":
            # Re-insert the flight
            self._tree.insert(action[1])
        elif action[0] == "insert":
            # Delete the flight (undo creation)
            self._tree.delete(action[1].getValue())
        elif action[0] == "update":
            # Revert the old values
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

        # 1. Save rotation counters BEFORE insertion
        before = self._tree.getRotationCounts().copy()

        # 2. Insert into AVL
        self._tree.insert(flight)

        # 3. Save rotation counters AFTER insertion
        after = self._tree.getRotationCounts()

        # 4. Compare counters to detect if a conflict occurred
        rotation_detected = None

        for rotation_type in ["LL", "RR", "LR", "RL"]:
            if after[rotation_type] > before[rotation_type]:
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

    # ==================== EXPORT ====================
    # Method to save the entire tree to a JSON file

    def export_tree_to_json(self, filename):
        """
        Exporta el árbol completo a un archivo JSON.
        Guarda la estructura jerárquica del árbol incluyendo todas las propiedades
        de cada vuelo, alturas y factores de balance (si es AVL).

        Parámetros:
            filename: Nombre o ruta del archivo donde guardar el JSON

        Retorna:
            bool: True si la exportación fue exitosa, False si hay error
        """
        try:
            # Serialize the tree to a dictionary
            tree_data = self._tree.serialize_to_dict()

            # Save to JSON file with readable format (indent=2)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(tree_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error al exportar árbol: {str(e)}")
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
