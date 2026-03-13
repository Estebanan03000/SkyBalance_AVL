import json  # Para cargar archivos JSON
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Agrega la raíz al path
from Modelos.AVL import AVL  # Importa la clase AVL
from Modelos.BST import BST  # Importa la clase BST
from Modelos.Flight import Flight  # Importa la clase Flight para crear nodos

class JSONLoader:
    def __init__(self):
        self.avl = AVL()  # Instancia del árbol AVL principal
        self.bst = None   # Instancia del BST para comparación (solo en inserción)

    def load_from_file(self, file_path):
        # Abre y carga el contenido del archivo JSON
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Detecta automáticamente el tipo de JSON:
        # - Si tiene "flights", es de tipo "inserción"
        # - Si tiene "codigo", es de tipo "topología"
        if "flights" in data:
            self.load_insertion(data["flights"])
        elif "codigo" in data:
            self.load_topology(data)
        else:
            raise ValueError("Tipo de JSON no reconocido. Debe tener 'flights' o 'codigo'.")

    def load_insertion(self, flights):
        # Crea un BST para comparar con el AVL
        self.bst = BST()
        # Itera sobre cada vuelo en la lista
        for v in flights:
            # Crea una instancia de Flight mapeando los campos del JSON
            flight = Flight(
                id=v['codigo'],          # ID del vuelo
                origin=v['origen'],       # Origen
                destiny=v['destino'],     # Hora de salida
                departureTime=v['horaSalida'],  # Hora de salida
                basePrice=v['precioBase'],      # Precio base
                finalPrice=v['precioFinal'],    # Precio final
                passengers=v['pasajeros'],      # Número de pasajeros
                promotion=v['promocion'],       # Promoción
                alert=v['alerta']               # Alerta
            )
            # Inserta el vuelo en el AVL (se balancea automáticamente)
            self.avl.insert(flight)
            # Inserta el vuelo en el BST para comparación
            self.bst.insert(flight)
        # Imprime las propiedades del AVL
        print(f"AVL - Raíz: {self.avl.getRoot().getValue() if self.avl.getRoot() else 'None'}, Profundidad: {self.avl.getDepth()}, Hojas: {self.avl.countLeaves()}")
        # Imprime las propiedades del BST
        print(f"BST - Raíz: {self.bst.getRoot().getValue() if self.bst.getRoot() else 'None'}, Profundidad: {self.bst.getDepth()}, Hojas: {self.bst.countLeaves()}")

    def load_topology(self, tree_data):
        # Reconstruye el AVL desde la topología del JSON
        self.avl.buildFromTopology(tree_data)
        # Imprime las propiedades del AVL reconstruido
        print(f"AVL - Raíz: {self.avl.getRoot().getValue() if self.avl.getRoot() else 'None'}, Profundidad: {self.avl.getDepth()}, Hojas: {self.avl.countLeaves()}")

# Bloque para probar el código (ejecuta si corres este archivo directamente)
if __name__ == "__main__":
    loader = JSONLoader()
    # Cambia por la ruta real de tu JSON
    loader.load_from_file("Modelos/prueba_insercion.json")