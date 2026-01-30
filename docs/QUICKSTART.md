# Quick Start Guide

Get the Gardening Helper Service running in 5 minutes.

## Option 1: Using Docker (Easiest)

### 1. Start PostgreSQL

```bash
docker-compose up -d
```

### 2. Set up Python environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# No need to edit - defaults work with Docker Compose
```

### 4. Run migrations and seed data

```bash
alembic upgrade head
python -m seed_data.plant_varieties
```

### 5. Start the server

```bash
./run_dev.sh
# Or: uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## Option 2: Using Local PostgreSQL

### 1. Install PostgreSQL

Install PostgreSQL 13+ from https://www.postgresql.org/download/

### 2. Create database

```bash
psql -U postgres
CREATE DATABASE gardening_db;
CREATE USER gardener WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE gardening_db TO gardener;
\q
```

### 3. Follow steps 2-5 from Option 1 above

## First API Call

### 1. Create a user

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "zip_code": "94102"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

### 3. Create a garden

```bash
curl -X POST "http://localhost:8000/gardens" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Garden",
    "description": "Test garden"
  }'
```

### 4. Browse plant varieties

```bash
curl -X GET "http://localhost:8000/plant-varieties?search=tomato" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Create a planting

```bash
curl -X POST "http://localhost:8000/planting-events" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "garden_id": 1,
    "plant_variety_id": 1,
    "planting_date": "2024-05-15",
    "planting_method": "transplant",
    "plant_count": 4
  }'
```

### 6. View auto-generated tasks

```bash
curl -X GET "http://localhost:8000/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

You should see watering and harvest tasks auto-generated!

## Explore with Swagger UI

Open http://localhost:8000/docs in your browser for a full interactive API explorer.

## Troubleshooting

**Database connection error**: Check that PostgreSQL is running and credentials in `.env` are correct.

**Import errors**: Make sure virtual environment is activated: `source venv/bin/activate`

**Alembic errors**: Try `alembic downgrade base` then `alembic upgrade head`

## Next Steps

Read the full [README.md](README.md) for:
- Complete API reference
- Architecture details
- Production deployment guidance
- Rule engine customization
