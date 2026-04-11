import os
import json
from flask import Blueprint, request, jsonify
from App.Services.Flight_Service import Flight_Service
from App.Models.Flight import Flight
from datetime import datetime
from App.Services.Metrics_Service import Metrics_Service

# Create an instance of the Flight_Service and Metrics_Service.
# These will stay in memory while the Flask application is running.
flight_service = Flight_Service()
metrics_service = Metrics_Service(flight_service)

# Create a Flask blueprint to group the application's API routes.
main_routes = Blueprint("main", __name__)


def _build_flight_from_payload(data):
    """Build a Flight instance from a JSON payload.

    This helper accepts alternate field names so the same payload can work with
    English or Spanish keys from different data sources.
    """
    date_value = data.get("date") or data.get("departureTime") or data.get("horaSalida")
    if isinstance(date_value, str) and "T" in date_value:
        # Accept ISO-like datetime strings and parse them directly.
        date_value = datetime.fromisoformat(date_value)

    return Flight(
        data.get("id") or data.get("codigo"),
        data.get("origin") or data.get("origen"),
        data.get("destiny") or data.get("destino"),
        date_value,
        data.get("basePrice") or data.get("precioBase"),
        data.get("finalPrice") or data.get("precioFinal"),
        data.get("passengers") or data.get("pasajeros"),
        data.get("discount", data.get("promotion", data.get("promocion", 0))),
        data.get("sold", data.get("alert", data.get("alerta", False))),
    )


def _load_flights_from_json_object(json_data):
    """Load flight records from a decoded JSON object.

    The JSON object must contain a top-level 'flights' array.
    """
    if "flights" not in json_data:
        raise ValueError("JSON must include a top-level 'flights' array")

    flight_list = []
    for item in json_data["flights"]:
        flight_list.append(_build_flight_from_payload(item))

    return flight_list


# ===============================
# GET /flights - List all flights
# ===============================
@main_routes.route("/flights", methods=["GET"])
def list_flights():
    """
    Endpoint to retrieve all flights stored in the AVL tree.

    Returns:
        JSON array of flight objects with the following fields:
            - id: Flight ID
            - origin: Flight origin
            - destiny: Flight destination
            - basePrice: Base price of the flight
            - finalPrice: Final price of the flight
            - passengers: Number of passengers
    """
    flights = flight_service.get_all_flights()

    # Convert Flight objects to dictionaries for JSON serialization
    flights_data = [
        {
            "id": f.getValue(),
            "origin": f.getOrigin(),
            "destiny": f.getDestiny(),
            "basePrice": f.getBasePrice(),
            "finalPrice": f.getFinalPrice(),
            "passengers": f.getPassengers(),
        }
        for f in flights
    ]
    return jsonify(flights_data)


# ===============================
# POST /flights - Create a new flight
# ===============================
@main_routes.route("/flights", methods=["POST"])
def create_flight():
    """
    Endpoint to create a new flight and insert it into the AVL tree.

    Expects JSON data in the request body with the following fields:
        - id: Unique flight ID
        - origin: Flight origin
        - destiny: Flight destination
        - date: Flight date in "%Y-%m-%d %H:%M:%S" format
        - basePrice: Base price
        - finalPrice: Final price
        - passengers: Number of passengers
        - discount (optional): Discount percentage (default 0)
        - sold (optional): Boolean indicating if the flight is sold (default False)

    Returns:
        JSON message confirming the creation with HTTP status 201.
    """
    data = request.get_json()

    flight = Flight(
        data["id"],
        data["origin"],
        data["destiny"],
        datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S"),
        data["basePrice"],
        data["finalPrice"],
        data["passengers"],
        data.get("discount", 0),
        data.get("sold", False),
    )

    flight_service.create_flight(flight)
    return jsonify({"message": "Flight created"}), 201


# ===============================
# PUT /flights/<flight_id> - Update an existing flight
# ===============================
@main_routes.route("/flights/<int:flight_id>", methods=["PUT"])
def update_flight(flight_id):
    """
    Endpoint to update an existing flight.

    Path Parameters:
        - flight_id: ID of the flight to update

    Request Body (JSON):
        - Any of the Flight attributes you want to update (e.g., origin, destiny, basePrice, finalPrice, passengers)

    Returns:
        JSON message confirming the update, or an error if the flight does not exist.
    """
    data = request.get_json()
    try:
        flight_service.update_flight(flight_id, **data)
        flight_service.applyDepthPenalty()
        return jsonify({"message": "Flight updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# ===============================
# DELETE /flights/<flight_id> - Delete a flight
# ===============================
@main_routes.route("/flights/<int:flight_id>", methods=["DELETE"])
def delete_flight(flight_id):
    """
    Endpoint to delete a flight from the AVL tree.

    Path Parameters:
        - flight_id: ID of the flight to delete

    Returns:
        JSON message confirming deletion, or an error if the flight does not exist.
    """
    try:
        flight_service.delete_flight(flight_id)
        flight_service.applyDepthPenalty()
        return jsonify({"message": "Flight deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 404


# ===============================
# POST /tree/export - Export tree to JSON file
# ===============================
@main_routes.route("/tree/export", methods=["POST"])
def export_tree():
    """
    Endpoint to export the complete AVL tree structure to a JSON file.

    The exported JSON preserves the hierarchical parent-child structure,
    node heights, balance factors (for AVL), and all flight details.

    Expects JSON in request body:
        - filename: Name or path of the JSON file to create
                    Example: "tree_backup.json"

    Returns:
        JSON message confirming successful export, or an error message.
    """
    try:
        data = request.get_json()
        filename = data.get("filename", "tree_export.json")

        # Export the tree to disk
        success = flight_service.export_tree_to_json(filename)

        if success:
            return (
                jsonify({"message": f"Tree exported successfully to {filename}"}),
                200,
            )
        else:
            return jsonify({"error": "Failed to export tree"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@main_routes.route("/flights/insert", methods=["POST"])
def insert_flight():
    """Insert a single flight using the bulk insertion service.

    This endpoint wraps the existing multi_inserts logic so the frontend can
    insert one flight with the same reporting behavior.
    """
    data = request.get_json()

    flight = Flight(
        data["id"],
        data["origin"],
        data["destiny"],
        datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S"),
        data["basePrice"],
        data["finalPrice"],
        data["passengers"],
        data.get("discount", 0),
        data.get("sold", False),
    )

    # Use multi_inserts to preserve rotation report generation.
    reports = flight_service.multi_inserts([flight])
    return jsonify(reports[0]), 200


@main_routes.route("/tree/load", methods=["POST"])
def load_tree():
    """Load flight data from a server-side JSON file and insert into the tree."""
    try:
        data = request.get_json() or {}
        filename = data.get("filename", "App/Models/prueba_insercion.json")
        path = filename if os.path.isabs(filename) else os.path.join(os.getcwd(), filename)

        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        flights = _load_flights_from_json_object(payload)
        reports = flight_service.multi_inserts(flights)
        return jsonify({"message": "JSON loaded successfully", "reports": reports}), 200
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {filename}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@main_routes.route("/tree/upload", methods=["POST"])
def upload_tree():
    """Upload a JSON file from the frontend and insert its flights into the tree."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        payload = json.load(file)
        flights = _load_flights_from_json_object(payload)
        reports = flight_service.multi_inserts(flights)
        return jsonify({"message": "Uploaded JSON file successfully", "reports": reports}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@main_routes.route("/tree/undo", methods=["POST"])
def undo_action():
    """Undo the last flight operation stored in the history stack."""
    try:
        flight_service.undo()
        return jsonify({"message": "Action undone"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@main_routes.route("/tree/cancel-subtree", methods=["POST"])
def cancel_subtree():
    """Cancel a subtree starting at the given flight node."""
    data = request.get_json() or {}
    flight_id = data.get("id")
    if flight_id is None:
        return jsonify({"error": "Flight id is required"}), 400

    node = flight_service.get_flight(flight_id)
    if node is None:
        return jsonify({"error": "Flight not found"}), 404

    deleted_count = metrics_service.massiveCancelation(node)
    return jsonify({"message": "Subtree canceled", "deleted_count": deleted_count}), 200


@main_routes.route("/config/mode", methods=["PUT"])
def switch_mode():
    """Switch the tree implementation mode between Stress (BST) and Global Balance (AVL)."""
    data = request.get_json() or {}
    mode = data.get("mode")
    if mode not in ["Stress", "Global Balance"]:
        return jsonify({"error": "Invalid mode. Use 'Stress' or 'Global Balance'"}), 400

    flight_service.set_mode(mode)
    return jsonify({"message": f"Mode switched to {mode}"}), 200


@main_routes.route("/tree/verify", methods=["GET"])
def verify_tree():
    """Verify the current tree balance and identify inconsistent nodes."""
    tree = flight_service._tree
    flights = flight_service.get_all_flights()
    inconsistent = []

    for node in flights:
        left_height = tree.getHeightNode(node.getLeftChild())
        right_height = tree.getHeightNode(node.getRightChild())
        if abs(left_height - right_height) > 1:
            inconsistent.append(node.getValue())

    return jsonify(
        {
            "balanced": len(inconsistent) == 0,
            "inconsistent_nodes": inconsistent,
            "mode": "AVL" if tree.__class__.__name__ == "AVL" else "Stress",
        }
    )


@main_routes.route("/tree/traverse", methods=["GET"])
def traverse_tree():
    """Traverse the tree using BFS, DFS, or INORDER order and return node IDs."""
    order_type = request.args.get("type", "BFS").upper()
    tree = flight_service._tree

    if order_type == "BFS":
        result = tree.breadthFirstSearch()
    elif order_type == "DFS":
        nodes = tree.preOrderTraversal() or []
        result = [node.getValue() for node in nodes]
    elif order_type == "INORDER":
        nodes = tree.inOrderTraversal() or []
        result = [node.getValue() for node in nodes]
    else:
        return jsonify({"error": "Invalid traversal type"}), 400

    return jsonify({"order": order_type, "nodes": result})


@main_routes.route("/queue/process", methods=["POST"])
def process_queue():
    """Process a list of flights provided in the request body."""
    data = request.get_json() or {}
    flights_data = data.get("flights")

    if not isinstance(flights_data, list):
        return jsonify({"error": "A list of flights is required"}), 400

    flights = [_build_flight_from_payload(item) for item in flights_data]
    reports = flight_service.multi_inserts(flights)
    return jsonify({"message": "Queue processed", "reports": reports}), 200


@main_routes.route("/metrics", methods=["GET"])
def get_metrics():
    """Return real-time metrics for the current flight tree."""
    metrics_data = metrics_service.getRealTimeMetrics()

    # Return the collected metrics as JSON.
    return jsonify(metrics_data)


@main_routes.route("/config/max-depth", methods=["PUT"])
def set_max_depth():
    """Update the maximum depth threshold used for depth penalty pricing."""
    data = request.get_json()
    flight_service.setMaxDepth(data["maxDepth"])
    return jsonify(
        {"message": "Depth penalty configuration updated and prices recalculated."}
    )


@main_routes.route("/flights/lowest-profitability", methods=["DELETE"])
def delete_lowest_profitability():
    """Delete the flight with the lowest profitability and return the deleted flight ID."""
    try:
        flight_id = flight_service.deleteLowestProfitability()
        return (
            jsonify({"message": "Flight deleted successfully", "flight_id": flight_id}),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400
