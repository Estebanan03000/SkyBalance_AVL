import os
import json
from flask import Blueprint, request, jsonify
from App.Services.Flight_Service import Flight_Service
from App.Models.Flight import Flight
from datetime import datetime
from App.Services.Metrics_Service import Metrics_Service
from App.Utils.Tree_Render import TreeRenderer
from App.Models.Flight import Flight as flight_model

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


@main_routes.route("/flights/load", methods=["POST"])
def load_flights():
    try:
        data = request.get_json()

        # Reinitialize services at module level so all other endpoints see the new tree
        import App.routes as current_module
        current_module.flight_service = Flight_Service()
        current_module.metrics_service = Metrics_Service(current_module.flight_service)
        fs = current_module.flight_service

        # --- INSERTION MODE ---
        if "flights" in data or "vuelos" in data:
            from App.Models.BST import BST
            bst = BST()

            for v in (data.get("flights") or data.get("vuelos")):
                # Separate objects so parent pointers don't collide between trees
                flight_avl = Flight(
                    id=str(v.get("code") or v.get("codigo")),
                    origin=v.get("origin") or v.get("origen"),
                    destiny=v.get("destiny") or v.get("destino"),
                    departureTime=v.get("departureTime") or v.get("horaSalida"),
                    basePrice=v.get("basePrice") or v.get("precioBase"),
                    finalPrice=v.get("basePrice") or v.get("precioBase"),
                    passengers=v.get("passengers") or v.get("pasajeros"),
                    promotion=v.get("promotion") if v.get("promotion") is not None else v.get("promocion", False),
                    alert=v.get("alert") if v.get("alert") is not None else v.get("alerta", False),
                )
                flight_bst = Flight(
                    id=str(v.get("code") or v.get("codigo")),
                    origin=v.get("origin") or v.get("origen"),
                    destiny=v.get("destiny") or v.get("destino"),
                    departureTime=v.get("departureTime") or v.get("horaSalida"),
                    basePrice=v.get("basePrice") or v.get("precioBase"),
                    finalPrice=v.get("basePrice") or v.get("precioBase"),
                    passengers=v.get("passengers") or v.get("pasajeros"),
                    promotion=v.get("promotion") if v.get("promotion") is not None else v.get("promocion", False),
                    alert=v.get("alert") if v.get("alert") is not None else v.get("alerta", False),
                )
                fs._tree.insert(flight_avl)
                bst.insert(flight_bst)

            fs.applyDepthPenalty()

            avl_root = fs._tree._root
            bst_root = bst._root

            print("Nodes in AVL:", len(fs.get_all_flights()))
            print("AVL depth:", fs._tree.getDepth())
            print("BST depth:", bst.getDepth())

            return jsonify({
                "mode": "insertion",
                "avl": {
                    "root": avl_root.getValue() if avl_root else None,
                    "depth": fs._tree.getDepth(),
                    "leaves": fs._tree.countLeaves()
                },
                "bst": {
                    "root": bst_root.getValue() if bst_root else None,
                    "depth": bst.getDepth(),
                    "leaves": bst.countLeaves()
                }
            }), 200

        # --- TOPOLOGY MODE ---
        elif "code" in data or "codigo" in data:
            fs._tree.buildFromTopology(data)
            fs.applyDepthPenalty()
            root = fs._tree._root
            return jsonify({
                "mode": "topology",
                "avl": {
                    "root": root.getValue() if root else None,
                    "depth": fs._tree.getDepth(),
                    "leaves": fs._tree.countLeaves()
                }
            }), 200

        else:
            return jsonify({"error": "Unrecognized JSON format"}), 400

    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "detail": traceback.format_exc()
        }), 500

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

    # If tree is empty, return empty list instead of crashing
    if not flights:
        return jsonify([])

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
    try:
        import App.routes as current_module
        fs = current_module.flight_service

        data = request.get_json()

        flight = Flight(
            str(data["id"]),
            data["origin"],
            data["destiny"],
            data["date"],
            data["basePrice"],
            data["finalPrice"],
            data["passengers"],
            data.get("discount", 0),
            data.get("sold", False),
        )

        fs.create_flight(flight)
        return jsonify({"message": "Flight created"}), 201

    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "detail": traceback.format_exc()
        }), 500


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


# ===============================
# POST /flights/insert  - single insert with multi-insert
# ===============================


@main_routes.route("/flights/insert", methods=["POST"])
def insert_flight():
    """
    Endpoint for insert one flight with multi-insert.
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

    # Call to multi_inserts with a list of just an element
    reports = flight_service.multi_inserts([flight])
    return jsonify(reports[0]), 200  # Return only the report of the flight


# ===============================
# GET /metrics  - Obtain metrcis
# ===============================


@main_routes.route("/metrics", methods=["GET"])
def get_metrics():
    """Return real-time metrics for the current flight tree."""
    metrics_data = metrics_service.getRealTimeMetrics()

    # Return the collected metrics as JSON.
    return jsonify(metrics_data)


# ===============================
# PUT /config/max-depth  - Config limit height for the penalitation sistem
# ===============================


@main_routes.route("/config/max-depth", methods=["PUT"])
def set_max_depth():
    """Update the maximum depth threshold used for depth penalty pricing."""
    data = request.get_json()
    flight_service.setMaxDepth(data["maxDepth"])
    return jsonify(
        {"message": "Depth penalty configuration updated and prices recalculated."}
    )


# ===============================
# DELETE /flights/lowest-profitability - Inteligent elimination by economic impact
# ===============================


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


# ===============================
# Get /tree/render - Get render of the tree
# ===============================
#
@main_routes.route("/tree/render", methods=["GET"])
def render_tree():
    try:
        renderer = TreeRenderer(flight_service._tree)
        image = renderer.render()
        return jsonify({"image": image}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_routes.route("/tree/traversal/type", methods=["GET"])
def dfs_traversal():
    return jsonify({
        "inorder": flight_service.get_traversal("inorder"),
        "preorder": flight_service.get_traversal("preorder"),
        "postorder": flight_service.get_traversal("postorder"),
        "levelorder": flight_service.get_traversal("levelorder"),
    })