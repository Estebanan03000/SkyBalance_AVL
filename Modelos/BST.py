class BST:
    def __init__(self):
        self._root = None

    def getRoot(self):
        return self._root
    
    def setRoot(self, root):
        self._root = root

    # método de insertar para verificar si no hay raíz
    # cuando no hay raíz, se crea el nodo y se asigna como raiz
    # cuando si hay raiz se procede a insertar llamando a la función privada con la raiz del árbol y el nodo a insertar
    def insert(self, node):
        # verificar si no hay raiz para asignar el nuevo como raiz
        if self.root is None:
            self.root = node
        else:
            self.__insert(self.root, node)

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
                else:
            # si tiene hijo izquierdo, entonces se llama recursivamente por el hijo izquierdo con el nodo a insertar.
                    self.__insert(currentRoot.getLeftChild(), node)

    # Método que permita realizar la búsqueda de un nodo mediante su valor
    # debe seguir la lógica de las reglas de un BST
    def search(self, value):
        #validar si existe una raíz en el árbol
        if self.root is None:
            raise Exception("El árbol no tiene una raíz.")
        else:
            return self.__search(self.root, value)

    # función recursiva para atender la búsqueda
    def __search(self, currentRoot, value):
        # validar si el valor buscado es igual a la raiz actual
        # print(f"El valor del nodo es: {currentRoot.getValue()}")
        # print(f"Comparación: {currentRoot.getValue() == value}" )
        if currentRoot.getValue() == value:
        # si es así se retorna la actual raiz
            return currentRoot
        # sino se valida si se debe ir por la derecha o por la izquierda
        elif value > currentRoot.getValue():
        # si es mayor, se verifica que exista un hijo derecho
        # en caso de no existir se genera
            if currentRoot.getRightChild() is None:
                return None
            else:
            # se pasa la solicitud de búsqueda al hijo derecho
                return self.__search(currentRoot.getRightChild(), value)
        else:
        # si es menor, se verifica que exista un hijo izquierdo
        # en caso de no existir se genera
            if currentRoot.getLeftChild() is None:
                return None
            else:
            # se pasa la solicitud de búsqueda al hijo izquierdo
                return self.__search(currentRoot.getLeftChild(), value)

    # Método para recorrido en anchura
    def breadthFirstSearch(self):
        # verificar si el árbol está vacío
        if self.root is None:
            print("El árbol está vacío.")
        else:
            # se encola la raíz de primera
            queue = [self.root]
            # resultado del recorrido
            result = []
            # mientras existan elementos en la cola (nodos)
            # se debe procesar con: desencolar, imprimir y encolar hijos
            while len(queue) > 0:
                # desencolar
                currentNode = queue.pop(0)
                # imprimir que es agregar al resultado
                result.append(currentNode.getValue())
                # se valida que tenga hijo derecho para encolarlo
                if currentNode.getLeftChild() is not None:
                    queue.append(currentNode.getLeftChild())
                # se valida que tenga hijo izquierdo para encolarlo
                if currentNode.getRightChild() is not None:
                    queue.append(currentNode.getRightChild())
        return result

    # Método para realizar el recorrido en profundidad tipo  Pre-Order
    def preOrderTraversal(self):
        # validar si el árbol está vacío y mostrar mensaje
        if self.root is None:
            print("El árbol está vacío.")
        else:
            # si el árbol no está vacío, se genera un result que tendrá el recorrido al final
            result = []
            # se inicia el llamado recursivo por la raiz del árbol
            self.__preOrderTraversal(self.root, result)
            return result

    # Método recursivo para el recorrido Pre-Order
    def __preOrderTraversal(self, currentRoot, result):
        # Se imprime (agrega a la cola) la raiz actual
        result.append(currentRoot)

        # se verifica si tiene hijo izquierdo para seguir el recorrido por él
        if currentRoot.getLeftChild() is not None:
            self.__preOrderTraversal(currentRoot.getLeftChild(), result)

        # se verifica si tiene hijo derecho para seguir el recorrido por él
        if currentRoot.getRightChild() is not None:
            self.__preOrderTraversal(currentRoot.getRightChild(), result)


    # Método para realizar el recorrido en profundidad tipo  In-Order
    def inOrderTraversal(self):
        # validar si el árbol está vacío y mostrar mensaje
        if self.root is None:
            print("El árbol está vacío.")
        else:
            # si el árbol no está vacío, se genera un result que tendrá el recorrido al final
            result = []
            # se inicia el llamado recursivo por la raiz del árbol
            self.__inOrderTraversal(self.root, result)
            return result

    # Método recursivo para el recorrido In-Order
    def __inOrderTraversal(self, currentRoot, result):
        # se verifica si tiene hijo izquierdo para seguir el recorrido por él
        if currentRoot.getLeftChild() is not None:
            self.__inOrderTraversal(currentRoot.getLeftChild(), result)

        # Se imprime (agrega a la cola) la raiz actual
        result.append(currentRoot)

        # se verifica si tiene hijo derecho para seguir el recorrido por él
        if currentRoot.getRightChild() is not None:
            self.__inOrderTraversal(currentRoot.getRightChild(), result)

    # Método para realizar el recorrido en profundidad tipo  Pos-Order
    def posOrderTraversal(self):
        # validar si el árbol está vacío y mostrar mensaje
        if self.root is None:
            print("El árbol está vacío.")
        else:
        # si el árbol no está vacío, se genera un result que tendrá el recorrido al final
            result = []
        # se inicia el llamado recursivo por la raiz del árbol
            self.__posOrderTraversal(self.root, result)
            return result

    # Método recursivo para el recorrido Pos-Order
    def __posOrderTraversal(self, currentRoot, result):
        # se verifica si tiene hijo izquierdo para seguir el recorrido por él
        if currentRoot.getLeftChild() is not None:
            self.__posOrderTraversal(currentRoot.getLeftChild(), result)

        # se verifica si tiene hijo derecho para seguir el recorrido por él
        if currentRoot.getRightChild() is not None:
            self.__posOrderTraversal(currentRoot.getRightChild(), result)

        # Se imprime (agrega a la cola) la raiz actual
        result.append(currentRoot)

    # Método para eliminar
    def delete(self, value):
        if self.root is None:
            print("El árbol está vacío.")
        else:
            node = self.__search(self.root, value)
            if node is None:
                print(f"El valor {value} no se encuentra en el árbol.")
            else:
                self.__deleteNode(node)

    # Método que evalúa cada uno de los casos de eliminar y procede según sea
    def __deleteNode(self, node):
        # identificar el caso de eliminación
        nodeCase = self.IdentifyDeletionCase(node)
        match nodeCase:
            case 1:
                self.__deleteLeafNode(node)
            case 2:
                self.__deleteNodeWithOneChild(node)
            case 3:
                self.__deleteNodeWithTwoChildren(node)

    # Método que permite eliminar un nodo hoja del árbol
    def __deleteLeafNode(self, node):
        if node.getValue() < node.getParent().getValue():
            node.getParent().setLeftChild(None)
        else:
            node.getParent().setRightChild(None)
        node.setParent(None)

    def __deleteNodeWithOneChild(self, node):
        if node.getLeftChild() is not None:
            child = node.getLeftChild()
        else:
            child = node.getRightChild()
        if child.getValue() < node.getParent().getValue():
            node.getParent().setLeftChild(child)
        else:
            node.getParent().setRightChild(child)
        child.setParent(node.getParent())
        node.setParent(None)
        node.setLeftChild(None)
        node.setRightChild(None)

    def __deleteNodeWithTwoChildren(self, node):
        successor = node.getLeftChild()
        while successor.getRightChild() is not None:
            successor = successor.getRightChild()
        node.setValue(successor.getValue())
        self.__deleteNode(successor)

    # Método para identificar cuál es el caso de eliminación
    # 1. Nodo hoja
    # 2. Nodo con un hijo
    # 3. Nodo con 2 hijos
    def IdentifyDeletionCase(self, node):
        nodeCase = 2
        if(node.getLeftChild() is None and node.getRightChild() is None):
            nodeCase = 1
        elif(node.getLeftChild() is not None and node.getRightChild() is not None):
            nodeCase = 3
        return nodeCase
    
    # Método para dibujar el árbol en forma de árbol
    def print_tree(self):
        if self.root is None:
            print("El árbol está vacío.")
        else:
            self.__print_tree(self.root, "", True)

    # Methodo para imprimir el árbol BST
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