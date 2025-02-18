import random
import string
from datetime import datetime, timedelta
from flask import jsonify
import africastalking
from model import db
from model import PasswordReset
from flask_jwt_extended import jwt_required

# Africa's Talking Setup (do not re-initialize here, it should be done in app.py)
sms = africastalking.SMS

# Generate reset token
def generate_reset_token(length=6):
    """Generate a random token for password reset."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Send SMS with reset token
def send_sms(phone_number, token):
    """Send the reset token to the user's phone number."""
    message = f"Your password reset token is: {token}. It expires in 10 minutes."
    try:
        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        return {"error": str(e)}

# Request password reset - handles generating a token and sending it via SMS
@jwt_required()
def request_password_reset(phone_number, user_id):
    """Request a password reset token by providing the user's phone number."""
    if not phone_number:
        return jsonify({"message": "Phone number is required"}), 400

    # Generate the reset token
    token = generate_reset_token()
    expiration_time = datetime.utcnow() + timedelta(minutes=10)  # Token expires in 10 minutes

    # Save the reset token in the database
    password_reset = PasswordReset(user_id=user_id, token=token, expiration=expiration_time)
    db.session.add(password_reset)
    db.session.commit()

    # Send the reset token via SMS
    response = send_sms(phone_number, token)
    if "error" in response:
        return jsonify({"message": "Failed to send SMS", "error": response["error"]}), 500

    return jsonify({"message": "Password reset token sent successfully"}), 200
