from flask import Blueprint, request, jsonify
from model import Product, RankedProduct, db

product_bp = Blueprint('product', __name__)

def calculate_mb_cb_scores(product):
    """
    Calculates MB (Marketability) and CB (Customer Benefit) scores for a product.
    """
    # Example calculation (you can adjust this logic)
    mb_score = product['product_rating'] * 10 + product['num_ratings'] / 10
    cb_score = product['product_price'] / product['delivery_cost']
    return mb_score, cb_score

@product_bp.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query:
        return jsonify({"message": "Query parameter is required"}), 400

    # Simulate crawling e-commerce APIs (e.g., Amazon, eBay, Shopify, Alibaba)
    products = [
        {"product_name": "Samsung A51", "product_price": 30098, "product_rating": 4.7, "num_ratings": 10, "delivery_cost": 200, "payment_mode": "Pay after delivery", "shop_name": "Jumia", "product_url": "https://jumia.com/samsung-a51"},
        {"product_name": "Samsung A51", "product_price": 29999, "product_rating": 4.0, "num_ratings": 4, "delivery_cost": 150, "payment_mode": "Pay before delivery", "shop_name": "Kill Mall", "product_url": "https://killmall.com/samsung-a51"},
    ]

    # Save products to database
    for product in products:
        existing_product = Product.query.filter_by(product_name=product['product_name'], shop_name=product['shop_name']).first()
        if not existing_product:
            new_product = Product(
                product_name=product['product_name'],
                product_price=product['product_price'],
                product_rating=product['product_rating'],
                num_ratings=product['num_ratings'],
                delivery_cost=product['delivery_cost'],
                payment_mode=product['payment_mode'],
                shop_name=product['shop_name'],
                product_url=product['product_url']
            )
            db.session.add(new_product)
    db.session.commit()

    # Calculate MB/CB scores and rank products
    ranked_products = []
    for product in products:
        mb_score, cb_score = calculate_mb_cb_scores(product)
        ranked_product = RankedProduct(
            product_id=product['id'],
            mb_score=mb_score,
            cb_score=cb_score,
            rank=1  # Rank will be updated later
        )
        ranked_products.append(ranked_product)

    # Sort by MB score descending
    ranked_products.sort(key=lambda x: x.mb_score, reverse=True)
    for i, rp in enumerate(ranked_products):
        rp.rank = i + 1

    db.session.add_all(ranked_products)
    db.session.commit()

    return jsonify([rp.to_dict() for rp in ranked_products]), 200
