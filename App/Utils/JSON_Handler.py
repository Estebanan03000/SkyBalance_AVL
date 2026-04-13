"""
JSON_Handler.py
Generic module for loading and exporting flight data in both Insertion and Topology modes.
Supports flexible field naming (English and Spanish).
"""

import json
from App.Models.Flight import Flight


class JSONHandler:
    """
    Generic handler for importing/exporting flight trees in two formats:
    
    1. INSERTION MODE: Array of individual flights to be inserted sequentially
       - JSON structure: {"tipo": "INSERCION", "vuelos": [...]}
       - Used to compare AVL vs BST performance
       - Each flight is inserted in order, allowing analysis of tree growth
    
    2. TOPOLOGY MODE: Pre-built tree structure respecting parent-child relationships
       - JSON structure: {"codigo": X, "izquierdo": {...}, "derecho": {...}, ...}
       - Used to restore or share specific tree topologies
       - Maintains exact tree structure and balance factors
    """

    @staticmethod
    def detect_format(json_data):
        """
        Detect whether the JSON is in Insertion or Topology mode.
        
        Args:
            json_data (dict): Parsed JSON object
            
        Returns:
            str: Either "insertion" or "topology", or None if unrecognized
        """
        # INSERTION MODE: Has "flights" or "vuelos" at top level
        if "flights" in json_data or "vuelos" in json_data:
            return "insertion"
        
        # TOPOLOGY MODE: Has "code" or "codigo" at top level (root node)
        if "code" in json_data or "codigo" in json_data:
            return "topology"
        
        # Unknown format
        return None

    @staticmethod
    def load_insertion_mode(json_data):
        """
        Load flights from Insertion mode JSON.
        
        Expected format:
        {
            "tipo": "INSERCION",
            "ordenamiento": "codigo",
            "vuelos": [
                {"codigo": "SB400", "origen": "Medellin", ...},
                ...
            ]
        }
        
        Args:
            json_data (dict): Parsed JSON object
            
        Returns:
            list: List of Flight objects in insertion order
            
        Raises:
            ValueError: If the required "vuelos" or "flights" array is missing
        """
        # Support both Spanish ("vuelos") and English ("flights")
        flights_array = json_data.get("vuelos") or json_data.get("flights")
        
        if not flights_array:
            raise ValueError("JSON must include 'vuelos' or 'flights' array")
        
        flights = []
        for f_data in flights_array:
            flight = JSONHandler._parse_flight_data(f_data)
            flights.append(flight)
        
        return flights

    @staticmethod
    def load_topology_mode(json_data):
        """
        Load a pre-built tree structure from Topology mode JSON.
        
        Expected format:
        {
            "codigo": 500,
            "origen": "Medellin",
            ...,
            "izquierdo": { "codigo": 300, ... },
            "derecho": { "codigo": 700, ... }
        }
        
        Args:
            json_data (dict): Parsed JSON object representing tree root
            
        Returns:
            Flight: Root node of the reconstructed tree with all parent-child relationships
        """
        def build_node(data):
            if data is None:
                return None
            
            flight = JSONHandler._parse_flight_data(data)
            
            # Recursively build left and right subtrees
            left_key = data.get("left") or data.get("izquierdo")
            right_key = data.get("right") or data.get("derecho")
            
            left_child = build_node(left_key)
            right_child = build_node(right_key)
            
            flight.setLeftChild(left_child)
            flight.setRightChild(right_child)
            
            # Set parent references
            if left_child:
                left_child.setParent(flight)
            if right_child:
                right_child.setParent(flight)
            
            return flight
        
        return build_node(json_data)

    @staticmethod
    def export_insertion_mode(flights_list):
        """
        Export a list of flights as Insertion mode JSON.
        
        Perfect for sharing a dataset that should be re-inserted from scratch,
        or for comparing AVL vs BST performance on the same ordered data.
        
        Args:
            flights_list (list): List of Flight objects in insertion order
            
        Returns:
            dict: JSON-serializable dictionary in Insertion format
        """
        return {
            "tipo": "INSERCION",
            "ordenamiento": "codigo",
            "vuelos": [
                JSONHandler._flight_to_dict(f) for f in flights_list
            ]
        }

    @staticmethod
    def export_topology_mode(root_node):
        """
        Export a tree as Topology mode JSON.
        
        Preserves the exact structure and balance state of the tree,
        including height and balance factors.
        
        Args:
            root_node (Flight): Root of the flight tree
            
        Returns:
            dict: JSON-serializable dictionary representing the full tree structure
        """
        def node_to_dict(node):
            if node is None:
                return None
            
            data = JSONHandler._flight_to_dict(node)
            
            # Include tree structure information
            if hasattr(node, 'getHeight') and callable(node.getHeight):
                data["altura"] = node.getHeight()
            
            if hasattr(node, 'getBalanceFactor') and callable(node.getBalanceFactor):
                data["factorEquilibrio"] = node.getBalanceFactor()
            
            # Recursively export children
            left_child = node.getLeftChild()
            right_child = node.getRightChild()
            
            data["izquierdo"] = node_to_dict(left_child)
            data["derecho"] = node_to_dict(right_child)
            
            return data
        
        return node_to_dict(root_node)

    @staticmethod
    def _parse_flight_data(data):
        """
        Parse flight data from JSON, supporting both Spanish and English field names.
        
        Args:
            data (dict): Flight data from JSON
            
        Returns:
            Flight: Parsed Flight object
        """
        return Flight(
            id=data.get("code") or data.get("codigo"),
            origin=data.get("origin") or data.get("origen"),
            destiny=data.get("destiny") or data.get("destino"),
            departureTime=data.get("departureTime") or data.get("horaSalida"),
            basePrice=data.get("basePrice") or data.get("precioBase"),
            finalPrice=data.get("finalPrice") or data.get("precioFinal") or data.get("precioBase"),
            passengers=data.get("passengers") or data.get("pasajeros"),
            promotion=(
                data.get("promotion")
                if data.get("promotion") is not None
                else data.get("promocion", False)
            ),
            alert=(
                data.get("alert")
                if data.get("alert") is not None
                else data.get("alerta", False)
            ),
            priority=data.get("priority") or data.get("prioridad", 0)
        )

    @staticmethod
    def _flight_to_dict(flight):
        """
        Convert a Flight object to a dictionary with Spanish field names.
        
        Args:
            flight (Flight): Flight object to convert
            
        Returns:
            dict: Dictionary with flight data
        """
        return {
            "codigo": flight.getValue(),
            "origen": flight.getOrigin(),
            "destino": flight.getDestiny(),
            "horaSalida": str(flight.getDepartureTime()) if flight.getDepartureTime() else None,
            "precioBase": flight.getBasePrice(),
            "precioFinal": flight.getFinalPrice(),
            "pasajeros": flight.getPassengers(),
            "promocion": flight.getPromotion(),
            "alerta": flight.getAlert(),
            "prioridad": flight.getPriority() if hasattr(flight, 'getPriority') else 0
        }

    @staticmethod
    def save_to_file(data, filename):
        """
        Save JSON data to a file.
        
        Args:
            data (dict): Data to save
            filename (str): Output file path
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_from_file(filename):
        """
        Load JSON data from a file.
        
        Args:
            filename (str): Input file path
            
        Returns:
            dict: Parsed JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
