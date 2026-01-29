# Gardening Helper Service

MVP online gardening lifecycle management service for amateur gardeners.

## Overview

This service helps home gardeners track and manage their gardening lifecycle from seed to harvest:

**Seed → Germination → Planting → Growing → Care Tasks → Harvest**

### Key Features

- **User Authentication**: Simple email/password authentication with JWT tokens
- **Climate Zone Detection**: Automatic USDA zone determination from location
- **Seed Management**: Track seed batches with viability warnings
- **Germination Tracking**: Monitor seed germination with success rate tracking
- **Planting Tracking**: Record planting events with health status monitoring
  - Plant health status (healthy, stressed, diseased)
  - Plant notes for observations
- **Rule-Based Task Generation**: Automatic care task creation based on plant lifecycle
  - Watering schedules based on plant requirements
  - Harvest reminders based on planting date + days to harvest
  - Seed viability warnings
  - Intelligent priority assignment based on plant health and task type
- **Task Management**: Advanced task system with priorities and recurring tasks
  - Task priorities: High, Medium, Low
  - Recurring tasks: Daily, Weekly, Biweekly, Monthly
  - Automatic next occurrence generation for recurring tasks
- **Dashboard & Filters**: Visual task management with statistics and filtering
  - Filter tasks by priority
  - View task statistics by priority and status
  - Track recurring task counts

## Architecture

Clean, maintainable architecture:

```
gardening-service/
├── app/
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic validation schemas
│   ├── repositories/    # Database CRUD operations
│   ├── services/        # Business logic (auth, climate zones)
│   ├── rules/           # Rule-based task generation engine
│   ├── api/             # REST API endpoints
│   ├── config.py        # Configuration management
│   ├── database.py      # Database setup
│   └── main.py          # FastAPI application
├── migrations/          # Alembic database migrations
├── seed_data/           # Initial plant variety data
├── requirements.txt     # Python dependencies
└── alembic.ini         # Migration configuration
```

### Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT tokens with bcrypt password hashing
- **Validation**: Pydantic v2

## Setup Instructions

### Prerequisites

- Python 3.12
- PostgreSQL 13 or higher
- pip and venv

### 1. Clone and Navigate

```bash
cd gardening-service
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

Create a PostgreSQL database:

```bash
# Using psql
psql -U postgres
CREATE DATABASE gardening_db;
CREATE USER gardener WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE gardening_db TO gardener;
\q
```

### 5. Configure Environment

Copy the example environment file and customize:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://gardener:password@localhost:5432/gardening_db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
APP_NAME=Gardening Helper Service
DEBUG=True
```

**Important**: Generate a secure secret key for production:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. Load Seed Data

Populate the database with common plant varieties:

```bash
python -m seed_data.plant_varieties
```

### 8. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Usage

### Authentication Flow

1. **Create User**

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "gardener@example.com",
    "password": "securepassword123",
    "zip_code": "94102"
  }'
```

2. **Login**

```bash
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "gardener@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

3. **Use Token for Authenticated Requests**

```bash
export TOKEN="your-access-token-here"

curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

### Core Workflows

#### 1. Create a Garden

```bash
curl -X POST "http://localhost:8000/gardens" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Backyard Garden",
    "description": "Main vegetable garden"
  }'
```

#### 2. Browse Plant Varieties

```bash
curl -X GET "http://localhost:8000/plant-varieties?search=tomato" \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. Create Seed Batch

```bash
curl -X POST "http://localhost:8000/seed-batches" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plant_variety_id": 1,
    "source": "Local nursery",
    "harvest_year": 2024,
    "quantity": 50,
    "notes": "Organic heirloom seeds"
  }'
```

**Note**: If seeds are >3 years old, a viability warning task is auto-generated.

#### 4. Create Planting Event

```bash
curl -X POST "http://localhost:8000/planting-events" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "garden_id": 1,
    "plant_variety_id": 1,
    "planting_date": "2024-05-15",
    "planting_method": "transplant",
    "plant_count": 6,
    "location_in_garden": "Bed 1, Row 2",
    "health_status": "healthy",
    "plant_notes": "Strong seedlings, good color"
  }'
```

**Auto-Generated Tasks**:
- Watering schedule (based on plant's water requirements)
  - Priority: HIGH if plant is stressed/diseased, MEDIUM otherwise
- Expected harvest date task (planting_date + days_to_harvest)
  - Priority: HIGH (time-sensitive)

#### 5. View Tasks

```bash
# All tasks
curl -X GET "http://localhost:8000/tasks" \
  -H "Authorization: Bearer $TOKEN"

# Pending tasks only
curl -X GET "http://localhost:8000/tasks?status=pending" \
  -H "Authorization: Bearer $TOKEN"

# Tasks in date range
curl -X GET "http://localhost:8000/tasks?start_date=2024-05-01&end_date=2024-05-31" \
  -H "Authorization: Bearer $TOKEN"
```

#### 6. Complete a Task

```bash
curl -X POST "http://localhost:8000/tasks/1/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "completed_date": "2024-05-16",
    "notes": "Watered thoroughly in morning"
  }'
```

#### 7. Create Manual Task

```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "fertilize",
    "title": "Fertilize tomatoes",
    "description": "Apply organic fertilizer",
    "due_date": "2024-06-01",
    "priority": "medium",
    "is_recurring": true,
    "recurrence_frequency": "biweekly"
  }'
```

**Note**: When a recurring task is completed, the next occurrence is automatically created based on the recurrence frequency.

## Rule Engine

The service includes a deterministic rule-based task generation engine (not AI-based).

### Implemented Rules

#### 1. Harvest Rule
- **Trigger**: New planting event
- **Logic**: `harvest_date = planting_date + days_to_harvest`
- **Task**: Auto-generates harvest reminder
- **Priority**: HIGH (time-sensitive harvest window)

#### 2. Watering Rule
- **Trigger**: New planting event
- **Logic**: Based on plant's water requirement
  - HIGH: Every 2 days
  - MEDIUM: Every 4 days
  - LOW: Every 7 days
- **Task**: Generates 4 watering tasks ahead
- **Priority**:
  - HIGH if plant is stressed or diseased
  - MEDIUM for healthy plants

#### 3. Seed Viability Rule
- **Trigger**: New seed batch created
- **Logic**: Warns if seeds are ≥3 years old
- **Task**: Creates viability check reminder
- **Priority**: LOW (informational, not time-critical)

### Extending Rules

Rules are isolated in [app/rules/rules.py](app/rules/rules.py). To add a new rule:

1. Create a class extending `BaseRule`
2. Implement `generate_tasks()` method
3. Register in `TaskGenerator` ([app/rules/task_generator.py](app/rules/task_generator.py))

Example:

```python
class FertilizeRule(BaseRule):
    @property
    def name(self) -> str:
        return "Fertilizer Schedule Generator"

    def generate_tasks(self, db: Session, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        planting_event = context.get("planting_event")
        # ... implement logic
        return [task_dict]
```

## Database Schema

### Core Entities

- **User**: User accounts with location and USDA zone
- **Garden**: User's growing areas
- **PlantVariety**: Reference table of plant types (static seed data)
- **SeedBatch**: Seeds from a specific source and year
- **GerminationEvent**: When seeds are started
  - `germination_success_rate`: Percentage (0-100) of successful germination
- **PlantingEvent**: When/where plants are planted (lifecycle anchor)
  - `health_status`: Plant health (healthy, stressed, diseased)
  - `plant_notes`: Observations about the plants
- **CareTask**: Unified task model (auto-generated or manual)
  - `priority`: Task priority (low, medium, high)
  - `is_recurring`: Boolean flag for recurring tasks
  - `recurrence_frequency`: Frequency for recurring tasks (daily, weekly, biweekly, monthly)
  - `parent_task_id`: Reference to parent task for recurring occurrences

### Relationships

```
User
├── Gardens
├── SeedBatches
├── GerminationEvents
├── PlantingEvents
└── CareTasks

Garden
└── PlantingEvents

PlantVariety (static)
├── SeedBatches
├── GerminationEvents
└── PlantingEvents

SeedBatch
└── GerminationEvents

GerminationEvent
└── PlantingEvents

PlantingEvent
└── CareTasks
```

## Development with Docker

### Quick Start with Docker Compose

The fastest way to run the entire stack locally (API + Database + UI):

```bash
# Build and start all services
docker-compose up

# In another terminal, verify services are running
curl http://localhost:8080/health  # API
curl http://localhost:3000          # UI
```

**Services available:**
- **UI**: http://localhost:3000 (Web interface)
- **API**: http://localhost:8080 (REST API)
- **API Docs**: http://localhost:8080/docs (Swagger UI)
- **Database**: localhost:5432 (PostgreSQL)

To rebuild after code changes:
```bash
docker-compose up --build
```

To stop:
```bash
docker-compose down
```

### UI Development

The frontend is a React + TypeScript application built with Vite.

**Environment Variables:**
- `VITE_API_URL` - API base URL (default: http://localhost:8080)

**Local development without Docker:**
```bash
cd frontend
npm install
npm run dev
```

**Build for production:**
```bash
cd frontend
npm run build
```

**Run tests:**
```bash
cd frontend
npm test
```

### Running Tests

Unit tests for rule engine and task generation:

```bash
# Install test dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_rules.py

# Run specific test
pytest tests/test_rules.py::TestHarvestRule::test_harvest_rule_generates_task
```

Tests use an in-memory SQLite database and do not require external services.

### Creating a New Migration

After modifying models:

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Production Deployment to Fly.io

### Prerequisites

1. Install the Fly.io CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Create a Fly.io account and login:
   ```bash
   fly auth login
   ```

### Deployment Steps

#### 1. Create and Configure App

```bash
# Launch app (interactive - will create fly.toml)
fly launch --no-deploy

# When prompted:
# - Choose app name (or let Fly generate one)
# - Choose region (select closest to your users)
# - Do NOT deploy yet (we need to configure database first)
```

#### 2. Create PostgreSQL Database

```bash
# Create managed Postgres database
# Choose: Development - Single node, 1x shared CPU, 256MB RAM, 1GB disk
fly postgres create --name gardening-db

# Attach database to app
fly postgres attach gardening-db
```

This automatically sets the `DATABASE_URL` environment variable.

#### 3. Set Secret Environment Variables

```bash
# Generate a secure secret key
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Set secrets (NOT visible in fly.toml)
fly secrets set SECRET_KEY="$SECRET_KEY"
```

#### 4. Deploy Application

```bash
# Deploy to Fly.io
fly deploy

# Monitor deployment
fly logs
```

#### 5. Verify Deployment

```bash
# Check app status
fly status

# View logs
fly logs

# Open app in browser
fly open

# Check health endpoint
curl https://your-app-name.fly.dev/health
```

#### 6. Load Seed Data (First Deploy Only)

```bash
# SSH into the running app
fly ssh console

# Inside the container, run:
python -m seed_data.plant_varieties

# Exit
exit
```

#### 7. Deploy Frontend UI (Optional)

The frontend can be deployed as a separate Fly.io app:

```bash
# Navigate to frontend directory
cd frontend

# Launch frontend app
fly launch --no-deploy

# Update VITE_API_URL in frontend/fly.toml to point to your backend:
# VITE_API_URL = "https://your-backend-app.fly.dev"

# Deploy frontend
fly deploy

# Verify
fly open
```

**Note:** The UI is statically built, so `VITE_API_URL` must be set to your backend URL before deployment.

### Managing the Deployed App

```bash
# View current configuration
fly config show

# Scale resources (if needed)
fly scale vm shared-cpu-1x --memory 512

# Restart app
fly apps restart

# View database info
fly postgres db list --app gardening-db

# Connect to database
fly postgres connect --app gardening-db

# View secrets (values are hidden)
fly secrets list

# Update a secret
fly secrets set SECRET_KEY="new-value"

# View deployments
fly releases

# Rollback to previous version
fly releases rollback
```

### Environment Variables

The following environment variables are configured:

**Set in fly.toml** (non-secret):
- `APP_NAME`: Application name
- `APP_ENV`: production
- `DEBUG`: False
- `ALGORITHM`: HS256
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 10080 (7 days)
- `PORT`: 8080

**Set via `fly secrets`** (secret):
- `SECRET_KEY`: JWT signing key (required)
- `DATABASE_URL`: Auto-set by Fly Postgres attachment

### Cost Optimization

Current configuration targets the **free/lowest tier**:

- **App**: shared-cpu-1x, 256MB RAM
  - Scales to zero when idle (no traffic)
  - ~$0-2/month depending on usage

- **Database**: Development single node
  - 1x shared CPU, 256MB RAM, 1GB disk
  - ~$0-2/month

**Estimated total: $0-5/month**

To monitor costs:
```bash
fly platform status
```

### Troubleshooting

**Migrations failed:**
```bash
# Check logs
fly logs

# SSH into container and run manually
fly ssh console
alembic upgrade head
```

**App won't start:**
```bash
# Check logs for errors
fly logs

# Verify secrets are set
fly secrets list

# Ensure DATABASE_URL is set
fly config show
```

**Database connection issues:**
```bash
# Verify database is attached
fly postgres db list --app gardening-db

# Test connection
fly ssh console -C "python -c \"import psycopg2; psycopg2.connect('$DATABASE_URL')\""
```

**Out of memory:**
```bash
# Increase memory allocation
fly scale vm shared-cpu-1x --memory 512
```

## Local Development (Alternative: Native Setup)

If you prefer not to use Docker, follow the original setup instructions at the top of this README (Prerequisites → Start the Server).

## API Endpoints Reference

### Users
- `POST /users` - Create user
- `POST /users/login` - Login
- `GET /users/me` - Get current user info

### Gardens
- `POST /gardens` - Create garden
- `GET /gardens` - List user's gardens
- `GET /gardens/{id}` - Get garden
- `PATCH /gardens/{id}` - Update garden
- `DELETE /gardens/{id}` - Delete garden

### Plant Varieties
- `GET /plant-varieties` - List varieties (searchable)
- `GET /plant-varieties/{id}` - Get variety

### Seed Batches
- `POST /seed-batches` - Create seed batch (+ auto-generates viability tasks)
- `GET /seed-batches` - List user's batches
- `GET /seed-batches/{id}` - Get batch
- `PATCH /seed-batches/{id}` - Update batch
- `DELETE /seed-batches/{id}` - Delete batch

### Germination Events
- `POST /germination-events` - Create event
- `GET /germination-events` - List user's events
- `GET /germination-events/{id}` - Get event
- `PATCH /germination-events/{id}` - Update event (including `germination_success_rate`)

### Planting Events
- `POST /planting-events` - Create event (+ auto-generates care tasks with priorities)
  - Accepts `health_status` and `plant_notes` fields
- `GET /planting-events` - List user's events
- `GET /planting-events/{id}` - Get event
- `PATCH /planting-events/{id}` - Update event (including health status and notes)

### Care Tasks
- `POST /tasks` - Create manual task
  - Accepts `priority`, `is_recurring`, and `recurrence_frequency` fields
- `GET /tasks` - List tasks (filterable by status, date range)
- `GET /tasks/{id}` - Get task
- `PATCH /tasks/{id}` - Update task (including priority)
- `POST /tasks/{id}/complete` - Mark task complete (auto-generates next occurrence for recurring tasks)
- `DELETE /tasks/{id}` - Delete task

## License

MIT

## Support

For issues or questions, please open an issue on the project repository.
