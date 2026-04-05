from App.Models.BST import BST

class AVL(BST):
    def __init__(self):
        super().__init__()  # Call the constructor of the parent class (BST)
        self._RR_count = 0
        self._LL_count = 0
        self._RL_count = 0
        self._LR_count = 0

    # Public method to insert
    def insert(self, node):

        # If the tree is empty, insert as root and parent would be None
        if self._root is None:
            self._root = node
            node.setParent(None)

        # If there is already a root, call the private method
        else:
            self.__insert(self._root, node)

    # Recursive method to insert a node when the tree has a root
    def __insert(self, currentRoot, node):
        if node.getValue() == currentRoot.getValue():
            print(f"El valor del nodo {node.getValue()} ya existe en el árbol.")
        else:
            # Check if the value to insert is greater than the current root
            if node.getValue() > currentRoot.getValue():
                # Check if a right child exists
                if currentRoot.getRightChild() is None:
                    # If it has no right child, assign the node as right child
                    currentRoot.setRightChild(node)
                    # And the new node will have the current root as parent
                    node.setParent(currentRoot)
                    # Check for imbalance
                    self.checkBalance(currentRoot)
                else:
                    # Already has a right child, so insertion should be processed from the right child
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
                    # Check for imbalance
                    self.checkBalance(currentRoot)
                else:
                    # If it has a left child, then recursively call with the left child and the node to insert.
                    self.__insert(currentRoot.getLeftChild(), node)

    # START OF AVL TREE BALANCING METHODS
    # -----------------------------------------------------------

    # Method to check the balancing of a tree from a node
    def checkBalance(self, node):
        if node is None:
            raise Exception("EL nodo a balancear no es válido")
        self.__checkBalance(node)

    # Recursive method to validate tree balancing
    def __checkBalance(self, node):
        # Identify the parent before rotation to avoid confusion
        parent = node.getParent()
        bf = self.getBalanceFactor(node)
        if abs(bf) > 1:
            # Identify the imbalance case (LL, RR, RL, LR)
            bfCase = self.getBalanceCase(node, bf)
            match bfCase:
                case "LL":
                    # Rotate the middle node to the right
                    self.__rotateRight(node)

                case "RR":
                    # Rotate the middle node to the left
                    self.__rotateLeft(node)

                case "LR":
                    # Rotate the left child
                    self.__rotateLeft(node.getLeftChild())

                    # Rotate the imbalanced node
                    self.__rotateRight(node)
                case "RL":
                    # Rotate the right child
                    self.__rotateRight(node.getRightChild())

                    # Rotate the imbalanced node
                    self.__rotateLeft(node)
        # Check that the parent is not None and proceed to balance it if required
        if parent is not None:
            self.__checkBalance(parent)
        # Método para balancear un caso de desbalanceo LL
        # elif node != self.__root:
        # if node.getParent() is not None:
        # self.__checkBalance(node.getParent())

# Method for simple rotation to the right
    def __rotateRight(self, topNode):
        self._LL_count += 1 
        # Get the middle node
        middleNode = topNode.getLeftChild()

        # Get the parent of the top node, when it is the root it will be None
        parentTopNode = topNode.getParent()

        # Get the right child of the middle node
        rightChildOfMiddleNode = middleNode.getRightChild()

        # Move the top as right child of the middle node
        middleNode.setRightChild(topNode)
        topNode.setParent(middleNode)

        # Rearrange the parent node of the top pointing to the middle
        # Check if the top was the root
        if parentTopNode is None:
            self._root = middleNode
            middleNode.setParent(None)
        else:
            if parentTopNode.getLeftChild() == topNode:
                parentTopNode.setLeftChild(middleNode)
            else:
                parentTopNode.setRightChild(middleNode)
            # Regardless of whether it was left or right child, assign that parent of the top as parent of the middle node
            middleNode.setParent(parentTopNode)

        # Reassign the left child of the middle node to the top node that already went down as right child of the middle node
        topNode.setLeftChild(rightChildOfMiddleNode)
        if rightChildOfMiddleNode is not None:
            rightChildOfMiddleNode.setParent(topNode)

    # Method for simple rotation to the left
    def __rotateLeft(self, topNode):
        self._RR_count += 1
        # Get the middle node
        middleNode = topNode.getRightChild()

        # Get the parent of the top node, when it is the root it will be None
        parentTopNode = topNode.getParent()

        # Get the left child of the middle node
        leftChildOfMiddleNode = middleNode.getLeftChild()

        # Move the top as left child of the middle node
        middleNode.setLeftChild(topNode)
        topNode.setParent(middleNode)

        # Rearrange the parent node of the top pointing to the middle
        # Check if the top was the root
        if parentTopNode is None:
            self._root = middleNode
            middleNode.setParent(None)
        else:
            if parentTopNode.getLeftChild() == topNode:
                parentTopNode.setLeftChild(middleNode)
            else:
                parentTopNode.setRightChild(middleNode)
            # Regardless of whether it was left or right child, assign that parent of the top as parent of the middle node
            middleNode.setParent(parentTopNode)

        # Reassign the left child of the middle node to the top node that already went down as left child of the middle node
        topNode.setRightChild(leftChildOfMiddleNode)
        if leftChildOfMiddleNode is not None:
            leftChildOfMiddleNode.setParent(topNode)

    # Method to identify the imbalance case
    def getBalanceCase(self, node, bf):
        bfCase = ""
        # Negative case, goes by R
        if bf < -1:
            bfChild = self.getBalanceFactor(node.getRightChild())
            if bfChild < 0:
                bfCase = "RR"  
            else:
                bfCase = "RL"
                self._RL_count += 1
        else:  # Positive case L
            bfChild = self.getBalanceFactor(node.getLeftChild())
            if bfChild > 0:
                bfCase = "LL"
            else:
                bfCase = "LR"
                self._LR_count += 1

        return bfCase
    
    #Method to return the amount of rotations of each type
    def getRotationCounts(self):
        return {
            "RR": self._RR_count,
            "LL": self._LL_count,
            "RL": self._RL_count,
            "LR": self._LR_count
        }
            
    # Method to calculate the BF of a node
    def getBalanceFactor(self, node):
        if node is None:
            return 0
        leftChildHeight = self.getHeightNode(node.getLeftChild())
        rightChildHeight = self.getHeightNode(node.getRightChild())
        return leftChildHeight - rightChildHeight

    # -----------------------------------------------------------
    # END OF AVL TREE BALANCING METHODS

    # Public method to delete a node by value, using inheritance from BST and adding balancing
    def delete(self, value):
        if self._root is None:
            print("El árbol está vacío.")
            return
        node = self.search(value)
        if node is None:
            print(f"El valor {value} no se encuentra en el árbol.")
            return
        parent = node.getParent()
        # Call the parent's delete method to handle the basic deletion logic
        super().delete(value)
        # After deletion, check balance from the parent
        if parent is not None:
            self.checkBalance(parent)
        elif self._root is not None:
            self.checkBalance(self._root)
