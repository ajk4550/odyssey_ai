![Odyssey AI](header.jpg)

# Odyssey AI

An AI-powered trip planning API built with FastAPI. Users first discover destination suggestions based on their preferences, then generate a full day-by-day itinerary for their chosen destination.

## How It Works

**Phase 1 — Discovery:** The user describes what kind of trip they want (vacation type, budget, interests, travel constraints). An AI agent suggests 5 destinations with travel times from the user's origin.

**Phase 2 — Planning:** The user picks a destination and provides dates. A second AI agent generates a detailed day-by-day itinerary with activities and estimated costs.

## Tech Stack

- **FastAPI** — API framework
- **PostgreSQL + SQLAlchemy (async)** — database and ORM
- **Alembic** — database migrations
- **OpenAI Agents SDK** — AI agent orchestration
- **OpenRouteService API** — geocoding and travel time calculations
- **Pydantic v2** — request/response validation

## Setup

**1. Clone the repo and create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Create a `.env` file** (see `.env.example`):

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/odyssey
OPENAI_API_KEY=your_openai_key
OPENROUTESERVICE_API_KEY=your_ors_key
```

**3. Run database migrations**

```bash
alembic upgrade head
```

**4. Start the server**

```bash
fastapi dev
```

## API Endpoints

### `POST /api/v1/suggest-destinations`

Returns 5 destination suggestions based on the user's criteria.

```json
{
  "origin": "Ithaca, NY",
  "vacation_type": "On a Lake",
  "month": "July",
  "budget": 2000,
  "interests": ["Kayaking", "Hiking"],
  "exclude": ["New York"],
  "max_travel_hours": 8
}
```

### `POST /api/v1/plan-trip`

Generates a full day-by-day trip itinerary. Trip is persisted to the database.

```json
{
  "origin": "Ithaca, NY",
  "destination_idea": "Burlington, VT",
  "start_date": "2026-07-10",
  "end_date": "2026-07-14",
  "budget": 2000,
  "interests": ["Kayaking", "Hiking"],
  "exclude": ["New York", "Swimming"]
}
```

## Project Structure

```
app/
├── ai_agents/          # AI agent logic and evaluator
├── api/                # FastAPI routes
├── core/               # Configuration
├── db/                 # Database session and init
├── models/             # SQLAlchemy models, Pydantic schemas, enums
├── prompts/            # Prompt builders for each agent
└── tools/              # Travel time tool (used by agents)
migrations/             # Alembic migration files
```
