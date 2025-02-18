from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, decode_token
from model import SearchHistory, db
import jwt  # import the JWT package directly for decoding

history_bp = Blueprint('history', __name__)

def get_user_id_from_jwt(token):
    """Decodes the JWT token and retrieves the user_id."""
    try:
        # Decode the JWT token to get the payload
        decoded_token = jwt.decode(token, options={"verify_signature": False})  # Assuming you don't verify the signature here
        return decoded_token.get('sub')  # assuming 'sub' is the user ID in the JWT
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

@history_bp.route('/save-history', methods=['POST'])
def save_history():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token is missing"}), 400

    token = token.split(' ')[1]  # Remove 'Bearer ' from the token
    user_id = get_user_id_from_jwt(token)

    if not user_id:
        return jsonify({"message": "Invalid or expired token"}), 401

    data = request.json
    query = data.get('query')

    new_history = SearchHistory(user_id=user_id, query=query)
    db.session.add(new_history)
    db.session.commit()

    return jsonify({"message": "Search history saved"}), 200


@history_bp.route('/get-history', methods=['GET'])
def get_history():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Token is missing"}), 400

    token = token.split(' ')[1]  # Remove 'Bearer ' from the token
    user_id = get_user_id_from_jwt(token)

    if not user_id:
        return jsonify({"message": "Invalid or expired token"}), 401

    history = SearchHistory.query.filter_by(user_id=user_id).order_by(SearchHistory.timestamp.desc()).all()
    return jsonify([h.to_dict() for h in history]), 200
