import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_get_products(client):
    response = client.get('/api/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['products']) == 3

def test_get_single_product_success(client):
    response = client.get('/api/products/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == 1

def test_get_product_not_found(client):
    response = client.get('/api/products/999')
    assert response.status_code == 404

def test_create_product_valid_json(client):
    response = client.post('/api/products',
                          json={'name': 'Jacket', 'price': 89.99},
                          content_type='application/json')
    assert response.status_code == 201

def test_create_product_invalid_json(client):
    response = client.post('/api/products',
                          data='not json',
                          content_type='text/plain')
    assert response.status_code == 400

def test_update_product(client):
    response = client.put('/api/products/1',
                         json={'name': 'Updated', 'price': 29.99})
    assert response.status_code == 200

def test_delete_product(client):
    response = client.delete('/api/products/1')
    assert response.status_code == 200
