from Modelos.BST import BST

class AVL(BST):
    def __init__(self):
        self._root = None

    def getRoot(self):
        return self._root
    
    def setRoot(self, root):
        self._root = root

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

    # Método que permite calcular la altura de un nodo
    def getHeightNode(self, node):
        if node is None:
            return -1
        else:
            return self.__getHeightNode(node)

    # Cálculo recursivo de la altura de un nodo
    def __getHeightNode(self, node):
        # si es None se debe retornar -1 para equilibrar el +1 de su padre
        if node is None:
            return -1
        else:
            # se verifica altura por hijo izquierdo
            leftHeight = self.__getHeightNode(node.getLeftChild())
            # se verifica altura por hijo derecho
            rightHeight = self.__getHeightNode(node.getRightChild())
            # se obtiene el mayor valor de las alturas calculadas
            maxHeight = max(leftHeight, rightHeight)
            # se incrementa en 1 al retornar al padre para representar la arista que los une
            return maxHeight + 1

    # INICIO DE MÉTODOS DEL BALANCEO DEL ÁRBOL AVL
    # -----------------------------------------------------------

    # Método para chequear el balanceo de un árbol a partir de un nodo
    def checkBalance(self, node):
        if node is None:
            raise Exception("EL nodo a balancear no es válido")
        elif node != self.root:
            self.__checkBalance(node)

    # Método recursivo para validar el balanceo de un árbol
    def __checkBalance(self, node):
        bf = self.getBalanceFactor(node)
        if bf > 1 or bf < -1:
        # se identifica el caso de desbalanceo (LL, RR, RL, LR)
            bfCase = self.getBalanceCase(node, bf)
            match bfCase:
                case "LL":
                    self.__rotateRight(node)

                case "RR":
                    self.__rotateLeft(node)


        # Método para balancear un caso de desbalanceo LL
        else:
        # se verifica que el nodo actual no sea la raiz, y se invoca el chequeo de balanceo con su padre.
        # cuando es la raiz se finaliza la evaluación
            if node != self.root:
        #if node.getParent() is not None:
                self.__checkBalance(node.getParent())

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
            self.root = middleNode
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
            self.root = middleNode
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
            # caso negativo va por R
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