from App.Models.Flight import Flight
from App.Models.Queue import Queue


class BST:
    """Basic binary search tree implementation for Flight nodes."""

    def __init__(self):
        self._root = None

    def getRoot(self):
        return self._root

    def setRoot(self, root):
        self._root = root

    # Insert method to check if there is no root
    # When there is no root, the node is created and assigned as root
    # When there is a root, proceed to insert by calling the private function with the tree root and the node to insert
    def insert(self, node):
        # Check if there is no root to assign the new one as root
        if self._root is None:
            self._root = node
        else:
            self.__insert(self._root, node)

    # Recursive method to insert a node when the tree has a root
    def __insert(self, currentRoot, node):
        if node.getValue() == currentRoot.getValue():
            print(
                f"The value of the node {node.getValue()} already exists in the tree."
            )
        else:
            # Check if the value to insert is greater than the current root
            if node.getValue() > currentRoot.getValue():
                # Check if a right child exists
                if currentRoot.getRightChild() is None:
                    # If it has no right child, assign the node as right child
                    currentRoot.setRightChild(node)
                    # And the new node will have the current root as parent
                    node.setParent(currentRoot)
                else:
                    # It already has a right child, so insertion should be processed from the right child
                    # Making the recursive call with that child
                    self.__insert(currentRoot.getRightChild(), node)
            else:
                # The value of the node to insert is less than the value of the current root
                # Check if it has a left child
                if currentRoot.getLeftChild() is None:
                    # If it doesn't have one, assign the node as left child
                    currentRoot.setLeftChild(node)
                    # And the new node is assigned the current root as parent
                    node.setParent(currentRoot)
                else:
                    # If it has a left child, then recursively call with the left child and the node to insert.
                    self.__insert(currentRoot.getLeftChild(), node)

    # Method to search for a node by its value
    # Must follow the logic of BST rules
    def search(self, value):
        # Validate if a root exists in the tree
        if self._root is None:
            raise Exception("The tree has no root.")
        else:
            return self.__search(self._root, value)

    # Recursive function to handle the search
    def __search(self, currentRoot, value):
        # Validate if the searched value equals the current root
        if currentRoot.getValue() == value:
            # If so, return the current root
            return currentRoot
        # Otherwise validate if we should go right or left
        elif value > currentRoot.getValue():
            # If greater, verify that a right child exists
            # If it doesn't exist, return None
            if currentRoot.getRightChild() is None:
                return None
            else:
                # Pass the search request to the right child
                return self.__search(currentRoot.getRightChild(), value)
        else:
            # If less, verify that a left child exists
            # If it doesn't exist, return None
            if currentRoot.getLeftChild() is None:
                return None
            else:
                # Pass the search request to the left child
                return self.__search(currentRoot.getLeftChild(), value)

    # Method for breadth-first traversal
    def breadthFirstSearch(self):
        # Check if the tree is empty
        if self._root is None:
            print("The tree is empty.")
        else:
            # Enqueue the root first
            queue = Queue()
            queue.enqueue(self._root)
            # Traversal result
            result = []
            # While there are elements in the queue (nodes)
            # Process with: dequeue, print and enqueue children
            while not queue.is_empty():
                # Dequeue
                currentNode = queue.dequeue()
                # Print which is add to result
                result.append(currentNode.getValue())
                # Validate that it has a left child to enqueue it
                if currentNode.getLeftChild() is not None:
                    queue.enqueue(currentNode.getLeftChild())
                # Validate that it has a right child to enqueue it
                if currentNode.getRightChild() is not None:
                    queue.enqueue(currentNode.getRightChild())
        return result

    # Method for depth-first traversal type Pre-Order
    def preOrderTraversal(self):
        # Validate if the tree is empty and show message
        if self._root is None:
            print("El árbol está vacío.")
        else:
            # If the tree is not empty, generate a result that will have the traversal at the end
            result = []
            # Start the recursive call from the tree root
            self.__preOrderTraversal(self._root, result)
            return result

    # Recursive method for Pre-Order traversal
    def __preOrderTraversal(self, currentRoot, result):
        # Print (add to list) the current root
        result.append(currentRoot)

        # Check if it has a left child to continue traversal through it
        if currentRoot.getLeftChild() is not None:
            self.__preOrderTraversal(currentRoot.getLeftChild(), result)

        # Check if it has a right child to continue traversal through it
        if currentRoot.getRightChild() is not None:
            self.__preOrderTraversal(currentRoot.getRightChild(), result)

    # Method for depth-first traversal type In-Order
    def inOrderTraversal(self):
        # Validate if the tree is empty and show message
        if self._root is None:
            print("El árbol está vacío.")
        else:
            # If the tree is not empty, generate a result that will have the traversal at the end
            result = []
            # Start the recursive call from the tree root
            self.__inOrderTraversal(self._root, result)
            return result

    # Recursive method for In-Order traversal
    def __inOrderTraversal(self, currentRoot, result):
        # Check if it has a left child to continue traversal through it
        if currentRoot.getLeftChild() is not None:
            self.__inOrderTraversal(currentRoot.getLeftChild(), result)

        # Print (add to list) the current root
        result.append(currentRoot)

        # Check if it has a right child to continue traversal through it
        if currentRoot.getRightChild() is not None:
            self.__inOrderTraversal(currentRoot.getRightChild(), result)

    # Method for depth-first traversal type Post-Order
    def posOrderTraversal(self):
        # Validate if the tree is empty and show message
        if self._root is None:
            print("El árbol está vacío.")
        else:
            # If the tree is not empty, generate a result that will have the traversal at the end
            result = []
            # Start the recursive call from the tree root
            self.__posOrderTraversal(self._root, result)
            return result

    # Recursive method for Post-Order traversal
    def __posOrderTraversal(self, currentRoot, result):
        # Check if it has a left child to continue traversal through it
        if currentRoot.getLeftChild() is not None:
            self.__posOrderTraversal(currentRoot.getLeftChild(), result)

        # Check if it has a right child to continue traversal through it
        if currentRoot.getRightChild() is not None:
            self.__posOrderTraversal(currentRoot.getRightChild(), result)

        # Print (add to list) the current root
        result.append(currentRoot)

    # Method to delete
    def delete(self, value):
        if self._root is None:
            print("El árbol está vacío.")
        else:
            node = self.__search(self._root, value)
            if node is None:
                print(f"El valor {value} no se encuentra en el árbol.")
            else:
                self.__deleteNode(node)

    # Method that evaluates each deletion case and proceeds accordingly
    def __deleteNode(self, node):
        # Identify the deletion case
        nodeCase = self.IdentifyDeletionCase(node)
        match nodeCase:
            case 1:
                self.__deleteLeafNode(node)
            case 2:
                self.__deleteNodeWithOneChild(node)
            case 3:
                self.__deleteNodeWithTwoChildren(node)

    # Method that allows deleting a leaf node from the tree
    def __deleteLeafNode(self, node):
        if node.getValue() < node.getParent().getValue():
            node.getParent().setLeftChild(None)
        else:
            node.getParent().setRightChild(None)
        node.setParent(None)

    def __deleteNodeWithOneChild(self, node):
        # Identify the single child of the node to delete.
        if node.getLeftChild() is not None:
            child = node.getLeftChild()
        else:
            child = node.getRightChild()

        # Determine whether the child should become the left or right child of the parent.
        if child.getValue() < node.getParent().getValue():
            node.getParent().setLeftChild(child)
        else:
            node.getParent().setRightChild(child)

        # Update the parent reference of the promoted child.
        child.setParent(node.getParent())

        # Clear the deleted node's references for cleanup.
        node.setParent(None)
        node.setLeftChild(None)
        node.setRightChild(None)

    def __deleteNodeWithTwoChildren(self, node):
        # Find the inorder successor of the node to delete.
        # The successor is the rightmost node in the left subtree.
        successor = node.getLeftChild()
        while successor.getRightChild() is not None:
            successor = successor.getRightChild()

        # Replace the deleted node's value with the successor's value.
        node.setValue(successor.getValue())

        # Recursively delete the successor node.
        self.__deleteNode(successor)

    # Method to identify which is the deletion case
    # 1. Leaf node
    # 2. Node with one child
    # 3. Node with 2 children
    def IdentifyDeletionCase(self, node):
        nodeCase = 2
        if node.getLeftChild() is None and node.getRightChild() is None:
            nodeCase = 1
        elif node.getLeftChild() is not None and node.getRightChild() is not None:
            nodeCase = 3
        return nodeCase

    # Method that allows calculating the height of a node
    def getHeightNode(self, node):
        if node is None:
            return -1
        else:
            return self.__getHeightNode(node)

    # Recursive calculation of the height of a node
    def __getHeightNode(self, node):
        # If it is None, return -1 to balance the +1 of its parent
        if node is None:
            return -1
        else:
            # Check height by left child
            leftHeight = self.__getHeightNode(node.getLeftChild())
            # Check height by right child
            rightHeight = self.__getHeightNode(node.getRightChild())
            # Get the greatest value of the calculated heights
            maxHeight = max(leftHeight, rightHeight)
            # Increment by 1 when returning to parent to represent the edge that unites them
            return maxHeight + 1

    # Method to draw the tree as a tree
    def print_tree(self):
        if self._root is None:
            print("El árbol está vacío.")
        else:
            self.__print_tree(self._root, "", True)

    # Method to print the BST
    def __print_tree(self, node=None, prefix="", is_left=True):
        if node is not None:
            # Print right subtree
            if node.getRightChild():
                new_prefix = prefix + ("│   " if is_left else "    ")
                self.__print_tree(node.getRightChild(), new_prefix, False)

            # Print current node
            connector = "└── " if is_left else "┌── "
            print(prefix + connector + str(node.getValue()))

            # Print left subtree
            if node.getLeftChild():
                new_prefix = prefix + ("    " if is_left else "│   ")
                self.__print_tree(node.getLeftChild(), new_prefix, True)

    def buildFromTopology(self, tree_data):
        # Define an internal recursive function to build each node
        def build_node(data):
            # If the data is None (leaf or empty), return None
            if data is None:
                return None

            # Create a Flight instance with the JSON fields
            flight = Flight(
                id=str(data.get("code") or data.get("codigo") or data.get("id")),
                origin=data.get("origin") or data.get("origen"),
                destiny=data.get("destiny") or data.get("destino"),
                departureTime=data.get("departureTime") or data.get("horaSalida"),
                basePrice=data.get("basePrice") or data.get("precioBase"),
                finalPrice=data.get("finalPrice") or data.get("precioFinal"),
                passengers=data.get("passengers") or data.get("pasajeros"),
                promotion=data.get("promotion") if data.get("promotion") is not None else data.get("promocion", False),
                alert=data.get("alert") if data.get("alert") is not None else data.get("alerta", False),
                priority=data.get("priority") or data.get("prioridad", 0)
            )
            left_key = data.get("left") or data.get("izquierdo")
            right_key = data.get("right") or data.get("derecho")
            flight.setLeftChild(build_node(left_key))
            flight.setRightChild(build_node(right_key))

            # If left child exists, assign this node as its parent
            if flight.getLeftChild():
                flight.getLeftChild().setParent(flight)

            # If right child exists, assign this node as its parent
            if flight.getRightChild():
                flight.getRightChild().setParent(flight)

            # Return the constructed node
            return flight

        # Assign the tree root by calling build_node with the root data from JSON
        self._root = build_node(tree_data)

    def get_all_nodes(self):
        nodes = []
        self.__inOrderTraversal(self._root, nodes)
        return nodes

    # Method to count the leaves of the tree (nodes without children)
    def countLeaves(self):
        if self._root is None:
            return 0
        return self.__countLeaves(self._root)

    # Auxiliary recursive method to count leaves
    def __countLeaves(self, node):
        if node is None:
            return 0
        # If it has no left or right children, it is a leaf
        if node.getLeftChild() is None and node.getRightChild() is None:
            return 1
        # Sum the leaves of the left and right subtrees
        return self.__countLeaves(node.getLeftChild()) + self.__countLeaves(
            node.getRightChild()
        )

    # Method to get the depth of the tree (height)
    def getDepth(self):
        return self.getHeightNode(self._root)

    # ==================== SERIALIZATION ====================
    # Method to save the complete tree in JSON

    def serialize_to_dict(self):
        """
        Converts the complete tree to a dictionary to save as JSON.
        Preserves the complete hierarchical structure with all data.

        Returns:
            dict: Nested dictionary representing the complete tree.
                  Each node contains: flight data + height + balance factor (if AVL)
                  + references to left and right children.
        """
        return self.__serialize_node(self._root)

    def __serialize_node(self, node):
        """
        Recursive function that serializes a node and its subtrees.
        Processes each node and recursively calls its children.

        Parameters:
            node: Current node to serialize (can be None)

        Returns:
            dict or None: Dictionary with node data and children, or None if node is empty
        """
        # If the node is None, return None (base case of recursion)
        if node is None:
            return None

        # Create dictionary with all flight data
        node_data = {
            "id": node.getValue(),
            "origin": node.getOrigin(),
            "destiny": node.getDestiny(),
            "departureTime": str(node.getDepartureTime()),
            "basePrice": node.getBasePrice(),
            "finalPrice": node.getFinalPrice(),
            "passengers": node.getPassengers(),
            "promotion": node.getPromotion(),
            "alert": node.getAlert(),
            "priority": node.getPriority(),
        }

        # If it is an AVL tree, add balancing information
        # (The AVL class inherits from BST so verify using isinstance)
        from App.Models.AVL import AVL

        if isinstance(self, AVL):
            node_data["height"] = self.getHeightNode(node)
            node_data["balanceFactor"] = self.getBalanceFactor(node)

        # RECURSIVE calls to children
        # This is what builds the hierarchical structure
        node_data["left"] = self.__serialize_node(node.getLeftChild())
        node_data["right"] = self.__serialize_node(node.getRightChild())

        return node_data

    def getNodeDepth(self, node):
        depth = 0
        current = node
        while current.getParent() is not None:
            current = current.getParent()
            depth += 1
        return depth
