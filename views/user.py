from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from model import db, User, SearchHistory

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    """
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"message": "Username, email, and password are required"}), 400

    # Check if the user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Create a new user
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@user_bp.route('/login', methods=['POST'])
def login():
    """
    Log in a user and generate a JWT token.
    """
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Find the user by email
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200


@user_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update the user's profile information.
    """
    user_id = get_jwt_identity()
    data = request.json
    username = data.get('username')
    profile_picture = data.get('profile_picture')

    # Find the user
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Update user details
    if username:
        user.username = username
    if profile_picture:
        user.profile_picture = profile_picture

    db.session.commit()

    return jsonify({"message": "Profile updated successfully"}), 200


@user_bp.route('/save-search-history', methods=['POST'])
@jwt_required()
def save_search_history():
    """
    Save a user's search query to their search history.
    """
    user_id = get_jwt_identity()
    data = request.json
    search_query = data.get('search_query')

    if not search_query:
        return jsonify({"message": "Search query is required"}), 400

    # Save the search query to the database
    new_search = SearchHistory(user_id=user_id, search_query=search_query)
    db.session.add(new_search)
    db.session.commit()

    return jsonify({"message": "Search history saved successfully"}), 200


@user_bp.route('/get-search-history', methods=['GET'])
@jwt_required()
def get_search_history():
    """
    Retrieve a user's search history.
    """
    user_id = get_jwt_identity()

    # Fetch the user's search history
    search_history = SearchHistory.query.filter_by(user_id=user_id).all()
    history_list = [{"id": sh.id, "search_query": sh.search_query, "search_date": sh.search_date} for sh in search_history]

    return jsonify(history_list), 200