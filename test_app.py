"""
test_app.py  —  Automated tests for Aura Flask API
Run with:  python -m pytest test_app.py -v
All tests must pass before submission.
"""
import pytest
from app import app


# ---------------------------------------------------------------------------
# Fixture: gives every test a fresh test client AND resets shared state
# ---------------------------------------------------------------------------
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Reset in-memory data so tests don't interfere with each other
        import app as app_module
        app_module.products = [
            {"id": 1, "name": "Slim Fit Jeans", "category": "Bottoms", "price": 2499, "stock": 20},
            {"id": 2, "name": "Polo Shirt",      "category": "Tops",    "price": 1299, "stock": 15},
            {"id": 3, "name": "Denim Jacket",    "category": "Jackets", "price": 3999, "stock": 8},
        ]
        app_module.next_product_id = 4
        app_module.cart = []
        app_module.next_cart_id = 1
        yield client


# ---------------------------------------------------------------------------
# Test 1 — Health check returns 200 with status "ok"
# ---------------------------------------------------------------------------
def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'


# ---------------------------------------------------------------------------
# Test 2 — GET /api/products returns the product list
# ---------------------------------------------------------------------------
def test_get_products(client):
    response = client.get('/api/products')
    assert response.status_code == 200
    data = response.get_json()
    assert 'products' in data
    assert isinstance(data['products'], list)
    assert data['count'] == 3


# ---------------------------------------------------------------------------
# Test 3 — POST /api/products with valid data returns 201 and the new product
# ---------------------------------------------------------------------------
def test_add_product_success(client):
    new_product = {
        "name": "Cargo Shorts",
        "category": "Bottoms",
        "price": 1799,
        "stock": 25
    }
    response = client.post('/api/products',
                           json=new_product,
                           content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert data['product']['name'] == 'Cargo Shorts'
    assert data['product']['price'] == 1799
    assert 'id' in data['product']


# ---------------------------------------------------------------------------
# Test 4 — POST /api/products with missing fields returns 400
# ---------------------------------------------------------------------------
def test_add_product_missing_fields(client):
    incomplete = {"name": "T-Shirt"}   # missing category, price, stock
    response = client.post('/api/products',
                           json=incomplete,
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


# ---------------------------------------------------------------------------
# Test 5 — GET /api/products/<id> returns 404 for a non-existent product
# ---------------------------------------------------------------------------
def test_get_product_not_found(client):
    response = client.get('/api/products/9999')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data


# ---------------------------------------------------------------------------
# Test 6 — POST /api/cart with valid data returns 201
# ---------------------------------------------------------------------------
def test_add_to_cart_success(client):
    response = client.post('/api/cart',
                           json={"product_id": 1, "quantity": 2},
                           content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert data['cart_item']['product_id'] == 1
    assert data['cart_item']['quantity'] == 2


# ---------------------------------------------------------------------------
# Test 7 — POST /api/cart with missing fields returns 400
# ---------------------------------------------------------------------------
def test_add_to_cart_missing_fields(client):
    response = client.post('/api/cart',
                           json={"product_id": 1},   # quantity missing
                           content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
