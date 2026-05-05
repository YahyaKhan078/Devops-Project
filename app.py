from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Serve frontend
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/frontend/<path:filename>')
def frontend_files(filename):
    return send_from_directory('frontend', filename)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Flask Backend API",
        "version": "1.0.0"
    }), 200

# GET endpoint - Get all products
@app.route('/api/products', methods=['GET'])
def get_products():
    products = [
        {"id": 1, "name": "T-Shirt", "price": 19.99, "category": "Clothing"},
        {"id": 2, "name": "Jeans", "price": 49.99, "category": "Clothing"},
        {"id": 3, "name": "Shoes", "price": 79.99, "category": "Footwear"}
    ]
    return jsonify({
        "products": products,
        "total": len(products)
    }), 200

# GET single product
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    products = {
        1: {"id": 1, "name": "T-Shirt", "price": 19.99, "category": "Clothing"},
        2: {"id": 2, "name": "Jeans", "price": 49.99, "category": "Clothing"},
        3: {"id": 3, "name": "Shoes", "price": 79.99, "category": "Footwear"}
    }
    
    if product_id not in products:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify(products[product_id]), 200

# POST endpoint - Create new product
@app.route('/api/products', methods=['POST'])
def create_product():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    if 'name' not in data:
        return jsonify({"error": "Product name is required"}), 400
    
    if 'price' not in data:
        return jsonify({"error": "Product price is required"}), 400
    
    new_product = {
        "id": 4,
        "name": data['name'],
        "price": data['price'],
        "category": data.get('category', 'Uncategorized')
    }
    
    return jsonify({
        "message": "Product created successfully",
        "product": new_product
    }), 201

# PUT endpoint - Update product
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    if product_id < 1 or product_id > 3:
        return jsonify({"error": "Product not found"}), 404
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    updated_product = {
        "id": product_id,
        "name": data.get('name', f"Product {product_id}"),
        "price": data.get('price', 0),
        "category": data.get('category', 'Uncategorized')
    }
    
    return jsonify({
        "message": f"Product {product_id} updated",
        "product": updated_product
    }), 200

# DELETE endpoint
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    if product_id < 1 or product_id > 3:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify({
        "message": f"Product {product_id} deleted successfully"
    }), 200

# 404 handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
