from Models.BST import BST



class AVL(BST):
    def __init__(self):
        self._root = None

    def getRoot(self):
        return self._root

    def setRoot(self, root):
        self._root = root

    # Método público para insertar
    def insert(self, node):

        # si el árbol está vacío se inserta como raiz y el padre sería None
        if self._root is None:
            self._root = node
            node.setParent(None)

        # si ya hay raíz se llama al método privado
        else:
            self.__insert(self._root, node)

    # Método recursivo para insertar un nodo cuando se tiene raiz en el árbol
    def __insert(self, currentRoot, node):
        if node.getValue() == currentRoot.getValue():
            print(f"El valor del nodo {node.getValue()} ya existe en el árbol.")
        else:
            # se verifica si el valor a insertar es mayor que el actual raiz
            if node.getValue() > currentRoot.getValue():
                # se verifica si existe un hijo derecho
                if currentRoot.getRightChild() is None:
                    # si no tiene hijo derecho, se asigna el nodo como hijo derecho
                    currentRoot.setRightChild(node)
                    # y el nuevo nodo tendrá como padre a la actual raiz
                    node.setParent(currentRoot)
                    # verificar desbalanceo
                    self.checkBalance(currentRoot)
                else:
                    # ya tiene hijo derecho, entonces se debe procesar la inserción desde el hijo derecho
                    # haciendo el llamado recursivo con ese hijo
                    self.__insert(currentRoot.getRightChild(), node)
            else:
                # el valor del nodo a insertar es menor que el valor de la actual raiz
                # se verifica si tiene hijo izquierdo
                if currentRoot.getLeftChild() is None:
                    # si no tiene se asigna el nodo como hijo izquierdo
                    currentRoot.setLeftChild(node)
                    # y al nuevo nodo se le asigna como padre a la actual raiz
                    node.setParent(currentRoot)
                    # verificar desbalanceo
                    self.checkBalance(currentRoot)
                else:
                    # si tiene hijo izquierdo, entonces se llama recursivamente por el hijo izquierdo con el nodo a insertar.
                    self.__insert(currentRoot.getLeftChild(), node)

    # INICIO DE MÉTODOS DEL BALANCEO DEL ÁRBOL AVL
    # -----------------------------------------------------------

    # Método para chequear el balanceo de un árbol a partir de un nodo
    def checkBalance(self, node):
        if node is None:
            raise Exception("EL nodo a balancear no es válido")
        self.__checkBalance(node)

    # Método recursivo para validar el balanceo de un árbol
    def __checkBalance(self, node):
        # Se identifica el padre antes de hacer la rotación para evitar confusiones
        parent = node.getParent()
        bf = self.getBalanceFactor(node)
        if abs(bf) > 1:
            # se identifica el caso de desbalanceo (LL, RR, RL, LR)
            bfCase = self.getBalanceCase(node, bf)
            match bfCase:
                case "LL":
                    # rotar el nodo de en medio hacia la derecha
                    self.__rotateRight(node)

                case "RR":
                    # rotar el nodo de en medio hacia la izquierda
                    self.__rotateLeft(node)

                case "LR":
                    # rotar el hijo izquierdo
                    self.__rotateLeft(node.getLeftChild())

                    # rotar el nodo desbalanceado
                    self.__rotateRight(node)
                case "RL":
                    # rotar el hijo derecho
                    self.__rotateRight(node.getRightChild())

                    # rotar el nodo desbalanceado
                    self.__rotateLeft(node)
        # Se verifica que el padre no sea None y se procede a balancearlo si lo requiere
        if parent is not None:
            self.__checkBalance(parent)
        # Método para balancear un caso de desbalanceo LL
        # elif node != self.__root:
        # if node.getParent() is not None:
        # self.__checkBalance(node.getParent())

    # método para el giro simple a la derecha
    def __rotateRight(self, topNode):
        # se obtiene el nodo de la mitad
        middleNode = topNode.getLeftChild()

        # se obtiene el padre del nodo superior, cuando es la raiz será None
        parentTopNode = topNode.getParent()

        # se obtiene el hijo derecho del nodo de la mitad
        rightChildOfMiddleNode = middleNode.getRightChild()

        # se mueve el superior como hijo derecho del nodo de la mitad
        middleNode.setRightChild(topNode)
        topNode.setParent(middleNode)

        # reacomodar al nodo padre del superior apuntando al de la mitad
        # verificar si el superior era la raiz
        if parentTopNode is None:
            self._root = middleNode
            middleNode.setParent(None)
        else:
            if parentTopNode.getLeftChild() == topNode:
                parentTopNode.setLeftChild(middleNode)
            else:
                parentTopNode.setRightChild(middleNode)
            # sin importar si era hijo izq o derecho, se asigna ese padre del superior como padre del nodo de la mitad
            middleNode.setParent(parentTopNode)

        # reasignar el hijo derecho del nodo de la mitad al nodo superior que ya bajó como hijo derecho del nodo de la mitad
        topNode.setLeftChild(rightChildOfMiddleNode)
        if rightChildOfMiddleNode is not None:
            rightChildOfMiddleNode.setParent(topNode)

    # método para el giro simple a la izquierda
    def __rotateLeft(self, topNode):
        # se obtiene el nodo de la mitad
        middleNode = topNode.getRightChild()

        # se obtiene el padre del nodo superior, cuando es la raiz será None
        parentTopNode = topNode.getParent()

        # se obtiene el hijo izquierdo del nodo de la mitad
        leftChildOfMiddleNode = middleNode.getLeftChild()

        # se mueve el superior como hijo izquierdo del nodo de la mitad
        middleNode.setLeftChild(topNode)
        topNode.setParent(middleNode)

        # reacomodar al nodo padre del superior apuntando al de la mitad
        # verificar si el superior era la raiz
        if parentTopNode is None:
            self._root = middleNode
            middleNode.setParent(None)
        else:
            if parentTopNode.getLeftChild() == topNode:
                parentTopNode.setLeftChild(middleNode)
            else:
                parentTopNode.setRightChild(middleNode)
            # sin importar si era hijo izq o derecho, se asigna ese padre del superior como padre del nodo de la mitad
            middleNode.setParent(parentTopNode)

        # reasignar el hijo izquierdo del nodo de la mitad al nodo superior que ya bajó como hijo izquierdo del nodo de la mitad
        topNode.setRightChild(leftChildOfMiddleNode)
        if leftChildOfMiddleNode is not None:
            leftChildOfMiddleNode.setParent(topNode)

    # método para identificar el caso de desbalanceo
    def getBalanceCase(self, node, bf):
        bfCase = ""
        # caso negativo, va por R
        if bf < -1:
            bfChild = self.getBalanceFactor(node.getRightChild())
            # caso negativo, va por R
            if bfChild < 0:
                bfCase = "RR"
            else:
                # caso positivo va por L
                bfCase = "RL"
        # caso positivo L
        else:
            bfChild = self.getBalanceFactor(node.getLeftChild())
            # caso positivo, va por L
            if bfChild > 0:
                bfCase = "LL"
            else:
                # caso negativo va por RM
                bfCase = "LR"
        return bfCase

    # Método para calcular el BF de un nodo
    def getBalanceFactor(self, node):
        if node is None:
            return 0
        leftChildHeight = self.getHeightNode(node.getLeftChild())
        rightChildHeight = self.getHeightNode(node.getRightChild())
        return leftChildHeight - rightChildHeight

    # -----------------------------------------------------------
    # FIN DE MÉTODOS DEL BALANCEO DEL ÁRBOL AVL
