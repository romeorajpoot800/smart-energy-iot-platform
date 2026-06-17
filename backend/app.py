"""
Smart Energy Monitoring System - Flask API Server
"""

from flask import Flask
from flask_cors import CORS
from backend.database import create_tables, create_admin

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
create_tables()
create_admin()


# ==================== Routes ====================

@app.route("/")
def home():
    return {"message": "Smart Energy Monitoring API", "status": "running"}


@app.route("/health")
def health():
    return {"status": "healthy"}


# Import and register blueprints
from backend.routes import sensor_routes, device_routes, alert_routes, user_routes

app.register_blueprint(sensor_routes.bp)
app.register_blueprint(device_routes.bp)
app.register_blueprint(alert_routes.bp)
app.register_blueprint(user_routes.bp)


if __name__ == "__main__":
    print("Starting Smart Energy Monitoring API...")
    print("API available at: http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
