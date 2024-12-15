from flask import Flask
from services.routes import setup_routes

app = Flask(__name__)

# Route'ları yükle
setup_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
