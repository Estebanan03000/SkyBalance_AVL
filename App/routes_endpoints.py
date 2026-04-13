"""
Additional endpoints para SkyBalance_AVL
Se importan en app.py con: from App.routes_endpoints import additional_routes
"""

from flask import Blueprint, request, jsonify
from App.Models.Flight import Flight

additional_routes = Blueprint("additional", __name__)

# Esta función necesita recibir flight_service desde app.py
_flight_service = None

def init_endpoints(flight_service):
    """Inicializar endpoints con referencia a flight_service"""
    global _flight_service
    _flight_service = flight_service


def _get_flight_service():
    """Return the live Flight_Service instance used by main routes."""
    try:
        from App.routes import flight_service as live_flight_service

        return live_flight_service
    except Exception:
        return _flight_service


# ===============================
# PUT /config/mode - Change tree mode (Stress=BST or Global Balance=AVL)
# ===============================
@additional_routes.route("/config/mode", methods=["PUT"])
def change_mode():
    """
    Switch between Stress mode (BST) and Global Balance mode (AVL).
    
    Expected JSON body:
        {"mode": "Stress"} or {"mode": "Global Balance"}
    """
    try:
        data = request.get_json()
        mode = data.get("mode", "Global Balance")
        
        if mode not in ["Stress", "Global Balance"]:
            return jsonify({"error": "Mode must be 'Stress' or 'Global Balance'"}), 400
        
        flight_service = _get_flight_service()
        flight_service.set_mode(mode)
        flight_service._mode = mode
        
        return jsonify({
            "message": f"✅ Árbol cambiado a modo {mode}",
            "mode": mode
        }), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error al cambiar modo: {str(e)}"}), 400


# ===============================
# GET /tree/verify - Verify AVL properties
# ===============================
@additional_routes.route("/tree/verify", methods=["GET"])
def verify_tree():
    """
    Verify if the current tree is balanced (AVL property).
    
    Returns information about balance status and any inconsistent nodes.
    """
    try:
        flight_service = _get_flight_service()
        root = flight_service._tree.getRoot()
        
        if root is None:
            return jsonify({
                "balanced": True,
                "mode": flight_service._mode,
                "inconsistent_nodes": []
            }), 200
        
        inconsistent_nodes = []
        
        # Check AVL property: balance factors should be -1, 0, or 1
        def check_balance(node):
            if node is None:
                return True
            
            left = node.getLeftChild()
            right = node.getRightChild()
            
            left_height = left.getHeight() if left else 0
            right_height = right.getHeight() if right else 0
            balance_factor = left_height - right_height
            
            if abs(balance_factor) > 1:
                inconsistent_nodes.append({
                    "id": node.getValue(),
                    "balance_factor": balance_factor
                })
            
            return check_balance(left) and check_balance(right)
        
        is_balanced = check_balance(root)
        
        return jsonify({
            "balanced": is_balanced,
            "mode": flight_service._mode,
            "inconsistent_nodes": inconsistent_nodes
        }), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error en verificación: {str(e)}"}), 400


# ===============================
# GET /tree/traverse - Tree traversal (DFS, BFS, INORDER, POSTORDER)
# ===============================
@additional_routes.route("/tree/traverse", methods=["GET"])
def traverse_tree():
    """
    Perform tree traversal and return the nodes in traversal order.
    
    Query parameters:
        type: "DFS", "BFS", "INORDER", "POSTORDER" (default: DFS)
    """
    try:
        traverse_type = request.args.get("type", "DFS").upper()
        flight_service = _get_flight_service()
        tree = flight_service._tree
        result_nodes = []
        
        if traverse_type == "DFS":
            # DFS: Use preOrder traversal
            flights = tree.preOrderTraversal() or []
            result_nodes = [f.getValue() for f in flights]
            order = "DFS (Pre-Order)"
        
        elif traverse_type == "BFS":
            # BFS: Breadth-first search
            flights = tree.breadthFirstSearch() or []
            result_nodes = [f.getValue() for f in flights]
            order = "BFS"
        
        elif traverse_type == "INORDER":
            # Inorder traversal
            flights = tree.inOrderTraversal() or []
            result_nodes = [f.getValue() for f in flights]
            order = "InOrder"
        
        elif traverse_type == "POSTORDER":
            # Postorder traversal
            flights = tree.posOrderTraversal() or []
            result_nodes = [f.getValue() for f in flights]
            order = "PostOrder"
        
        else:
            return jsonify({"error": "Unknown traversal type. Use DFS, BFS, INORDER, or POSTORDER"}), 400
        
        return jsonify({
            "order": order,
            "nodes": result_nodes,
            "count": len(result_nodes)
        }), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error en traversal: {str(e)}"}), 400


# ===============================
# POST /tree/undo - Undo the last operation
# ===============================
@additional_routes.route("/tree/undo", methods=["POST"])
def undo_operation():
    """
    Undo the last tree operation (insertion or deletion).
    """
    try:
        flight_service = _get_flight_service()
        result = flight_service.undo()
        
        if result:
            operation, flight_id = result
            return jsonify({
                "message": f"✅ Operación '[{operation}] Vuelo {flight_id}' deshecha",
                "operation": operation,
                "flight_id": flight_id
            }), 200
        else:
            return jsonify({
                "message": "⚠️ No hay operaciones para deshacer",
                "operation": None,
                "flight_id": None
            }), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error en undo: {str(e)}"}), 400


# ===============================
# POST /tree/cancel-subtree - Cancel (delete) a subtree
# ===============================
@additional_routes.route("/tree/cancel-subtree", methods=["POST"])
def cancel_subtree():
    """
    Cancel a subtree rooted at the given flight ID.
    All nodes under that root will be deleted.
    
    Expected JSON body:
        {"id": flight_id}
    """
    try:
        data = request.get_json()
        root_id = data.get("id")
        
        if not root_id:
            return jsonify({"error": "ID is required"}), 400
        
        # Find the root flight
        flight_service = _get_flight_service()
        root_flight = flight_service.get_flight(root_id)
        
        if not root_flight:
            return jsonify({"error": f"❌ Vuelo {root_id} no encontrado"}), 404
        
        # Collect all node IDs in the subtree
        deleted_ids = []
        
        def collect_subtree(node):
            if node is None:
                return
            deleted_ids.append(node.getValue())
            collect_subtree(node.getLeftChild())
            collect_subtree(node.getRightChild())
        
        collect_subtree(root_flight)
        
        # Delete each node (in reverse order to avoid issues)
        for node_id in reversed(deleted_ids):
            try:
                flight_service.delete_flight(node_id)
            except:
                pass
        
        # Apply depth penalties after mass deletion
        flight_service.applyDepthPenalty()
        
        return jsonify({
            "message": f"✅ Subárbol cancelado",
            "deleted_count": len(deleted_ids),
            "deleted_ids": deleted_ids
        }), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error al cancelar subárbol: {str(e)}"}), 400


# ===============================
# POST /queue/process - Process queue of flights
# ===============================
@additional_routes.route("/queue/process", methods=["POST"])
def process_queue():
    """
    Process a queue of flights for batch insertion.
    
    Expected JSON body:
        {"flights": [{"id": ..., "origin": ..., ...}, ...]}
    """
    try:
        data = request.get_json()
        flights_data = data.get("flights", [])
        
        if not flights_data:
            return jsonify({
                "message": "Cola vacía",
                "processed": 0,
                "reports": []
            }), 200
        
        # Build Flight objects
        flights_to_insert = []
        for f_data in flights_data:
            try:
                flight = Flight(
                    id=f_data.get("id") or f_data.get("codigo"),
                    origin=f_data.get("origin") or f_data.get("origen"),
                    destiny=f_data.get("destiny") or f_data.get("destino"),
                    departureTime=f_data.get("departureTime") or f_data.get("horaSalida"),
                    basePrice=f_data.get("basePrice") or f_data.get("precioBase"),
                    finalPrice=f_data.get("finalPrice") or f_data.get("precioFinal") or f_data.get("precioBase"),
                    passengers=f_data.get("passengers") or f_data.get("pasajeros"),
                    promotion=(
                        f_data.get("promotion")
                        if f_data.get("promotion") is not None
                        else f_data.get("promocion", False)
                    ),
                    alert=(
                        f_data.get("alert")
                        if f_data.get("alert") is not None
                        else f_data.get("alerta", False)
                    ),
                )
                flights_to_insert.append(flight)
            except:
                pass
        
        # Insert all flights
        flight_service = _get_flight_service()
        reports = flight_service.multi_inserts(flights_to_insert)
        
        return jsonify({
            "message": f"✅ Cola procesada: {len(reports)} vuelos insertados",
            "processed": len(reports),
            "reports": reports
        }), 200
    except Exception as e:
        return jsonify({"error": f"❌ Error al procesar cola: {str(e)}"}), 400
