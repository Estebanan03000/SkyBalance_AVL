import json  # To load JSON files
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add root to path
from AVL import AVL  # Import AVL class
from BST import BST  # Import BST class
from Flight import Flight  # Import Flight class to create nodes


class JSONLoader:
    def __init__(self):
        self.avl = AVL()  # Instance of main AVL tree
        self.bst = None  # Instance of BST for comparison (only in insertion)

    def load_from_file(self, file_path):
        # Open and load JSON file content
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Automatically detects the type of JSON:
        # - If it has "flights", it is of type "insertion"
        # - If it has "codigo", it is of type "topology"
        if "flights" in data:
            self.load_insertion(data["flights"])
        elif "codigo" in data:
            self.load_topology(data)
        else:
            raise ValueError("Unrecognized JSON type. Must have 'flights' or 'codigo'.")

    def load_insertion(self, flights):
        # Create a BST to compare with the AVL
        self.bst = BST()
        # Iterate over each flight in the list
        for v in flights:
            # Create a Flight instance mapping JSON fields
            flight = Flight(
                id=v["codigo"],  # Flight ID
                origin=v["origen"],  # Origin
                destiny=v["destino"],  # Destination
                departureTime=v["horaSalida"],  # Departure time
                basePrice=v["precioBase"],  # Base price
                finalPrice=v["precioFinal"],  # Final price
                passengers=v["pasajeros"],  # Number of passengers
                promotion=v["promocion"],  # Promotion
                alert=v["alerta"],  # Alert
            )
            # Insert flight into AVL (automatically balanced)
            self.avl.insert(flight)
            # Insert flight into BST for comparison
            self.bst.insert(flight)
        self.avl.applyDepthPenalty()  # Calculate penalization based on depth after all insertions
        # Print AVL properties
        print(
            f"AVL - Root: {self.avl.getRoot().getValue() if self.avl.getRoot() else 'None'}, Depth: {self.avl.getDepth()}, Leaves: {self.avl.countLeaves()}"
        )
        # Print BST properties
        print(
            f"BST - Root: {self.bst.getRoot().getValue() if self.bst.getRoot() else 'None'}, Depth: {self.bst.getDepth()}, Leaves: {self.bst.countLeaves()}"
        )

    def load_topology(self, tree_data):
        # Reconstruct the AVL from the JSON topology
        self.avl.buildFromTopology(tree_data)
        # Print reconstructed AVL properties
        print(
            f"AVL - Root: {self.avl.getRoot().getValue() if self.avl.getRoot() else 'None'}, Depth: {self.avl.getDepth()}, Leaves: {self.avl.countLeaves()}"
        )


# Block to test the code (runs if you execute this file directly)
if __name__ == "__main__":
    loader = JSONLoader()
    # Change to the real path of your JSON
    loader.load_from_file("Modelos/prueba_insercion.json")
