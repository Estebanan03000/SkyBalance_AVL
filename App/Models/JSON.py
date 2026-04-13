"""Utilities for loading flight datasets into AVL and BST structures."""

import json  # To load JSON files
import sys
import os

try:
    from App.Models.AVL import AVL  # Import AVL class
    from App.Models.BST import BST  # Import BST class
    from App.Models.Flight import Flight  # Import Flight class to create nodes
except ImportError:
    # Fallback for direct execution from this folder.
    current_dir = os.path.dirname(__file__)
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    from AVL import AVL
    from BST import BST
    from Flight import Flight


class JSONLoader:
    """Utility class to load flight data from JSON into tree structures."""

    def __init__(self):
        self.avl = AVL()  # Main AVL tree instance
        self.bst = None  # BST instance used only for insertion comparison

    @staticmethod
    def _get_value(record, *keys, default=None):
        """Return the first non-None value found for the provided keys."""
        for key in keys:
            if key in record and record[key] is not None:
                return record[key]
        return default

    def _build_flight(self, record):
        """Create a Flight instance from either English or Spanish JSON keys."""
        return Flight(
            id=self._get_value(record, "code", "codigo"),
            origin=self._get_value(record, "origin", "origen"),
            destiny=self._get_value(record, "destiny", "destino"),
            departureTime=self._get_value(record, "departureTime", "horaSalida"),
            basePrice=self._get_value(record, "basePrice", "precioBase"),
            finalPrice=self._get_value(
                record,
                "finalPrice",
                "precioFinal",
                "basePrice",
                "precioBase",
            ),
            passengers=self._get_value(record, "passengers", "pasajeros"),
            promotion=self._get_value(record, "promotion", "promocion", default=False),
            alert=self._get_value(record, "alert", "alerta", default=False),
            priority=int(self._get_value(record, "priority", "prioridad", default=0) or 0),
        )

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
        self.avl = AVL()
        self.bst = BST()

        for record in flights:
            # Each tree must receive its own node instance to avoid shared parent/child pointers.
            self.avl.insert(self._build_flight(record))
            self.bst.insert(self._build_flight(record))

        depth_penalty = getattr(self.avl, "applyDepthPenalty", None)
        if callable(depth_penalty):
            depth_penalty()

        avl_root = self.avl.getRoot()
        bst_root = self.bst.getRoot()

        print(
            f"AVL - Root: {avl_root.getValue() if avl_root else 'None'}, Depth: {self.avl.getDepth()}, Leaves: {self.avl.countLeaves()}"
        )
        print(
            f"BST - Root: {bst_root.getValue() if bst_root else 'None'}, Depth: {self.bst.getDepth()}, Leaves: {self.bst.countLeaves()}"
        )

    def load_topology(self, tree_data):
        # Reconstruct the AVL from the JSON topology
        self.avl = AVL()
        self.avl.buildFromTopology(tree_data)

        avl_root = self.avl.getRoot()
        print(
            f"AVL - Root: {avl_root.getValue() if avl_root else 'None'}, Depth: {self.avl.getDepth()}, Leaves: {self.avl.countLeaves()}"
        )


