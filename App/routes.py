from flask import Blueprint, request, jsonify
from Services import Flight_Service
from Models import Flight
from datetime import datetime

# Create an instance of the Flight_Service
# This instance will remain in memory while the app is running
flight_service = Flight_Service()

# Create a Flask blueprint to organize routes
main_routes = Blueprint("main", __name__)

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
            "passengers": f.getPassengers()
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
        data.get("sold", False)
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
        return jsonify({"message": "Flight deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 404