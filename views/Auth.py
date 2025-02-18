from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from model import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if any required fields are missing
    if not email or not password or not username:
        return jsonify({"message": "Missing required fields"}), 400

    # Check if email already exists in the database
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()  # Ensure rollback if there's an error
        return jsonify({"message": "Database error: " + str(e)}), 500

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Check if any required fields are missing
    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200


@auth_bp.route('/social-login', methods=['POST'])
def social_login():
    data = request.json
    provider = data.get('provider')
    token = data.get('token')

    if not provider or not token:
        return jsonify({"message": "Provider and token are required"}), 400

    # Validate token with the provider
    if provider == 'google':
        # You can implement Google OAuth token validation here if needed
        return jsonify({"message": "Social login with Google is not implemented"}), 400

    return jsonify({"message": "Unsupported provider"}), 400
