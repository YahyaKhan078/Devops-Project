# Deployment Document
## DevOps Project - Flask Backend API

---

## 1. Architecture Overview

```
User/Client
     |
     | HTTP Request
     v
AWS EC2 Instance (t3.micro, Ubuntu 22.04 LTS)
     |
     | Port 5000
     v
Docker Container (your-app:v1)
     |
     v
Flask Backend API (app.py)
     |
     v
REST API Endpoints (/health, /api/products)
```

- The Flask app runs inside a Docker container on an AWS EC2 instance
- GitHub Actions handles CI/CD — automatically runs tests and builds Docker image on every push to main
- The app is accessible publicly via the EC2 Public IP on port 5000

---

## 2. Application Description

- **Framework:** Flask (Python)
- **Purpose:** REST API for a product store (ecommerce backend)
- **CORS:** Enabled using flask-cors
- **Port:** 5000

### API Endpoints:

| Endpoint | Method | Description | Status Code |
|---|---|---|---|
| /health | GET | Health check | 200 |
| /api/products | GET | Get all products | 200 |
| /api/products/<id> | GET | Get single product | 200 / 404 |
| /api/products | POST | Create new product | 201 / 400 |
| /api/products/<id> | PUT | Update product | 200 / 404 |
| /api/products/<id> | DELETE | Delete product | 200 / 404 |

---

## 3. Deployment Steps

### Step 1 — Launch EC2 Instance
- Went to AWS Console → EC2 → Launch Instance
- Selected Ubuntu 22.04 LTS, t3.micro (Free Tier)
- Created key pair: my-key.pem
- Configured Security Group:
  - Port 22 (SSH) — for remote access
  - Port 5000 (Custom TCP) — for Flask app

### Step 2 — SSH Into EC2
```bash
chmod 400 my-key.pem
ssh -i ~/Downloads/my-key.pem ubuntu@13.235.8.12
```

### Step 3 — Install Docker on EC2
```bash
sudo apt update
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
exit
# SSH back in
ssh -i ~/Downloads/my-key.pem ubuntu@13.235.8.12
```

### Step 4 — Clone Repository
```bash
git clone https://github.com/YahyaKhan078/Devops-Project
cd Devops-Project
```

### Step 5 — Build Docker Image
```bash
docker build -t your-app:v1 .
```

### Step 6 — Run Container
```bash
docker run -d -p 5000:5000 --restart=always your-app:v1
```

### Step 7 — Verify Deployment
```bash
docker ps
curl http://localhost:5000/health
```

---

## 4. Docker Setup

### Dockerfile uses python:3.11-slim base image:
- Copies requirements.txt first and installs dependencies (for layer caching)
- Then copies the rest of the app code
- Exposes port 5000
- CMD runs python app.py on container start

### Key Docker Commands Used:
```bash
# Build image
docker build -t your-app:v1 .

# Run container with auto-restart
docker run -d -p 5000:5000 --restart=always your-app:v1

# Check running containers
docker ps
```

### What --restart=always means:
If the container crashes or the EC2 instance reboots, Docker will automatically
restart the container so the app stays online without any manual action needed.

---

## 5. CI/CD Pipeline

- **Workflow file:** .github/workflows/ci.yml
- **Trigger:** Runs automatically on every push to main branch

### Job 1 — Test:
- Installs Python dependencies from requirements.txt
- Runs pytest on test_app.py
- Must pass before Job 2 runs

### Job 2 — Docker:
- Builds the Docker image
- Runs a container and checks the /health endpoint
- Confirms app is responding correctly

Both jobs must show green checkmarks in the GitHub Actions tab before the
deployment is considered successful.

---

## 6. AWS Configuration

| Setting | Value |
|---|---|
| Instance Type | t3.micro |
| OS | Ubuntu 22.04 LTS |
| Region | ap-south-1 (Mumbai) |
| Public IP | 13.235.8.12 |
| Storage | 8 GB (default) |

### Security Group Rules:

| Type | Protocol | Port | Source | Purpose |
|---|---|---|---|---|
| SSH | TCP | 22 | My IP | Remote access via terminal |
| Custom TCP | TCP | 5000 | 0.0.0.0/0 | Flask app public access |

### Billing Alert:
- Set up a $1 budget alert in AWS Billing
- Email notification triggered if charges exceed $1

---

## 7. Challenges Faced

1. **t2.micro not available** — AWS newer accounts use t3.micro as free tier.
   Fixed by selecting t3.micro instead (same specs, also free tier).

2. **Docker commands ran on local machine instead of EC2** — Accidentally ran
   install commands on Kali Linux before SSHing into EC2.
   Fixed by SSHing into EC2 first, then running install commands.

3. **SSH connection cancelled by mistake** — Pressed Ctrl+C when asked to
   confirm SSH fingerprint. Fixed by running SSH command again and typing yes.

4. **Docker not found after install** — Had to exit and SSH back in after
   running usermod command for group changes to apply.

---

## 8. Lessons Learned

1. **Security groups act as cloud firewalls** — Only the ports you explicitly
   open are accessible. Port 5000 had to be manually opened for the app to work.

2. **--restart=always is critical for production** — Without it, if the server
   reboots the app goes offline and needs manual restart.

3. **Layer order in Dockerfile matters** — Copying requirements.txt before
   app code means Docker uses cached layers and builds faster on subsequent builds.

4. **usermod group changes need re-login** — After adding ubuntu to the docker
   group, you must logout and SSH back in for it to take effect.

5. **EC2 Public IP changes on restart** — The public IP is not static by default.
   For permanent IPs, an Elastic IP must be assigned.

---

## 9. Testing Evidence

### Pytest Output:
```
(Run: docker exec <container-id> pytest test_app.py -v)
All tests passing
```

### Docker ps Output:
```
CONTAINER ID   IMAGE         COMMAND           CREATED        STATUS        PORTS
be329f56d865   your-app:v1   "python app.py"   X minutes ago  Up X minutes  0.0.0.0:5000->5000/tcp
```

### Curl from EC2:
```bash
$ curl http://localhost:5000/health
{
  "service": "Flask Backend API",
  "status": "healthy",
  "version": "1.0.0"
}
```

### App Live in Browser:
- URL: http://13.235.8.12:5000/health
- Response: {"service": "Flask Backend API", "status": "healthy", "version": "1.0.0"}
- Status: 200 OK

### All API Endpoints Tested:
```bash
# Get all products
curl http://localhost:5000/api/products
# Returns: list of 3 products with 200 OK

# Get single product
curl http://localhost:5000/api/products/1
# Returns: T-Shirt product details with 200 OK

# Create product
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Jacket", "price": 99.99, "category": "Clothing"}'
# Returns: 201 Created

# Update product
curl -X PUT http://localhost:5000/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated T-Shirt", "price": 25.99}'
# Returns: 200 OK

# Delete product
curl -X DELETE http://localhost:5000/api/TZXXXXproducts/1
# Returns: 200 OK
```

---

*Document prepared by: Person 4 — AWS Deployment + Documentation*
*EC2 Instance IP: 13.235.8.12*
*App URL: http://13.235.8.12:5000/health*
