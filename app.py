from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes so the frontend can call this API

# ---------------------------------------------------------------------------
# In-memory data store  (no database needed for the DevOps lab)
# ---------------------------------------------------------------------------
products = [
    {"id": 1, "name": "Slim Fit Jeans",      "category": "Bottoms", "price": 2499, "stock": 20},
    {"id": 2, "name": "Polo Shirt",           "category": "Tops",    "price": 1299, "stock": 15},
    {"id": 3, "name": "Denim Jacket",         "category": "Jackets", "price": 3999, "stock": 8},
    {"id": 4, "name": "Cargo Shorts",         "category": "Bottoms", "price": 1799, "stock": 30},
    {"id": 5, "name": "Kameez Shalwar",       "category": "Eastern", "price": 2199, "stock": 12},
]
next_product_id = 6   # auto-increment counter

cart   = []   # list of {id, product_id, name, price, quantity}
next_cart_id = 1

@app.route('/')
def home():
    return {"message": "Aura Flask API is running"}, 200
# ---------------------------------------------------------------------------
# 1. Health Check  ← required by the project spec
# ---------------------------------------------------------------------------
@app.route('/health', methods=['GET'])
def health():
    """Returns a simple JSON confirming the app is running."""
    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
# 2. GET /api/products  — list all products
# ---------------------------------------------------------------------------
@app.route('/api/products', methods=['GET'])
def get_products():
    """Return the full product catalogue."""
    return jsonify({"products": products, "count": len(products)}), 200


# ---------------------------------------------------------------------------
# 3. POST /api/products  — add a new product  (accepts JSON input)
# ---------------------------------------------------------------------------
@app.route('/api/products', methods=['POST'])
def add_product():
    """
    Add a new product to the catalogue.
    Required JSON fields: name, category, price, stock
    """
    global next_product_id
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    required = ["name", "category", "price", "stock"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    if not isinstance(data["price"], (int, float)) or data["price"] <= 0:
        return jsonify({"error": "price must be a positive number"}), 400

    new_product = {
        "id":       next_product_id,
        "name":     data["name"],
        "category": data["category"],
        "price":    data["price"],
        "stock":    int(data["stock"]),
    }
    products.append(new_product)
    next_product_id += 1

    return jsonify({"message": "Product added successfully", "product": new_product}), 201


# ---------------------------------------------------------------------------
# 4. GET /api/products/<id>  — get a single product by ID
# ---------------------------------------------------------------------------
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Return a single product by its ID."""
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": f"Product with id {product_id} not found"}), 404
    return jsonify(product), 200


# ---------------------------------------------------------------------------
# 5. POST /api/cart  — add an item to the cart  (POST with JSON)
# ---------------------------------------------------------------------------
@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    """
    Add a product to the cart.
    Required JSON fields: product_id, quantity
    """
    global next_cart_id
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "product_id" not in data or "quantity" not in data:
        return jsonify({"error": "product_id and quantity are required"}), 400

    product = next((p for p in products if p["id"] == data["product_id"]), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    quantity = int(data["quantity"])
    if quantity < 1:
        return jsonify({"error": "quantity must be at least 1"}), 400

    # If product is already in cart, increase quantity
    existing = next((c for c in cart if c["product_id"] == data["product_id"]), None)
    if existing:
        existing["quantity"] += quantity
        return jsonify({"message": "Cart updated", "cart_item": existing}), 200

    cart_item = {
        "id":         next_cart_id,
        "product_id": product["id"],
        "name":       product["name"],
        "price":      product["price"],
        "quantity":   quantity,
    }
    cart.append(cart_item)
    next_cart_id += 1

    return jsonify({"message": "Item added to cart", "cart_item": cart_item}), 201


# ---------------------------------------------------------------------------
# 6. GET /api/cart  — view the cart
# ---------------------------------------------------------------------------
@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Return all items currently in the cart with a total."""
    total = sum(item["price"] * item["quantity"] for item in cart)
    return jsonify({"cart": cart, "item_count": len(cart), "total": total}), 200


# ---------------------------------------------------------------------------
# 7. DELETE /api/cart/<id>  — remove an item from the cart
# ---------------------------------------------------------------------------
@app.route('/api/cart/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    """Remove a specific cart item by its cart ID."""
    item = next((c for c in cart if c["id"] == cart_id), None)
    if not item:
        return jsonify({"error": f"Cart item with id {cart_id} not found"}), 404
    cart.remove(item)
    return jsonify({"message": "Item removed from cart"}), 200


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
