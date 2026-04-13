from flask import Flask
from App.routes import main_routes
from App.routes_endpoints import additional_routes, init_endpoints
from App.Services.Flight_Service import Flight_Service

# Create the Flask application and configure the static asset folder.
# The static folder is set to the frontend presentation directory so that
# CSS, JS, and HTML files can be served from the same location.
app = Flask(__name__, static_folder="./Presentation", static_url_path="")

# Register the blueprint that contains the application's API routes.
app.register_blueprint(main_routes)
app.register_blueprint(additional_routes)

# Initialize additional endpoints with flight_service reference once at startup.
from App.routes import flight_service
init_endpoints(flight_service)


@app.route("/")
def home():
    # Serve the main frontend page when the root URL is requested.
    return app.send_static_file("View/index.html")


if __name__ == "__main__":
    # Start the Flask development server.
    app.run(debug=True)
