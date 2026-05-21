"""Main Flask routes for flight management, tree visualization, and metrics."""

from flask import Blueprint, request, jsonify
from App.Services.Flight_Service import Flight_Service
from App.Models.Flight import Flight
from datetime import datetime
from App.Services.Metrics_Service import Metrics_Service
from App.Utils.Tree_Render import TreeRenderer
from App.Utils.JSON_Handler import JSONHandler
from App.Utils.id_utils import normalize_flight_id as _normalize_flight_id
from App.Models.Stack import Stack
from App.Models.Flight import Flight as flight_model

# Keep the service instances in memory while the Flask app is running.
flight_service = Flight_Service()
metrics_service = Metrics_Service(flight_service)

# Group the main application routes in a dedicated blueprint.
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
        _normalize_flight_id(data.get("id") or data.get("codigo") or data.get("code")),
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


def _flatten_topology_nodes(root_payload):
    """Flatten topology-like JSON into a list of node payloads (preorder)."""
    nodes = []

    def walk(node):
        if not isinstance(node, dict):
            return

        has_id = any(k in node for k in ["id", "code", "codigo"])
        if has_id:
            nodes.append(node)

        left = node.get("left") if "left" in node else node.get("izquierdo")
        right = node.get("right") if "right" in node else node.get("derecho")

        if isinstance(left, dict):
            walk(left)
        if isinstance(right, dict):
            walk(right)

    walk(root_payload)
    return nodes


def _normalize_json_to_flights(json_data):
    """Normalize any supported JSON format into a list of Flight instances."""
    raw_nodes = []

    if isinstance(json_data, list):
        raw_nodes = [item for item in json_data if isinstance(item, dict)]
    elif isinstance(json_data, dict):
        if isinstance(json_data.get("flights"), list):
            raw_nodes = [item for item in (json_data.get("flights") or []) if isinstance(item, dict)]
        elif isinstance(json_data.get("vuelos"), list):
            raw_nodes = [item for item in (json_data.get("vuelos") or []) if isinstance(item, dict)]
        elif any(k in json_data for k in ["id", "code", "codigo"]):
            raw_nodes = _flatten_topology_nodes(json_data)

    if not raw_nodes:
        raise ValueError("Unrecognized JSON format for flights")

    normalized_flights = []
    seen_ids = set()

    for item in raw_nodes:
        flight_id = _normalize_flight_id(item.get("id") or item.get("code") or item.get("codigo"))
        if flight_id in seen_ids:
            continue

        date_value = item.get("date") or item.get("departureTime") or item.get("horaSalida")
        base_price = item.get("basePrice") or item.get("precioBase") or 0
        final_price = item.get("finalPrice") or item.get("precioFinal") or base_price

        flight = Flight(
            id=flight_id,
            origin=item.get("origin") or item.get("origen"),
            destiny=item.get("destiny") or item.get("destino"),
            departureTime=date_value,
            basePrice=base_price,
            finalPrice=final_price,
            passengers=item.get("passengers") or item.get("pasajeros") or 0,
            promotion=(
                item.get("promotion")
                if item.get("promotion") is not None
                else item.get("promocion", item.get("discount", 0))
            ),
            alert=(
                item.get("alert")
                if item.get("alert") is not None
                else item.get("alerta", item.get("sold", False))
            ),
        )

        normalized_flights.append(flight)
        seen_ids.add(flight_id)

    return normalized_flights


@main_routes.route("/flights/load", methods=["POST"])
def load_flights():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400

       
        import App.routes as current_module
        fs = current_module.flight_service
        # Reset only the tree and history, keep versions intact
        from App.Models.AVL import AVL
        fs._tree = AVL()
        from App.Models.Stack import Stack
        fs._history = Stack()
        fs._max_depth = None
        fs._mode = "Normal"
        current_module.metrics_service = Metrics_Service(fs)

        flights = _normalize_json_to_flights(data)
        for flight in flights:
            fs._tree.insert(flight)

        fs.applyDepthPenalty()
        root = fs._tree.getRoot()

        return jsonify({
            "mode": "normalized",
            "loaded_count": len(flights),
            "avl": {
                "root": root.getValue() if root else None,
                "depth": fs._tree.getDepth(),
                "leaves": fs._tree.countLeaves(),
            },
        }), 200

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
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        flight = Flight(
            _normalize_flight_id(data.get("id") or data.get("codigo") or data.get("code")),
            data.get("origin") or data.get("origen"),
            data.get("destiny") or data.get("destino"),
            datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S"),
            data.get("basePrice") or data.get("precioBase"),
            data.get("finalPrice") or data.get("precioFinal") or data.get("basePrice") or data.get("precioBase"),
            data.get("passengers") or data.get("pasajeros"),
            data.get("discount", data.get("promotion", data.get("promocion", 0))),
            data.get("sold", data.get("alert", data.get("alerta", False))),
        )
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": f"Invalid flight payload: {error}"}), 400

    try:
        # Always use the live module-level instance that all routes share.
        import App.routes as current_module

        current_module.flight_service.create_flight(flight)
        current_module.flight_service.applyDepthPenalty()
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
    
    Supports two export modes:
    1. "insertion" - Export as array of flights (for re-insertion)
    2. "topology" - Export as tree structure (preserves exact topology)

    The exported JSON preserves the hierarchical parent-child structure,
    node heights, balance factors (for AVL), and all flight details.

    Expects JSON in request body:
        - filename: Name or path of the JSON file to create
                    Example: "tree_backup.json"
        - mode: "insertion" or "topology" (default: "topology")

    Returns:
        JSON message confirming successful export, or an error message.
    """
    try:
        data = request.get_json()
        filename = data.get("filename", "tree_export.json")
        mode = data.get("mode", "topology")  # Default to topology

        # Get all flights or tree root based on mode
        if mode == "insertion":
            # Export all flights as an array (in order)
            flights_list = flight_service.get_all_flights()
            export_data = JSONHandler.export_insertion_mode(flights_list)
        else:  # topology mode (default)
            # Export tree structure as-is
            root = flight_service._tree.getRoot()
            export_data = JSONHandler.export_topology_mode(root)

        # Save to file
        JSONHandler.save_to_file(export_data, filename)

        return (
            jsonify({"message": f"✅ Árbol exportado exitosamente a {filename} (Modo: {mode})"}),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"❌ Error en exportación: {str(e)}"}), 400


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
        view_mode = request.args.get("view", "ACTIVE")
        tree_for_view = flight_service.get_visualization_tree(view_mode)
        renderer = TreeRenderer(tree_for_view)
        image = renderer.render()
        return jsonify({"image": image, "view": view_mode}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_routes.route("/tree/state", methods=["GET"])
def tree_state():
    """Return the current tree as serialized JSON for frontend fallback rendering."""
    try:
        view_mode = request.args.get("view", "ACTIVE")
        tree = flight_service.get_visualization_tree(view_mode)
        return jsonify({
            "mode": flight_service._mode,
            "view": view_mode,
            "tree": tree.serialize_to_dict() if tree else None,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================
# POST /versions — Save a version
# ===============================
@main_routes.route("/versions", methods=["POST"])
def save_version():
    """Saves the current tree state with a given name."""
    import App.routes as current_module
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Field 'name' is required"}), 400
    try:
        current_module.flight_service.save_version(name)
        return jsonify({"message": f"Version '{name}' saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ===============================
# GET /versions — List versions
# ===============================
@main_routes.route("/versions", methods=["GET"])
def list_versions():
    """Returns the names of all saved versions."""
    import App.routes as current_module
    return jsonify(current_module.flight_service.list_versions())


# ===============================
# PUT /versions/<name>/restore — Restore a version
# ===============================
@main_routes.route("/versions/<string:name>/restore", methods=["PUT"])
def restore_version(name):
    """Restores the tree to the state of the given version."""
    import App.routes as current_module
    try:
        current_module.flight_service.restore_version(name)
        return jsonify({"message": f"Version '{name}' restored"})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@main_routes.route("/tree/traversal/type", methods=["GET"])
def dfs_traversal():
    return jsonify({
        "inorder": flight_service.get_traversal("inorder"),
        "preorder": flight_service.get_traversal("preorder"),
        "postorder": flight_service.get_traversal("postorder"),
        "levelorder": flight_service.get_traversal("levelorder"),
    })


