# DevOps Project - Flask Backend with Docker & CI/CD

## API Endpoints
- GET `/health` - Health check
- GET `/api/products` - Get all products
- GET `/api/products/{id}` - Get single product
- POST `/api/products` - Create product
- PUT `/api/products/{id}` - Update product
- DELETE `/api/products/{id}` - Delete product

## Run with Docker
Build and run the container:
`docker build -t your-app:v1 .`
`docker run -d -p 5000:5000 --name flask-app your-app:v1`
Test: `curl http://localhost:5000/health`

## CI/CD Pipeline
GitHub Actions runs 8 tests and builds Docker image on every push to main.

## Test Results
All 8 test cases pass:
- Health check endpoint
- GET products
- GET single product
- POST create product
- PUT update product
- DELETE delete product
- Error handling

## Technologies
Python 3.11, Flask, Docker, GitHub Actions, pytest

## Team Members
- Person 1: Flask Backend
- Person 2: Frontend + Git
- Person 3: Docker + CI/CD
- Person 4: AWS Deployment
