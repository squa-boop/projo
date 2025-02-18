import os
from flask import Flask
from flask_migrate import Migrate
from model import db
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_cors import CORS
import africastalking
from flask_bcrypt import Bcrypt  # Import Bcrypt

# Initialize Flask app
app = Flask(__name__)

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# Database configuration (SQLite instead of PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable SQLAlchemy track modifications

# JWT configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
jwt = JWTManager(app)

# Initialize db and migrate
db.init_app(app)
migrate = Migrate(app, db)

# Enable CORS globally
CORS(app)

# Africa's Talking configuration
africastalking.initialize(
    username=os.getenv("blessing"),
    api_key=os.getenv("atsk_89ef57f9358c238ea8e31ac2a5695096abd2bd649ae96f7f2f7813c0f2219aac1b67529c")
)

# Register blueprints (make sure the import paths are correct)
from views.filtering_sorting import filtering_sorting_bp  # Correct import
from views.africastalking_setup import africastalking_setup_bp  # Correct import
from views.Auth import auth_bp
from views.payment import payment_bp
from views.product import product_bp
from views.search import search_bp
from views.user import user_bp

# Register blueprints with the app
app.register_blueprint(auth_bp)
app.register_blueprint(filtering_sorting_bp)  # Registering the blueprint
app.register_blueprint(payment_bp)
app.register_blueprint(product_bp)
app.register_blueprint(search_bp)
app.register_blueprint(user_bp)
app.register_blueprint(africastalking_setup_bp)  # Registering the blueprint

if __name__ == "__main__":
    app.run(debug=True)
