# Learning Guide: FastAPI + SQLAlchemy + Alembic + Pydantic + PostgreSQL

A phased, hands-on checklist for wiring these tools together. No code here on purpose — just
hints and the "why" so you build the muscle memory yourself.

**Domain for this project:** `Professor`, `Subject`, `Assignment` (an assignment links a
professor to a subject — a classic many-to-many-with-extra-data relationship).

---

## Current State (what the scan found)

- Dependencies already installed: `alembic`, `fastapi[standard]`, `psycopg[binary]`, `pydantic`, `sqlalchemy`.
- `app/database.py` — has `engine` created from `DATABASE_URL`. Missing `SessionLocal` and `Base`.
- `app/main.py` — only a stub `main()` function; no FastAPI app object yet.
- `app/models/`, `app/schemas/`, `app/api/` — empty files for subject/professor/assignment.
- `app/config.py` — empty.
- `.env` — has `DATABASE_URL`, but it ends at `...:5432` with **no database name**. Fix this early.
- No `alembic.ini` / `alembic/` directory yet — Alembic is installed but not initialized.

---

## Phase 0 — Environment & Database Sanity Check

Goal: make sure Postgres is reachable before writing any app code.

- [ ] Confirm PostgreSQL is running locally and you can connect (try `psql`).
- [ ] Create the actual database you'll use (e.g. `learn_be`). The server having Postgres is not
      the same as the database existing.
- [ ] Fix `.env`: the `DATABASE_URL` is missing the DB name after the port. Format is
      `postgresql+psycopg://user:password@host:port/DBNAME`. Right now it stops at `:5432`.
- [ ] Decide: do you want secrets like the raw URL in `.env` only, or loaded through a typed
      settings object? (You'll build the typed version in Phase 1.)
- [ ] Hint: `psycopg[binary]` is the driver; the `+psycopg` in the URL tells SQLAlchemy to use it.

---

## Phase 1 — Configuration Layer (Pydantic Settings)

Goal: stop reading `os.getenv` scattered everywhere. Centralize config.

- [ ] In `app/config.py`, build a settings class using `pydantic-settings` (note: in Pydantic v2,
      `BaseSettings` moved to the separate `pydantic-settings` package — you may need to add it).
- [ ] Have the settings class read the `DATABASE_URL` (and later, other env vars) from `.env`.
- [ ] Expose a single `settings` instance that the rest of the app imports.
- [ ] Refactor `app/database.py` to pull the URL from `settings` instead of calling `os.getenv`
      directly. One source of truth.
- [ ] Hint: this is where you learn the difference between Pydantic *models* (request/response
      validation) and Pydantic *settings* (env/config). Same library, different jobs.

---

## Phase 2 — SQLAlchemy Foundation (engine, session, Base)

Goal: establish the three pillars every SQLAlchemy app needs.

- [ ] In `app/database.py`, keep the `engine`, then add:
  - [ ] A **session factory** (`sessionmaker`) bound to the engine.
  - [ ] A **declarative `Base`** class that all models will inherit from (SQLAlchemy 2.0 style uses
        `DeclarativeBase`).
- [ ] Write a **dependency function** that yields a session and closes it afterwards. This is what
      your FastAPI routes will depend on (think `try/finally` so the session always closes).
- [ ] Hint: understand *why* a session is per-request, not global. Sessions are not thread-safe and
      hold transaction state.

---

## Phase 3 — Define the ORM Models

Goal: describe your tables as Python classes.

- [ ] In `app/models/professor.py`, `subject.py`, `assignment.py`, define classes inheriting `Base`.
- [ ] Give each a `__tablename__`, a primary key, and real columns (name, title, etc.).
- [ ] Model the relationships:
  - [ ] An `Assignment` references a professor and a subject (foreign keys).
  - [ ] Decide whether you want `relationship()` back-references so you can navigate
        `professor.assignments`, etc.
- [ ] Make sure `app/models/__init__.py` imports all three models. Alembic autogenerate (Phase 4)
      can only "see" models that have been imported — this is the #1 beginner gotcha.
- [ ] Hint: SQLAlchemy 2.0 prefers `Mapped[...]` type annotations with `mapped_column(...)`. Learn
      this modern style rather than the older `Column(...)` form.

---

## Phase 4 — Alembic Migrations

Goal: version-control your schema instead of hand-creating tables.

- [ ] Initialize Alembic in the project root (creates `alembic.ini` + an `alembic/` folder).
- [ ] Edit `alembic/env.py` so it knows about:
  - [ ] Your `Base.metadata` (set `target_metadata`) — so autogenerate detects your models.
  - [ ] Your database URL — pull it from your settings/`.env`, not the hardcoded value in
        `alembic.ini`. (You can override `sqlalchemy.url` programmatically in `env.py`.)
  - [ ] Import your models (or `app.models`) so they're registered on `Base` before autogenerate runs.
- [ ] Generate your first migration with `--autogenerate` and a message.
- [ ] **Read the generated migration file before applying it.** Autogenerate is a helper, not an
      oracle — verify it did what you expect.
- [ ] Apply it (`upgrade head`) and confirm the tables exist in Postgres.
- [ ] Practice the loop: change a model → autogenerate → review → upgrade. Also try `downgrade`.
- [ ] Hint: never use `Base.metadata.create_all()` in a project that uses Alembic — pick one source
      of schema truth. Alembic wins here.

---

## Phase 5 — Pydantic Schemas (request/response models)

Goal: separate your API's data contracts from your DB tables.

- [ ] In `app/schemas/`, create schemas per entity. Typically you'll want variants:
  - [ ] A "create" schema (input — no id yet).
  - [ ] A "read/response" schema (output — includes id and server-set fields).
  - [ ] Optionally an "update" schema (all fields optional).
- [ ] Enable ORM compatibility on read schemas so a SQLAlchemy object can be returned directly
      (Pydantic v2: `model_config = ConfigDict(from_attributes=True)`).
- [ ] Hint: understand *why* ORM models and Pydantic schemas are kept separate — security (don't
      leak columns), decoupling the API shape from the DB shape, and validation.

---

## Phase 6 — API Routes (FastAPI wiring)

Goal: expose CRUD endpoints that use the session dependency.

- [ ] First, fix `app/main.py`: create the FastAPI **app instance** (the current `main()` stub is
      not a FastAPI app and won't serve anything).
- [ ] In each `app/api/*.py`, create an `APIRouter` for that entity and define endpoints
      (create, list, get-by-id, update, delete).
- [ ] Each route should depend on the DB session dependency from Phase 2, and use Pydantic schemas
      for input/output (set `response_model`).
- [ ] Register (`include_router`) all routers on the app in `main.py`, ideally with URL prefixes
      and tags.
- [ ] Hint: keep the routes thin. Query/commit/refresh logic can live inline at first, but notice
      when it starts repeating — that's the signal to extract a service/CRUD layer later.

---

## Phase 7 — Run, Test, Iterate

Goal: see it all working end to end.

- [ ] Run the dev server with `fastapi dev` (or `uvicorn`) pointing at your app object.
- [ ] Open the auto-generated docs at `/docs` and exercise each endpoint.
- [ ] Create a professor, a subject, then an assignment linking them — this proves your
      relationships and foreign keys work.
- [ ] Verify the rows actually landed in Postgres (`psql` or a GUI).
- [ ] Hint: watch what happens when you POST invalid data — that's Pydantic validation doing its job
      and returning 422s for free.

---

## Phase 8 — Reinforce the Whole Loop (optional but recommended)

- [ ] Add a new column to a model, run the full Alembic cycle, and confirm the API reflects it.
- [ ] Add a unique constraint or index via a migration and watch autogenerate detect it.
- [ ] Try a downgrade and re-upgrade to understand reversibility.
- [ ] Write a couple of tests (`pytest` + `httpx`/FastAPI `TestClient`) hitting your endpoints,
      ideally against a throwaway/test database.

---

## Mental Model Cheat-Sheet

- **PostgreSQL** = where data lives.
- **psycopg** = the driver that lets Python talk to Postgres.
- **SQLAlchemy** = maps Python classes ↔ tables, manages sessions/transactions.
- **Alembic** = git-for-your-schema; turns model changes into versioned migrations.
- **Pydantic** = validates/serializes data crossing the API boundary (and loads config).
- **FastAPI** = the web layer that ties request → validation → session → DB → response.

**The request lifecycle to internalize:**
`HTTP request → FastAPI route → Pydantic validates input → DB session dependency → SQLAlchemy
query/commit → ORM object → Pydantic serializes output → HTTP response.`

---

## Suggested Order If You Get Lost

0 → 1 → 2 → 3 → 4 (get migrations working and tables created *before* building the API) → 5 → 6 → 7.
Don't skip ahead to routes before the schema exists in the DB; debugging is much harder that way.
