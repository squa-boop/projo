from flask import Blueprint, request, jsonify
from model import FilterPreference, db
from sqlalchemy.sql import text

filter_bp = Blueprint('filter', __name__)

@filter_bp.route('/set-preference', methods=['POST'])
def set_preference():
    """
    Set or update a user's filter preferences.
    """
    data = request.json
    user_id = data.get('user_id')  # The user ID is passed in the request
    preference_key = data.get('key')
    preference_value = data.get('value')

    # Validate incoming data
    if not user_id or not preference_key or not preference_value:
        return jsonify({"message": "User ID, preference key, and preference value are required"}), 400

    # Check if preference already exists in the database
    preference = FilterPreference.query.filter_by(user_id=user_id, preference_key=preference_key).first()

    if preference:
        preference.preference_value = preference_value  # Update the preference
    else:
        # Add a new preference if not found
        preference = FilterPreference(user_id=user_id, preference_key=preference_key, preference_value=preference_value)
        db.session.add(preference)

    db.session.commit()
    return jsonify({"message": "Preference updated successfully"}), 200


@filter_bp.route('/apply-filters', methods=['GET'])
def apply_filters():
    """
    Apply filter preferences and sort the products accordingly.
    """
    data = request.args  # Query parameters are used for filtering
    user_id = data.get('user_id')

    # Validate user_id
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    # Fetch user preferences from the database
    preferences = FilterPreference.query.filter_by(user_id=user_id).all()

    # Initialize the base SQL query
    query = text("SELECT * FROM products")

    # Define a dictionary to map preference values to SQL sort directions
    sort_map = {
        'ascending': 'ASC',
        'descending': 'DESC'
    }

    # Apply filters dynamically based on user preferences
    for pref in preferences:
        if pref.preference_key in ['price', 'rating']:
            # Get the sort order from the map, default to 'ASC' if invalid
            sort_order = sort_map.get(pref.preference_value, 'ASC')
            query = query.order_by(text(f"{pref.preference_key} {sort_order}"))

    # Execute the query and fetch results
    results = db.session.execute(query).fetchall()

    # Return the results as a list of dictionaries
    return jsonify([dict(row) for row in results]), 200
