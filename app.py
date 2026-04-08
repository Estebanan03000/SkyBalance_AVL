from flask import Flask
from App.Routes import main_routes

app = Flask(__name__)

# Registrar el blueprint con todas las rutas
app.register_blueprint(main_routes)


@app.route("/")
def home():
    return {"message": "API funcionando"}


if __name__ == "__main__":
    app.run(debug=True)
