from Models.Flight import Flight
from Models.AVL import AVL
from Models.Stack import Stack
from Models.BST import BST

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

    def __init__(self, mode = "Global Balance"):
        """
        Initializes the Flight_Service with an empty AVL tree and an empty Stack to undo operations
        """
        self._history = Stack()
        self._mode = mode

    def set_mode(self, mode):
        if mode == "Stress":
            self._tree = BST()
        else:
            old_flights = BST.get_all_flights()
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
        return self._search(self._tree.getRoot(), flight_id)

    def _search(self, node, flight_id):
        """
        Recursively searches for a flight in the AVL tree.

        Parameters
        ----------
        node : Flight
            Current node being evaluated.
        flight_id : int
            ID of the flight being searched.

        Returns
        -------
        Flight or None
            The Flight object if found, otherwise None.
        """
        if node is None:
            return None

        if node.getValue() == flight_id:
            return node

        if flight_id < node.getValue():
            return self._search(node.getLeftChild(), flight_id)

        return self._search(node.getRightChild(), flight_id)

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
        flights = []
        self._inorder(self._tree.getRoot(), flights)
        return flights

    def _inorder(self, node, flights):
        """
        Performs an inorder traversal of the AVL tree.

        Parameters
        ----------
        node : Flight
            Current node being visited.
        flights : list
            List used to collect Flight objects during traversal.
        """
        if node is None:
            return

        self._inorder(node.getLeftChild(), flights)
        flights.append(node)
        self._inorder(node.getRightChild(), flights)

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

        # 🔹 Guardar en la pila SOLO si hubo cambios
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
            print("No hay operaciones para deshacer")
            return

        action = self._history.pop()

        if action[0] == "delete":
            self._tree.delete(action[1])

        elif action[0] == "insert":
            self._tree.insert(action[1])

        elif action[0] == "update":
            flight = self.get_flight(action[1])
            flight.setFinalPrice(action[2])