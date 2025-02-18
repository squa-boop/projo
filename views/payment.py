from flask import Blueprint, request, jsonify
from model import db, Product
from flask_jwt_extended import jwt_required, get_jwt_identity

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/calculate-total-cost', methods=['POST'])
@jwt_required()
def calculate_total_cost():
    """
    Calculate the total cost of a product including delivery.
    """
    data = request.json
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({"message": "Product ID is required"}), 400

    # Fetch product details from the database
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    # Calculate total cost (product price + delivery cost)
    total_cost = product.product_price + product.delivery_cost

    return jsonify({
        "product_name": product.product_name,
        "product_price": product.product_price,
        "delivery_cost": product.delivery_cost,
        "total_cost": total_cost
    }), 200


@payment_bp.route('/process-payment', methods=['POST'])
@jwt_required()
def process_payment():
    """
    Simulate processing a payment for a product.
    """
    data = request.json
    product_id = data.get('product_id')
    payment_mode = data.get('payment_mode')  # e.g., 'Pay before delivery', 'Pay after delivery'

    if not product_id or not payment_mode:
        return jsonify({"message": "Product ID and Payment Mode are required"}), 400

    # Fetch product details from the database
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404

    # Validate payment mode
    if payment_mode != product.payment_mode:
        return jsonify({"message": f"Invalid payment mode. Expected: {product.payment_mode}"}), 400

    # Simulate payment processing
    if payment_mode == 'Pay before delivery':
        return jsonify({
            "message": "Payment processed successfully. Delivery will follow.",
            "product_name": product.product_name,
            "product_price": product.product_price
        }), 200
    elif payment_mode == 'Pay after delivery':
        return jsonify({
            "message": "Order placed successfully. Payment due upon delivery.",
            "product_name": product.product_name,
            "product_price": product.product_price
        }), 200

    return jsonify({"message": "Payment mode not supported"}), 400
