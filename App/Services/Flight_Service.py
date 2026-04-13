"""Core service layer for managing flights and switching tree strategies."""

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

    def __init__(self, mode="Normal"):
        """
        Initializes the Flight_Service with an empty AVL tree and an empty Stack to undo operations
        """
        self._history = Stack()
        self._mode = mode
        self._max_depth = None  # It is configured before loading the JSON
        self._versions = {}
        # Initialize the tree according to the mode
        if mode == "Stress":
            self._tree = BST()
        else:
            self._tree = AVL()

    def _clone_flight(self, node):
        return Flight(
            id=node.getValue(),
            origin=node.getOrigin(),
            destiny=node.getDestiny(),
            departureTime=node.getDepartureTime(),
            basePrice=node.getBasePrice(),
            finalPrice=node.getFinalPrice(),
            passengers=node.getPassengers(),
            promotion=node.getPromotion(),
            alert=node.getAlert(),
        )

    def _clone_tree_structure(self, source_tree):
        """
        Creates an exact copy of the tree structure (nodes and links) 
        without reinserting. This preserves the current layout.
        
        Returns a tuple: (new_tree_instance, copied_root)
        """
        if source_tree.getRoot() is None:
            return None
        
        def clone_node(node):
            """Recursively clone a node and its children"""
            if node is None:
                return None
            
            # Create new Flight with same data
            cloned_flight = self._clone_flight(node)
            
            # Recursively clone children
            left_child = clone_node(node.getLeftChild())
            right_child = clone_node(node.getRightChild())
            
            # Set parent-child relationships
            if left_child:
                cloned_flight.setLeftChild(left_child)
                left_child.setParent(cloned_flight)
            
            if right_child:
                cloned_flight.setRightChild(right_child)
                right_child.setParent(cloned_flight)
            
            return cloned_flight
        
        # Clone the entire structure
        return clone_node(source_tree.getRoot())

    def set_mode(self, mode):
        """
        Change the tree mode between Stress (BST) and Global Balance (AVL).
        Preserves the exact tree structure when switching.
        Only degrades/rebalances if explicitly requested or on modifications.
        """
        if self._mode == mode:
            # Already in the desired mode
            return
        
        # Clone the current tree structure exactly (no reinsertion, no rebalancing)
        root_clone = self._clone_tree_structure(self._tree)
        
        if mode == "Stress":
            # Switch to BST (Stress mode) - keeping exact structure
            self._tree = BST()
            self._tree._root = root_clone
        else:
            # Switch to AVL (Normal or Global Balance mode) - keeping exact structure
            self._tree = AVL()
            self._tree._root = root_clone
            
            # Apply depth penalty if set
            if self._max_depth:
                self.applyDepthPenalty()
        
        # Update the mode
        self._mode = mode
        # Clear history when switching modes to avoid confusion
        self._history = Stack()

    def get_visualization_tree(self, view_mode=None):
        """Return a tree instance for visualization without mutating the active tree."""
        normalized_view = (view_mode or "ACTIVE").upper()

        if normalized_view == "ACTIVE":
            return self._tree

        if normalized_view == "AVL":
            tree = AVL()
            source_nodes = self.get_all_flights() or []
            for node in source_nodes:
                tree.insert(self._clone_flight(node))
            return tree

        if normalized_view == "BST":
            tree = BST()
            source_nodes = self.get_all_flights() or []
            for node in source_nodes:
                tree.insert(self._clone_flight(node))
            return tree

        raise ValueError(f"Unsupported visualization mode: {view_mode}")

    def global_rebalance(self):
        """
        Performs a global rebalance of the tree.
        Converts from BST to AVL and rebalances all nodes.
        Each node is checked for balance, and the tree is restructured as needed.
        
        Returns:
            dict: Report with initial and final tree statistics
        """
        # Get current tree info before rebalance
        initial_flights = self.get_all_flights() or []
        initial_depth = self._tree.getDepth()
        
        # Convert current tree to AVL (which auto-rebalances on insert)
        self._tree = AVL()
        
        # Re-insert all flights - AVL will rebalance automatically
        for flight in initial_flights:
            # Create new Flight instance to avoid pointer issues
            new_flight = Flight(
                id=flight.getValue(),
                origin=flight.getOrigin(),
                destiny=flight.getDestiny(),
                departureTime=flight.getDepartureTime(),
                basePrice=flight.getBasePrice(),
                finalPrice=flight.getFinalPrice(),
                passengers=flight.getPassengers(),
                promotion=flight.getPromotion(),
                alert=flight.getAlert()
            )
            self._tree.insert(new_flight)
        
        # Re-apply depth penalty if configured
        if self._max_depth:
            self.applyDepthPenalty()
        
        # Get new tree info after rebalance
        final_depth = self._tree.getDepth()
        
        # Update mode to Global Balance
        self._mode = "Global Balance"
        
        return {
            "rebalanced": True,
            "initial_depth": initial_depth,
            "final_depth": final_depth,
            "flights_rebalanced": len(initial_flights),
            "tree_type": "AVL"
        }
    
    def verify_all_balances(self):
        """
        Verifies the balance factor of each node in the current tree.
        Returns a detailed report of nodes that are unbalanced.
        
        Returns:
            dict: Report with balance information for all nodes
        """
        all_flights = self.get_all_flights() or []
        unbalanced_nodes = []
        balanced_nodes = []
        
        for flight in all_flights:
            node = self._tree.search(flight.getValue())
            if node is None:
                continue
            
            # Calculate balance factor
            left_height = self._tree.getHeightNode(node.getLeftChild()) if node.getLeftChild() else 0
            right_height = self._tree.getHeightNode(node.getRightChild()) if node.getRightChild() else 0
            balance_factor = left_height - right_height
            
            node_info = {
                "id": node.getValue(),
                "balance_factor": balance_factor,
                "left_height": left_height,
                "right_height": right_height,
                "depth": self._tree.getNodeDepth(node),
                "is_balanced": abs(balance_factor) <= 1
            }
            
            if abs(balance_factor) > 1:
                unbalanced_nodes.append(node_info)
            else:
                balanced_nodes.append(node_info)
        
        return {
            "mode": self._mode,
            "total_nodes": len(all_flights),
            "balanced_nodes": len(balanced_nodes),
            "unbalanced_nodes": len(unbalanced_nodes),
            "unbalanced_details": unbalanced_nodes,
            "balanced_details": balanced_nodes,
            "tree_depth": self._tree.getDepth()
        }

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
    def _normalize_id_value(self, raw_id):
        if raw_id is None:
            return None
        text = str(raw_id).strip()
        if not text:
            return None
        if text.isdigit():
            return int(text)
        digits = ""
        for char in text:
            if char.isdigit():
                digits += char
        return int(digits) if digits else None

    def _safe_search_by_id(self, flight_id):
        """Search node tolerant to legacy trees with mixed id types (str/int)."""
        try:
            return self._tree.search(flight_id)
        except Exception:
            pass

        target = self._normalize_id_value(flight_id)
        flights = self.get_all_flights() or []
        for node in flights:
            if self._normalize_id_value(node.getValue()) == target:
                return node
        return None

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
        return self._safe_search_by_id(flight_id)

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

        # Delete using the real node value to avoid int/str mismatches.
        self._tree.delete(flight.getValue())
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
    def save_version(self, name: str):
        """Saves a complete snapshot of the current tree with the given name."""
        if not name or not name.strip():
            raise Exception("Version name cannot be empty")
        snapshot = self._tree.serialize_to_dict()
        self._versions[name] = {
            "snapshot": snapshot,
            "max_depth": self._max_depth
        }

    def restore_version(self, name: str):
        """Restores the tree to the state saved under the given name."""
        if name not in self._versions:
            raise Exception(f"Version '{name}' does not exist")
        version = self._versions[name]
        self._tree = AVL()
        if version["snapshot"] is not None:
            self._tree.buildFromTopology(version["snapshot"])
        self._max_depth = version["max_depth"]
        self.applyDepthPenalty()
        self._history = Stack()

    def list_versions(self):
        """Returns the names of all saved versions."""
        return list(self._versions.keys())
    
    #Method to get the different kinds of tree traversals for the current tree (AVL or BST on stress mode)
    def get_traversal(self, traversal_type):
        if traversal_type == "inorder":
            return [n.getValue() for n in (self._tree.inOrderTraversal() or [])]

        elif traversal_type == "preorder":
            return [n.getValue() for n in (self._tree.preOrderTraversal() or [])]

        elif traversal_type == "postorder":
            return [n.getValue() for n in (self._tree.posOrderTraversal() or [])]

        elif traversal_type == "levelorder":
            nodes = self._tree.breadthFirstSearch() or []
            return [n.getValue() if hasattr(n, "getValue") else n for n in nodes]
        
        else:
            raise Exception("Invalid traversal type")
