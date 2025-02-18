from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

# Initialize db
db = SQLAlchemy()

# Initialize bcrypt
bcrypt = Bcrypt()

# User Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_picture = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    search_history = db.relationship('SearchHistory', backref='user', lazy=True)
    auth_tokens = db.relationship('AuthToken', backref='user', lazy=True)

    def set_password(self, password):
        # Use bcrypt to hash the password
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        # Use bcrypt to check the password
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Search History Model (for user searches)
class SearchHistory(db.Model):
    __tablename__ = 'search_history'

    id = db.Column(db.Integer, primary_key=True)
    search_query = db.Column(db.String(255), nullable=False)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<SearchHistory {self.search_query}>'

# Product Model (represents products from e-commerce sites)
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    product_rating = db.Column(db.Float, nullable=True)
    product_url = db.Column(db.String(512), nullable=False)
    delivery_cost = db.Column(db.Float, nullable=False)
    shop_name = db.Column(db.String(100), nullable=False)  # e.g., 'Jumia', 'eBay', etc.
    payment_mode = db.Column(db.String(50), nullable=False)  # Pay before delivery / Pay after delivery
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.product_name}>'

# Product Search Model (temporary index of product search results)
class ProductSearch(db.Model):
    __tablename__ = 'product_searches'

    id = db.Column(db.Integer, primary_key=True)
    search_query = db.Column(db.String(255), nullable=False)
    query_results = db.Column(db.JSON, nullable=False)  # JSON for storing search results dynamically
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProductSearch {self.search_query}>'

# Authentication Tokens Model (JWT token storage)
class AuthToken(db.Model):
    __tablename__ = 'auth_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    # Relationship
    user = db.relationship('User', backref='auth_tokens', lazy=True)

    def __repr__(self):
        return f'<AuthToken {self.token[:10]}>'

# Price History Model (tracks price changes over time)
class PriceHistory(db.Model):
    __tablename__ = 'price_history'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    old_price = db.Column(db.Float, nullable=False)
    new_price = db.Column(db.Float, nullable=False)
    change_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    product = db.relationship('Product', backref='price_history', lazy=True)

    def __repr__(self):
        return f'<PriceHistory {self.old_price} -> {self.new_price}>'

# Ranked Product Model (stores ranking, MB, CB scores)
class RankedProduct(db.Model):
    __tablename__ = 'ranked_products'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    mb_score = db.Column(db.Float, nullable=False)
    cb_score = db.Column(db.Float, nullable=False)
    rank = db.Column(db.Integer, nullable=False)

    # Relationship
    product = db.relationship('Product', backref='ranked_products', lazy=True)

    def __repr__(self):
        return f'<RankedProduct {self.product.product_name} - Rank {self.rank}>'

    def to_dict(self):
        return {
            "product_name": self.product.product_name,
            "product_price": self.product.product_price,
            "product_rating": self.product.product_rating,
            "shop_name": self.product.shop_name,
            "rank": self.rank,
            "mb_score": self.mb_score,
            "cb_score": self.cb_score
        }
