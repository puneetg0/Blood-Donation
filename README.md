# Blood Donation Manager

A full-stack web application to organize blood donor information and manage blood donation requests in one centralized system.

**Stack:** React + Vite (frontend) · FastAPI + SQLAlchemy (backend) · PostgreSQL (database)

---

## Project Status

| Area | Status |
|---|---|
| Project setup & folder structure | ✅ Done |
| Database models (all 5 tables) | ✅ Done |
| Authentication (register, login, JWT) | ✅ Done |
| Role-based access control | ✅ Done |
| Donor CRUD APIs | ✅ Done |
| Blood Request CRUD APIs | ✅ Done |
| Donation Coordination APIs | ✅ Done |
| API validation (Pydantic schemas) | ✅ Done |
| Backend modules organized | ✅ Done |
| HashMap-style PK lookups | ✅ Done |
| Database migrations (Alembic) | ✅ Done |
| Frontend pages (Login, Register, Dashboard) | ✅ Done |
| Frontend-backend integration | ✅ Done |
| Admin dashboard and request coordination | ✅ Done |
| Donor/request filtering and responsive layouts | ✅ Done |
| Input validation and role/ownership checks | ✅ Done |
| API workflow tests | ✅ Done |

---

## One-Time Database Setup

Run this **once** before starting the app. Open a terminal and connect to PostgreSQL as the superuser. Replace the example password with a unique local password and use the same value in `DATABASE_URL`:

```bash
psql -U postgres
```

Then run:

```sql
CREATE USER bdm_user WITH LOGIN;
\password bdm_user
CREATE DATABASE blood_donation OWNER bdm_user;
GRANT ALL PRIVILEGES ON DATABASE blood_donation TO bdm_user;
\q
```

Copy `..\.env.example` to `backend\.env`, set `DATABASE_URL`, `SECRET_KEY` to a long random value, and configure `CORS_ORIGINS` before running migrations.

Then create the tables:

```bash
cd backend
.venv\Scripts\activate
alembic upgrade head
```

Never commit `backend\.env` or use example values in production.

---

## Running the App

Open **two terminals**.

**Terminal 1 — Backend:**
```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload
```
API runs at: http://localhost:8000
Interactive docs: http://localhost:8000/docs

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```
App runs at: http://localhost:5173

### Create an administrator account

Public registration supports donor and requester roles only. After applying migrations, create an administrator interactively from the `backend` directory:

```bash
.venv\Scripts\activate
python create_admin.py
```

The command prompts for the name, email, and password; the password is not echoed or passed on the command line.

---

## How to Showcase / Demo the Project

### Step 1 — Open the interactive API docs
Go to **http://localhost:8000/docs** in your browser.
This is Swagger UI — it lets you test every API endpoint without Postman.

---

### Step 2 — Register a user account
Click `POST /api/auth/register` → **Try it out** → paste this body:

```json
{
  "full_name": "Puneet Goswami",
  "email": "puneet@example.com",
  "password": "password123",
  "role": "donor"
}
```

Click **Execute**. You will get back a JWT token and user object.

---

### Step 3 — Authorize with the token
1. Copy the `access_token` value from the response.
2. Click the **Authorize** button (top right of Swagger UI, lock icon).
3. Paste the token. Click **Authorize**.

All protected endpoints will now work with your token.

---

### Step 4 — Create a donor profile
Click `POST /api/donors/` → **Try it out**:

```json
{
  "blood_group": "O+",
  "phone_number": "9876543210",
  "city": "Delhi",
  "availability_status": "available",
  "consent_to_contact": true
}
```

---

### Step 5 — Create a blood request
Click `POST /api/requests/` → **Try it out**:

```json
{
  "blood_group": "O+",
  "units_required": 2,
  "hospital_name": "AIIMS Delhi",
  "city": "Delhi",
  "urgency": "urgent"
}
```

---

### Step 6 — Search donors
Click `GET /api/donors/` → **Try it out**.
Filter by `blood_group=O+`, `city=Delhi`, and `availability_status=available`. Search results include only donors who consented to appear and never include phone numbers.

---

### Step 7 — List all blood requests
Click `GET /api/requests/` → **Try it out**.
Filter by `status=pending` or `blood_group=O+`.

---

### Step 8 — Update a request status
Administrator accounts can change a request from pending to in progress, then to fulfilled or cancelled. Request owners can cancel their own open requests. Each status change is retained in status history.

Click `PATCH /api/requests/{request_id}` as an administrator → **Try it out**:

```json
{
  "status": "in_progress"
}
```

---

### Step 9 — Test the frontend
Go to **http://localhost:5173** and:
- Register a new account
- Log in
- View the dashboard

---

## API Endpoints Summary

### Auth
| Method | URL | Description |
|---|---|---|
| POST | /api/auth/register | Create account, returns JWT |
| POST | /api/auth/login | Login, returns JWT |
| GET | /api/auth/me | Get logged-in user profile |

### Donors
| Method | URL | Description |
|---|---|---|
| POST | /api/donors/ | Create donor profile |
| GET | /api/donors/ | Search consenting donors (filter: blood_group, city, availability_status; `offset`/`limit`) |
| GET | /api/donors/me | My donor profile |
| GET | /api/donors/{id} | Get private donor profile (owner or administrator only) |
| PATCH | /api/donors/{id} | Update donor profile |
| DELETE | /api/donors/{id} | Delete donor profile |

### Blood Requests
| Method | URL | Description |
|---|---|---|
| POST | /api/requests/ | Create blood request |
| GET | /api/requests/ | List requests visible to the current role (filter: blood_group, city, status; `offset`/`limit`) |
| GET | /api/requests/me | My requests |
| GET | /api/requests/{id}/history | Request status history (owner or administrator) |
| GET | /api/requests/{id} | Get request by ID |
| PATCH | /api/requests/{id} | Update request |
| DELETE | /api/requests/{id} | Delete request |

### Coordinations
| Method | URL | Description |
|---|---|---|
| POST | /api/coordinations/ | Link an available, consenting donor (administrator only) |
| GET | /api/coordinations/request/{id} | List coordinations for a request |
| GET | /api/coordinations/{id} | Get coordination by ID |
| PATCH | /api/coordinations/{id} | Update coordination status |
| DELETE | /api/coordinations/{id} | Remove coordination |

### Dashboard
| Method | URL | Description |
|---|---|---|
| GET | /api/dashboard/summary | Counts scoped to the current user's access |
| GET | /api/admin/dashboard | System-wide counts for administrators |

Donor search uses `availability_status` and `offset`/`limit` (maximum 100 records per page). Only donors who opted in to contact/search are returned. `GET /api/donors/me` returns the caller's own complete profile; individual donor records with private contact data are limited to the owner and administrators.

Request list visibility is role-scoped: requesters see their own requests, donors see open requests, and administrators see all requests. Only administrators can manage coordination records and advance request statuses; terminal statuses cannot be reopened.

---

## Backend Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py          # register, login, /me
│   │       ├── donors.py        # donor CRUD
│   │       ├── requests.py      # blood request CRUD
│   │       └── coordinations.py # coordination CRUD
│   ├── core/
│   │   ├── config.py            # reads .env settings
│   │   └── security.py          # bcrypt + JWT utilities
│   ├── db/
│   │   └── session.py           # DB engine, Base, get_db
│   ├── dependencies/
│   │   └── auth.py              # get_current_user, require_role
│   ├── models/
│   │   ├── enums.py             # all enum types
│   │   └── user.py              # all SQLAlchemy table models
│   ├── schemas/
│   │   ├── user.py              # auth schemas
│   │   ├── donor.py             # donor schemas
│   │   ├── blood_request.py     # request schemas
│   │   └── coordination.py      # coordination schemas
│   ├── services/
│   │   ├── auth_service.py      # register + login logic
│   │   ├── donor_service.py     # donor CRUD logic
│   │   ├── request_service.py   # request CRUD logic
│   │   └── coordination_service.py
│   └── main.py                  # FastAPI app entry point
├── alembic/                     # database migrations
├── tests/                       # API workflow tests
├── create_admin.py              # interactive administrator setup
├── requirements.txt
└── .env                         # secrets (not committed)
```

---

## Key Concepts Used

- **HashMap-style lookups:** `db.get(Model, id)` — direct primary key access, like a dictionary lookup, instead of scanning all rows.
- **Pydantic validation:** All API inputs are validated automatically. Invalid data returns a clear error before it touches the database.
- **JWT authentication:** Stateless tokens. The server does not store sessions — the token carries the user identity.
- **Role-based access:** `require_role(Role.admin)` dependency can be added to any route to restrict access.
- **Alembic migrations:** Schema changes are tracked and versioned. Run `alembic upgrade head` to apply all pending changes.

## Tests and quality checks

From the repository root:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest -q

Set-Location ..\frontend
npm run lint
npm run build
```

The API workflow tests cover input validation, donor privacy/consent, request ownership and lifecycle, coordination authorization, and administrator dashboard access.

---

## Screenshots

| Page | Description |
|------|-------------|
| `docs/screenshots/login.png` | Login page — authenticate with email and password |
| `docs/screenshots/register.png` | Register page — create a new donor or requester account |
| `docs/screenshots/dashboard.png` | Dashboard — role-scoped stats and quick actions |
| `docs/screenshots/donors.png` | Donor search — filter by blood group, city, availability |
| `docs/screenshots/requests.png` | Blood requests — create, view, update, cancel requests |
| `docs/screenshots/api-docs.png` | Interactive API docs (Swagger UI) at `/docs` |

> Place actual screenshot images in `docs/screenshots/` to populate this section.

---

## Deployment

### Docker Compose (recommended)

```bash
# Clone the repo
git clone https://github.com/puneetg0/Blood-Donation.git
cd Blood-Donation

# Configure production environment
cp .env.production.example .env
# Edit .env with your SECRET_KEY and CORS_ORIGINS

# Start all services
docker compose up -d
```

Services:
- **Backend API**: http://localhost:8000 (Swagger docs at /docs)
- **Frontend**: http://localhost:5173
- **PostgreSQL**: localhost:5432

Stop services:
```bash
docker compose down
```

### Manual deployment

1. **Backend:** See "Running the App" above. Use a production WSGI server (e.g., gunicorn) behind nginx.
2. **Frontend:** `npm run build` then serve the `dist/` folder with nginx or any static file host.
3. **Database:** Run `setup_db.sql` or `alembic upgrade head` against your PostgreSQL instance.

### GitHub Actions CI

Pushes and pull requests to `main` automatically run:
- Backend tests (pytest) against a PostgreSQL service container
- Frontend lint (ESLint) and production build (Vite)

See `.github/workflows/ci.yml`.

---

## Author

Puneet Goswami
