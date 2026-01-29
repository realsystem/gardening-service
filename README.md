# Gardening Helper Service

MVP online gardening lifecycle management service for amateur gardeners.

## Overview

This service helps home gardeners track and manage their gardening lifecycle from seed to harvest:

**Seed → Germination → Planting → Growing → Care Tasks → Harvest**

### Key Features

- **User Authentication & Profiles**: Complete user management system
  - Email/password authentication with JWT tokens
  - **Password Management**: Multiple secure options for password updates
    - **Change Password**: Direct password change from Profile > Security (requires current password)
    - **Reset Password**: Email-based password recovery for forgotten passwords
    - Cryptographically secure tokens (256-bit)
    - Time-limited links (1 hour expiration)
    - Rate limiting protection (3 requests per 15 minutes)
    - Password strength enforcement
    - Single-use tokens with automatic invalidation
    - Development mode: Console output (no email setup required)
    - Production mode: SMTP email integration
  - User profiles with display name, avatar, location
  - Gardening preferences and personalization
  - Profile editing capability with Security tab
- **Climate Zone Detection**: Automatic USDA zone determination from location
- **Dual Garden Types**: Support for both outdoor and indoor gardening
  - **Outdoor Gardens**: Traditional gardening workflows
  - **Indoor Gardens**: Advanced indoor growing with environmental monitoring
    - Light source tracking (LED, Fluorescent, HPS, MH, Natural Supplement)
    - Light schedule management (hours per day)
    - Temperature range monitoring (min/max in Fahrenheit)
    - Humidity range tracking (min/max percentage)
    - Container type and grow medium tracking
    - Location tracking within indoor spaces
  - **Hydroponics Systems**: Comprehensive support for hydroponic gardening
    - System type tracking (NFT, DWC, Ebb & Flow, Aeroponics, Drip, Wick)
    - Reservoir size and nutrient schedule management
    - pH range monitoring and automatic adjustment alerts
    - EC/PPM (Electrical Conductivity / Parts Per Million) tracking
    - Water temperature monitoring
    - Automated task generation for nutrient checks, pH adjustments, and reservoir maintenance
- **Environmental Monitoring**: Comprehensive sensor reading system
  - **Indoor Gardens**: Temperature, humidity, and light hours tracking
  - **Hydroponics Systems**: pH, EC, PPM, and water temperature monitoring
  - Automatic HIGH priority warning tasks when readings exceed safe ranges
  - Historical sensor data visualization
  - Real-time alerts for critical parameters (pH, EC, water temperature)
- **Soil Tracking & Science**: Professional soil analysis with actionable recommendations
  - Track soil samples with pH, N-P-K (Nitrogen, Phosphorus, Potassium), organic matter, and moisture
  - Plant-specific optimal soil ranges for common vegetables and herbs
  - **Science-Based Recommendations**: Specific, numeric guidance for soil amendments
    - pH adjustment: Calculate exact lime or sulfur amounts needed
    - Nutrient deficiencies: Specific fertilizer types and application rates
    - Organic matter management: Compost and amendment recommendations
    - Moisture optimization: Watering and drainage guidance
  - Link soil samples to gardens or specific plantings
  - Track soil changes over time with sample history
  - All recommendations based on agricultural research and best practices
- **Irrigation Tracking & Scheduling**: Water management with smart recommendations
  - Log irrigation events with date, volume, method, and duration
  - Track irrigation methods (drip, sprinkler, hand watering, soaker hose, flood, misting)
  - **Intelligent Watering Recommendations**: Plant-specific watering schedules
    - Automatic frequency recommendations based on plant type
    - Volume guidance (liters per square foot)
    - Overdue watering alerts with priority levels
    - Overwatering detection and warnings
    - Seasonal adjustment factors
  - Irrigation history and statistics (total volume, average per event, days since last watering)
  - Integration with soil moisture data for precise watering decisions
  - Weekly/monthly water usage summaries
- **Seed Management**: Track seed batches with viability warnings
  - Preferred germination methods per batch
  - Visual plant variety information with photos
  - Tag-based organization (easy, fruiting, perennial, etc.)
- **Germination Tracking**: Monitor seed germination with success rate tracking
- **Planting Tracking**: Record planting events with health status monitoring
  - Plant health status (healthy, stressed, diseased)
  - Plant notes for observations
- **Rule-Based Task Generation**: Automatic care task creation based on plant lifecycle
  - Context-aware rules for outdoor vs indoor gardens
  - Watering schedules based on plant requirements
  - Harvest reminders based on planting date + days to harvest
  - Seed viability warnings
  - Indoor-specific task types (lighting, temperature, humidity, nutrients, training)
  - Intelligent priority assignment based on plant health and task type
- **Task Management**: Advanced task system with priorities and recurring tasks
  - Task priorities: High, Medium, Low
  - Recurring tasks: Daily, Weekly, Biweekly, Monthly
  - Automatic next occurrence generation for recurring tasks
  - Indoor-specific task types (lighting, temperature, humidity, nutrients, training)
  - Hydroponics-specific task types:
    - Check nutrient solution (EC/PPM monitoring)
    - Adjust pH levels
    - Replace/top-up nutrient solution
    - Clean reservoir and system maintenance
    - Adjust water circulation (pumps, aeration)
- **Enhanced Dashboard**: Rich visual interface with personalization
  - Personalized greeting with user name and location
  - Profile information display
  - Garden management with type indicators
  - Sensor reading display for indoor gardens
  - Plant variety photos and tags
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

**Outdoor Garden:**
```bash
curl -X POST "http://localhost:8000/gardens" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Backyard Garden",
    "description": "Main vegetable garden",
    "garden_type": "outdoor"
  }'
```

**Indoor Garden:**
```bash
curl -X POST "http://localhost:8000/gardens" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Basement Grow Room",
    "description": "Indoor hydroponic setup",
    "garden_type": "indoor",
    "location": "Basement",
    "light_source_type": "led",
    "light_hours_per_day": 16,
    "temp_min_f": 65,
    "temp_max_f": 75,
    "humidity_min_percent": 40,
    "humidity_max_percent": 60,
    "container_type": "5-gallon grow bags",
    "grow_medium": "hydroponics"
  }'
```

**Auto-Generated Tasks for Indoor Gardens**:
- Daily light schedule reminder (MEDIUM priority, recurring)
- Weekly nutrient solution task if using hydroponics (MEDIUM priority, recurring)

**Hydroponic Garden:**
```bash
curl -X POST "http://localhost:8000/gardens" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "DWC Grow System",
    "description": "Deep Water Culture hydroponic setup",
    "garden_type": "indoor",
    "location": "Basement",
    "is_hydroponic": true,
    "hydro_system_type": "dwc",
    "reservoir_size_liters": 75,
    "nutrient_schedule": "General Hydroponics Flora series, following Lucas Formula",
    "ph_min": 5.5,
    "ph_max": 6.5,
    "ec_min": 1.2,
    "ec_max": 2.0,
    "ppm_min": 800,
    "ppm_max": 1400,
    "water_temp_min_f": 65,
    "water_temp_max_f": 72,
    "light_source_type": "led",
    "light_hours_per_day": 18,
    "temp_min_f": 70,
    "temp_max_f": 78,
    "humidity_min_percent": 50,
    "humidity_max_percent": 70
  }'
```

**Auto-Generated Tasks for Hydroponic Gardens**:
- Daily nutrient solution checks for first 2 weeks, then every 3 days (MEDIUM priority)
- Weekly complete nutrient solution replacement (MEDIUM priority, recurring)
- Biweekly reservoir cleaning and system maintenance (MEDIUM priority, recurring)

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
- For indoor gardens:
  - Daily light schedule reminders (MEDIUM priority)
  - Weekly nutrient tasks for hydroponics (MEDIUM priority)

#### 5. Add Sensor Reading (Indoor Gardens)

```bash
curl -X POST "http://localhost:8000/sensor-readings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "garden_id": 1,
    "reading_date": "2024-05-16",
    "temperature_f": 72.5,
    "humidity_percent": 55,
    "light_hours": 16
  }'
```

**Auto-Generated Warning Tasks**:
- If temperature is below `temp_min_f` or above `temp_max_f`: HIGH priority "Adjust temperature" task
- If humidity is below `humidity_min_percent` or above `humidity_max_percent`: HIGH priority "Adjust humidity" task

#### 6. Add Hydroponics Sensor Reading

```bash
curl -X POST "http://localhost:8000/sensor-readings" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "garden_id": 1,
    "reading_date": "2024-05-16",
    "temperature_f": 74,
    "humidity_percent": 60,
    "light_hours": 18,
    "ph_level": 6.2,
    "ec_ms_cm": 1.6,
    "ppm": 1100,
    "water_temp_f": 68
  }'
```

**Auto-Generated Hydroponics Warning Tasks**:
- If pH is below `ph_min` or above `ph_max`: HIGH priority "Adjust pH" task with specific instructions
- If EC is below `ec_min` or above `ec_max`: HIGH priority nutrient adjustment task
- If PPM is below `ppm_min` or above `ppm_max`: HIGH priority nutrient adjustment task
- If water temperature is below `water_temp_min_f` or above `water_temp_max_f`: HIGH priority water temperature adjustment task

#### 7. View Tasks

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

#### 8. Complete a Task

```bash
curl -X POST "http://localhost:8000/tasks/1/complete" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "completed_date": "2024-05-16",
    "notes": "Watered thoroughly in morning"
  }'
```

#### 9. Create Manual Task

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

#### Outdoor & Indoor Rules

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

#### Indoor-Specific Rules

#### 4. Light Schedule Rule
- **Trigger**: New planting event in indoor garden
- **Logic**: Creates recurring daily light schedule reminders
- **Task**: Generates "Adjust lighting schedule" task
- **Priority**: MEDIUM
- **Recurrence**: Daily

#### 5. Temperature Monitoring Rule
- **Trigger**: Sensor reading created with temperature out of safe range
- **Logic**: Compares reading temperature to garden's temp_min_f and temp_max_f
- **Task**: Creates "Adjust temperature" warning task
- **Priority**: HIGH (immediate environmental concern)

#### 6. Humidity Monitoring Rule
- **Trigger**: Sensor reading created with humidity out of safe range
- **Logic**: Compares reading humidity to garden's humidity_min_percent and humidity_max_percent
- **Task**: Creates "Adjust humidity" warning task
- **Priority**: HIGH (immediate environmental concern)

#### 7. Nutrient Schedule Rule
- **Trigger**: New planting event in indoor garden with hydroponic grow medium
- **Logic**: Detects "hydro" keyword in grow_medium field
- **Task**: Creates recurring nutrient solution task
- **Priority**: MEDIUM
- **Recurrence**: Weekly

#### Hydroponics-Specific Rules

#### 8. Nutrient Check Rule
- **Trigger**: New planting event in hydroponic garden
- **Logic**: Generates daily checks for first 14 days, then every 3 days
- **Task**: Check EC/PPM levels and nutrient concentrations
- **Priority**: MEDIUM
- **Recurrence**: Daily (after initial period)

#### 9. pH Monitoring Rule
- **Trigger**: Sensor reading with pH outside acceptable range
- **Logic**: Compares reading pH to garden's ph_min and ph_max
- **Task**: Creates pH adjustment task with specific instructions (pH UP or pH DOWN)
- **Priority**: HIGH (immediate action needed)

#### 10. EC/PPM Monitoring Rule
- **Trigger**: Sensor reading with EC or PPM outside acceptable range
- **Logic**: Compares reading to garden's ec_min/ec_max or ppm_min/ppm_max
- **Task**: Creates nutrient adjustment task (add nutrients or dilute with water)
- **Priority**: HIGH (nutrient imbalance)

#### 11. Water Temperature Monitoring Rule
- **Trigger**: Sensor reading with water temperature outside acceptable range
- **Logic**: Compares water temp to garden's water_temp_min_f and water_temp_max_f
- **Task**: Creates water temperature adjustment task (heater or chiller)
- **Priority**: HIGH (affects nutrient uptake)

#### 12. Reservoir Maintenance Rule
- **Trigger**: New planting event in hydroponic garden
- **Logic**: Schedules complete reservoir cleaning and system maintenance
- **Task**: Full reservoir clean, replace solution, check pumps/filters
- **Priority**: MEDIUM
- **Recurrence**: Biweekly (every 14 days)

#### 13. Nutrient Replacement Rule
- **Trigger**: New planting event in hydroponic garden
- **Logic**: Schedules complete nutrient solution replacement
- **Task**: Complete nutrient solution change following schedule
- **Priority**: MEDIUM
- **Recurrence**: Weekly (every 7 days)

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

- **User**: User accounts with profile and location
  - `display_name`: User's preferred display name
  - `avatar_url`: Optional profile picture URL
  - `city`: User's city/location
  - `gardening_preferences`: Gardening style and preferences
  - `usda_zone`: Climate zone
- **Garden**: User's growing areas (outdoor, indoor, or hydroponic)
  - `garden_type`: "outdoor" or "indoor"
  - `is_hydroponic`: Boolean flag for hydroponic systems
  - Indoor-specific fields:
    - `location`: Location within indoor space (e.g., "Basement", "Spare Room")
    - `light_source_type`: LED, Fluorescent, Natural Supplement, HPS, MH
    - `light_hours_per_day`: Hours of light per day (0-24)
    - `temp_min_f`, `temp_max_f`: Temperature range in Fahrenheit
    - `humidity_min_percent`, `humidity_max_percent`: Humidity range (0-100)
    - `container_type`: Type of containers used
    - `grow_medium`: Growing medium (e.g., soil, coco coir, hydroponics)
  - Hydroponics-specific fields:
    - `hydro_system_type`: System type (NFT, DWC, Ebb & Flow, Aeroponics, Drip, Wick)
    - `reservoir_size_liters`: Reservoir capacity in liters
    - `nutrient_schedule`: Nutrient solution schedule and notes
    - `ph_min`, `ph_max`: Target pH range (0-14)
    - `ec_min`, `ec_max`: Target EC range in mS/cm
    - `ppm_min`, `ppm_max`: Target PPM range
    - `water_temp_min_f`, `water_temp_max_f`: Water temperature range in Fahrenheit
- **SensorReading**: Environmental data for indoor and hydroponic gardens
  - `garden_id`: Reference to indoor/hydroponic garden
  - `reading_date`: Date of reading
  - Indoor readings:
    - `temperature_f`: Air temperature in Fahrenheit
    - `humidity_percent`: Relative humidity percentage
    - `light_hours`: Hours of light received
  - Hydroponics readings:
    - `ph_level`: pH level (0-14)
    - `ec_ms_cm`: Electrical Conductivity in mS/cm
    - `ppm`: Parts Per Million
    - `water_temp_f`: Water temperature in Fahrenheit
- **PlantVariety**: Reference table of plant types (static seed data)
  - `photo_url`: Optional plant variety image
  - `tags`: Comma-separated tags (easy, fruiting, perennial, etc.)
- **SeedBatch**: Seeds from a specific source and year
  - `preferred_germination_method`: User's preferred germination approach
- **GerminationEvent**: When seeds are started
  - `germination_success_rate`: Percentage (0-100) of successful germination
- **PlantingEvent**: When/where plants are planted (lifecycle anchor)
  - `health_status`: Plant health (healthy, stressed, diseased)
  - `plant_notes`: Observations about the plants
- **CareTask**: Unified task model (auto-generated or manual)
  - `task_type`: Includes multiple task categories:
    - Outdoor: water, fertilize, prune, mulch, weed, pest_control, harvest
    - Indoor: adjust_lighting, adjust_temperature, adjust_humidity, nutrient_solution, train_plant
    - Hydroponics: check_nutrient_solution, adjust_ph, replace_nutrient_solution, clean_reservoir, adjust_water_circulation
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
├── CareTasks
└── SensorReadings

Garden
├── PlantingEvents
└── SensorReadings (indoor gardens only)

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

## Local Testing (Recommended)

**Backend:**
```bash
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

**That's it!** No Docker, no database setup, no complex configuration.

---

The project uses a **hybrid testing model**:
- ✅ **Tests run locally** (no Docker required)
- ✅ **Docker is for services only** (database, API, frontend)
- ✅ **Fast, simple, Docker-free testing**

#### Backend Tests (pytest)

**Prerequisites:**
```bash
# Install dependencies in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Run all backend tests:**
```bash
# Run all tests (uses in-memory SQLite, no external database needed)
pytest

# Coverage is automatically generated (configured in pytest.ini)
# View coverage report: open htmlcov/index.html
```

**Note:** Tests use in-memory SQLite databases (see `tests/conftest.py`). No PostgreSQL or Docker required.

**Run specific test suites:**
```bash
# Model/Database tests
pytest tests/test_models.py

# API endpoint tests
pytest tests/test_api.py

# Rule engine tests (outdoor)
pytest tests/test_rules.py
pytest tests/test_task_generator.py

# Indoor gardening rules
pytest tests/test_indoor_rules.py

# Hydroponics rules
pytest tests/test_hydroponics_rules.py

# Integration tests
pytest tests/test_integration.py

# Run specific test
pytest tests/test_rules.py::TestHarvestRule::test_harvest_rule_generates_task
```

**Test Coverage:**
- ✅ Models & Database: All CRUD operations, relationships, cascade deletes
- ✅ API Endpoints: Auth, gardens, planting events, tasks, sensor readings, user profiles
- ✅ Business Logic: All rule engines (outdoor, indoor, hydroponics)
- ✅ Edge Cases: Invalid input, unauthorized access, error handling
- ✅ Integration: Full user workflows from registration to harvest

Tests use an in-memory SQLite database and do not require external services.

#### Frontend Tests (Vitest + React Testing Library)

**Install frontend test dependencies:**
```bash
cd frontend
npm install
```

**Run all frontend tests:**
```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with UI
npm test -- --ui

# Generate coverage report
npm test -- --coverage
```

**Test Coverage:**
- ✅ Dashboard: Loading states, gardens display, tasks display, error handling
- ✅ Auth: Login, registration, form validation, error messages
- ✅ Create Garden: Outdoor, indoor, and hydroponic garden forms
- ✅ Create Sensor Reading: Indoor and hydroponics sensor data
- ✅ Task List: Display, filtering, completion, priority indicators
- ✅ Component Interactions: Form submissions, API calls, user events

#### Integration Tests (End-to-End Workflows)

Integration tests verify complete user workflows:

```bash
# Run only integration tests
pytest tests/test_integration.py -v

# Specific workflow tests
pytest tests/test_integration.py::TestCompleteOutdoorGardeningWorkflow
pytest tests/test_integration.py::TestCompleteIndoorGardeningWorkflow
pytest tests/test_integration.py::TestCompleteHydroponicsWorkflow
```

**Tested Workflows:**
- ✅ Complete Outdoor Gardening: Register → Create Garden → Plant → Complete Tasks → Harvest
- ✅ Complete Indoor Gardening: Register → Indoor Garden → Plant → Monitor Sensors → Adjust
- ✅ Complete Hydroponics: Register → Hydro Garden → Plant → Monitor Nutrients → Adjust pH/EC
- ✅ Multi-Garden Management: Multiple gardens with different types
- ✅ Error Recovery: Invalid data, unauthorized access, API failures

#### Docker Usage

**Docker is for running SERVICES, not tests:**

```bash
# Start services (database, API, frontend)
docker-compose up

# Services available at:
# - API: http://localhost:8080
# - Frontend: http://localhost:3000
# - Database: localhost:5432
```

**DO NOT run tests in Docker locally.** Use `pytest` and `npm test` instead.

**Docker tests are for CI/CD only** (smoke tests, deployment verification).

#### Coverage Reports

After running tests with coverage, view detailed HTML reports:

**Backend:**
```bash
pytest --cov=app --cov-report=html tests/
open htmlcov/index.html
```

**Frontend:**
```bash
cd frontend
npm test -- --coverage
open coverage/index.html
```

**Coverage Summary:**
- Backend: 90%+ coverage (models, API, rules, repositories)
- Frontend: 85%+ coverage (components, forms, interactions)
- Integration: All critical user workflows tested

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
- `GET /users/me` - Get current user info (includes profile fields)
- `PATCH /users/me` - Update user profile (display_name, avatar_url, city, gardening_preferences)
- `POST /auth/password-reset/request` - Request password reset email (unauthenticated)
- `POST /auth/password-reset/confirm` - Confirm password reset with token
- `GET /auth/password-reset/requirements` - Get password strength requirements
- `POST /auth/password/change` - Change password (authenticated, requires current password)
- `POST /auth/password-reset/request-authenticated` - Request password reset email (authenticated users)

#### Password Management Options

Logged-in users can manage their passwords in two ways:

1. **Change Password Directly** (Recommended when you know your current password)
   - Go to Profile > Security tab
   - Enter current password, new password, and confirm
   - Immediate password update without email

2. **Reset via Email** (Useful for forgotten passwords or security)
   - Go to Profile > Security tab > "Send Password Reset Email"
   - Receive reset link via email (or check backend logs in dev mode)
   - Click link to set new password

For detailed password reset documentation, see [PASSWORD_RESET.md](PASSWORD_RESET.md)

### Gardens
- `POST /gardens` - Create garden (outdoor, indoor, or hydroponic)
  - Outdoor garden fields: `name`, `description`, `garden_type: "outdoor"`
  - Indoor garden fields (all optional): `location`, `light_source_type`, `light_hours_per_day`, `temp_min_f`, `temp_max_f`, `humidity_min_percent`, `humidity_max_percent`, `container_type`, `grow_medium`
  - Hydroponics fields (when `is_hydroponic: true`): `hydro_system_type`, `reservoir_size_liters`, `nutrient_schedule`, `ph_min`, `ph_max`, `ec_min`, `ec_max`, `ppm_min`, `ppm_max`, `water_temp_min_f`, `water_temp_max_f`
- `GET /gardens` - List user's gardens (includes indoor and hydroponics metadata)
- `GET /gardens/{id}` - Get garden
- `GET /gardens/{id}/sensor-readings` - Get all sensor readings for a specific garden (sorted by date, most recent first)
- `PATCH /gardens/{id}` - Update garden
- `DELETE /gardens/{id}` - Delete garden (cascades to delete plantings, sensor readings, soil samples, and irrigation events)

### Sensor Readings (Indoor & Hydroponic Gardens)
- `POST /sensor-readings` - Create sensor reading (+ auto-generates warning tasks if out of range)
  - Required: `garden_id`, `reading_date`
  - Indoor optional: `temperature_f`, `humidity_percent`, `light_hours`
  - Hydroponics optional: `ph_level`, `ec_ms_cm`, `ppm`, `water_temp_f`
  - Automatically generates HIGH priority tasks when readings exceed safe ranges
- `GET /sensor-readings` - List sensor readings (filterable by garden_id, start_date, end_date)
- `GET /sensor-readings/{id}` - Get specific reading
- `DELETE /sensor-readings/{id}` - Delete reading

### Plant Varieties
- `GET /plant-varieties` - List varieties (searchable, includes photo_url and tags)
- `GET /plant-varieties/{id}` - Get variety

### Seed Batches
- `POST /seed-batches` - Create seed batch (+ auto-generates viability tasks)
  - Accepts `preferred_germination_method` field
- `GET /seed-batches` - List user's batches (includes plant variety with photos/tags)
- `GET /seed-batches/{id}` - Get batch
- `PATCH /seed-batches/{id}` - Update batch (including preferred_germination_method)
- `DELETE /seed-batches/{id}` - Delete batch

### Germination Events
- `POST /germination-events` - Create event
- `GET /germination-events` - List user's events
- `GET /germination-events/{id}` - Get event
- `PATCH /germination-events/{id}` - Update event (including `germination_success_rate`)

### Planting Events
- `POST /planting-events` - Create event (+ auto-generates care tasks with priorities)
  - Accepts `health_status` and `plant_notes` fields
- `GET /planting-events` - List user's events (filterable by garden_id)
- `GET /planting-events/{id}` - Get event
- `PATCH /planting-events/{id}` - Update event (including health status and notes)
- `DELETE /planting-events/{id}` - Delete planting event (cascades to delete associated care tasks; preserves historical sensor readings, soil samples, and irrigation events)

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
