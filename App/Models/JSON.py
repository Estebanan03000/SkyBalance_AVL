import json  # To load JSON files
import sys
import os

# Add the parent folder to the path so model imports work when running this module directly.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from AVL import AVL  # Import AVL class
from BST import BST  # Import BST class
from Flight import Flight  # Import Flight class to create nodes


class JSONLoader:
    """Utility class to load flight data from JSON into tree structures."""

    def __init__(self):
        self.avl = AVL()  # Main AVL tree instance
        self.bst = None  # BST instance used only for insertion comparison

    def load_from_file(self, file_path):
        """Load flight data from a JSON file path.

        The method detects whether the JSON document is an insertion list
        or a tree topology document.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Automatically detect the JSON document type.
        if "flights" in data:
            self.load_insertion(data["flights"])
        elif "codigo" in data:
            self.load_topology(data)
        else:
            raise ValueError("Unrecognized JSON type. Must have 'flights' or 'codigo'.")

    def load_insertion(self, flights):
        """Load a list of flight records and insert them into AVL and BST instances."""
        self.bst = BST()

        for v in flights:
            flight = Flight(
                id=v["code"],
                origin=v["origin"],
                destiny=v["destination"],
                departureTime=v["departureTime"],
                basePrice=v["basePrice"],
                finalPrice=v["finalPrice"],
                passengers=v["passengers"],
                promotion=v["promotion"],
                alert=v["alert"],
                priority=v.get("priority", 3),  # Default priority to 3 if not provided
            )
            self.avl.insert(flight)
            self.bst.insert(flight)

        self.avl.applyDepthPenalty()

        print(
            f"AVL - Root: {self.avl.getRoot().getValue() if self.avl.getRoot() else 'None'}, Depth: {self.avl.getDepth()}, Leaves: {self.avl.countLeaves()}"
        )
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
