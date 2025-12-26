# SCA Backend API


## Prerequisites

- **Docker & Docker Compose** (recommended for easy setup)
  OR
- **Python 3.9+**
- **PostgreSQL 12+** (if running locally)

## Quick Start with Docker (Recommended)

### 1. Clone and Navigate
### 2. Create Environment File

Create a `.env` file in directory:

```bash
# Frontend URL
FRONTEND_URL=http://localhost:3000

# Database Configuration
POSTGRES_USER=sca_user
POSTGRES_PASSWORD=sca_password
POSTGRES_DB=sca_db

# Application Database URL
# For Docker Compose, use 'postgres' as hostname
DATABASE_URL=postgresql://sca_user:sca_password@postgres:5432/sca_db
```

### 3. Start Services

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL container
- Build and start the FastAPI backend
- Create database tables automatically

### 4. Verify Installation

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend

# Test the API
http://localhost:8000/health
```

### 5. Access the API

- **API Base URL**: `http://localhost:8000`
- **Interactive API Docs**: `http://localhost:8000/docs`

### Stop Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

## Local Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file:

```bash
# Frontend URL
FRONTEND_URL=http://localhost:3000

# Database Configuration
POSTGRES_USER=sca_user
POSTGRES_PASSWORD=sca_password
POSTGRES_DB=sca_db

# Application Database URL
# For local development, use 'localhost'
DATABASE_URL=postgresql://sca_user:sca_password@localhost:5432/sca_db
```

### 4. Start PostgreSQL

Using Docker Compose (only PostgreSQL):

```bash
docker-compose up -d postgres
```

Or use your own PostgreSQL instance and update the `DATABASE_URL` accordingly.

### 5. Run the Application

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `POSTGRES_USER` | PostgreSQL username | Yes | - |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes | - |
| `POSTGRES_DB` | PostgreSQL database name | Yes | `sca_db` |
| `DATABASE_URL` | Full database connection string | Yes | - |

**Note**: For Docker Compose, use `postgres` as the hostname in `DATABASE_URL`. For local development, use `localhost`.

## API Documentation

### Interactive Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`

### Postman Collection

Import the provided Postman collection for easy API testing:

- **File**: `SCA_Backend_API.postman_collection.json`
- **Remote**: `https://vadim-plataniy-3097402.postman.co/workspace/Vadym-Platanyi's-Team's-Workspa~4e97278c-0554-481c-8432-f44981e6a5f4/collection/51069928-6338c719-9e32-4353-bfe1-ef0a5c5e44b6?action=share&creator=51069928&active-environment=51069928-3bd01322-c997-4919-99cd-afa210839e71`
- **Base URL Variable**: Set `base_url`

## API Endpoints

### General

- `GET /` - Welcome message
- `GET /health` - Health check endpoint

### Cats

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/cats/` | Create a new cat (breed validated against Cat API) |
| `GET` | `/cats/` | List all cats (pagination: `?skip=0&limit=100`) |
| `GET` | `/cats/{cat_id}` | Get a single cat by ID |
| `PUT` | `/cats/{cat_id}` | Update cat's salary (only salary can be updated) |
| `DELETE` | `/cats/{cat_id}` | Remove a cat |

### Missions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/missions/` | Create a new mission with targets (1-3 targets) |
| `GET` | `/missions/` | List all missions (pagination: `?skip=0&limit=100`) |
| `GET` | `/missions/{mission_id}` | Get a single mission by ID |
| `POST` | `/missions/{mission_id}/assign-cat` | Assign a cat to a mission |
| `PUT` | `/missions/{mission_id}/targets` | Update mission targets |
| `PUT` | `/missions/{mission_id}/complete` | Mark mission as completed |
| `PUT` | `/missions/{mission_id}/targets/{target_id}/notes` | Update target notes |
| `DELETE` | `/missions/{mission_id}` | Delete a mission (only if not assigned to cat) |


## Project Structure

```
sca_back/
├── main.py                          # FastAPI application and endpoints
├── models.py                        # SQLAlchemy database models
├── schemas.py                       # Pydantic schemas for validation
├── database.py                      # Database configuration and session
├── config.py                        # Application settings
├── breed_validator.py              # Cat breed validation against Cat API
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker image definition
├── docker-compose.yml               # Docker Compose configuration
├── .env                             # Environment variables (create this)
├── .dockerignore                    # Files to exclude from Docker build
├── SCA_Backend_API.postman_collection.json  # Postman collection
└── README.md                        # This file
```

## Database Schema

### Tables

- **cats**: Stores cat information
  - `id`, `name`, `experience`, `breed`, `salary`

- **missions**: Stores mission information
  - `id`, `cat_id` (nullable), `complete_state`

- **targets**: Stores target information (linked to missions)
  - `id`, `mission_id`, `name`, `country`, `notes`, `complete_state`


