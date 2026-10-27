# Blood Donation Manager — Project Presentation

**9-Slide Presentation** | **Presenter:** Puneet Goswami | **Project:** Blood Donation Management System

---

## Slide 1 — Project Introduction

**Project Name:** Blood Donation Manager  
**Presenter:** [Your Name]  
**Program:** Internship / Training Program  
**One-line description:** A full-stack web application that centralizes donor registration, blood requests, and donation coordination in one secure platform.

**Key facts:**
- Full-stack: React + Vite (frontend) · FastAPI + SQLAlchemy (backend) · PostgreSQL (database)
- Role-based access: Donor, Requester, Administrator
- JWT authentication with bcrypt password hashing
- 5 backend API workflow tests passing
- Responsive UI for mobile and desktop

---

## Slide 2 — Problem Statement

**The Problem:**
Blood donation coordination is scattered across phone contacts, spreadsheets, messaging groups, and social media. This makes it difficult to:
- Find current donor information by blood group and location
- Know whether a donor is available to be contacted
- Track the status of blood requests (pending, in progress, fulfilled, cancelled)
- Maintain oversight of donor records and open requests
- Protect donor privacy — contact details should not be exposed unnecessarily

**Who experiences it:** Hospitals, blood banks, requesters coordinating urgent needs, and volunteer donors.

**Why a digital solution:** Centralized, searchable records with role-based access control, request status tracking, and privacy-protected donor search.

---

## Slide 3 — Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite | UI framework and build tool |
| **Frontend styling** | Custom CSS | Responsive design, mobile-first breakpoints |
| **Frontend state** | React Hook Form, React Router | Form validation and client-side routing |
| **Backend** | FastAPI (Python) | REST API framework |
| **ORM** | SQLAlchemy | Database modeling and queries |
| **Database** | PostgreSQL | Relational data store |
| **Migrations** | Alembic | Schema versioning |
| **Authentication** | JWT (python-jose) + bcrypt | Stateless tokens, hashed passwords |
| **Validation** | Pydantic | Request/response schema validation |
| **Testing** | pytest | API workflow tests |
| **DevOps** | Docker, Docker Compose | Containerized deployment |
| **CI/CD** | GitHub Actions | Automated testing and linting |


---

## Slide 4 — Application Features

**Core Features (MVP):**

1. **Authentication** — Register, login, logout with JWT; session restore on refresh
2. **Role-Based Access** — Donor, Requester, Administrator permissions
3. **Donor Registration** — Create donor profile with blood group, city, phone, availability, contact consent
4. **Donor Search** — Filter consenting donors by blood group, city, availability (phone hidden)
5. **Blood Requests** — Create, view, update, cancel requests with status lifecycle
6. **Request Status Tracking** — pending → in_progress → fulfilled/cancelled; full history audit trail
7. **Donation Coordination** — Admin links donors to requests; tracks contact status
8. **Dashboard** — Role-scoped statistics for donors, requesters, and admins
9. **Responsive UI** — Works on mobile (600px), tablet (800px), and desktop

**Screenshots available in:** README.md — Login page, Register page, Dashboard, Donor search, Blood requests, Swagger API docs

---

## Slide 5 — System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  http://localhost:5173                                          │
│                                                                 │
│  Pages: Login · Register · Dashboard · Donors · Requests       │
│  Context: AuthContext (JWT stored in localStorage)             │
│  Services: axios with automatic Bearer token injection         │
└──────────────────┬──────────────────────────────────────────────┘
                   │ HTTPS / API calls (proxied via Vite in dev)
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│  http://localhost:8000                                          │
│                                                                 │
│  Routes: /auth · /donors · /requests · /coordinations           │
│         /dashboard · /admin                                     │
│                                                                 │
│  Services: Auth · Donor · Request · Coordination · Dashboard    │
│  Security: JWT verification · Role checks · Ownership checks    │
└──────────────────┬──────────────────────────────────────────────┘
                   │ SQLAlchemy ORM
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                        │
│                                                                 │
│  Tables: users · donors · blood_requests ·                      │
│          donation_coordination · request_status_history         │
│                                                                 │
│  Constraints: Unique emails, unique donor per user,             │
│               unique coordination per request+donor pair        │
└─────────────────────────────────────────────────────────────────┘
```

**Data flow:** User action → Frontend API call → FastAPI route → Service layer → SQLAlchemy → PostgreSQL → Response back to frontend

---

## Slide 6 — Testing and Bug Fixes

**Testing approach:**
- **Backend:** 5 pytest API workflow tests covering registration, login, donor search, request lifecycle, coordination, admin dashboard
- **Frontend:** ESLint with 0 warnings; manual testing of all UI flows
- **API:** Swagger UI (/docs) used to verify every endpoint status code and validation

**Test results summary:**
| Category | Passed | Failed | Not Tested |
|----------|--------|--------|------------|
| Authentication | 12 | 0 | 3 |
| Donor Profile | 13 | 0 | 0 |
| Blood Requests | 18 | 0 | 0 |
| Coordination | 8 | 0 | 0 |
| Dashboard | 4 | 0 | 0 |
| Database/Persistence | 7 | 0 | 0 |
| Frontend UI | 10 | 0 | 0 |
| **Total** | **72** | **0** | **3** |

**Key bugs found and fixed:**
- Dashboard "pending" stat for donors showed `total_requests` instead of `pending_requests` → Fixed to show correct count
- No code regressions introduced; all 5 backend tests still pass

**Security verified:**
- Passwords hashed with bcrypt (never plain text)
- JWT tokens expire after 60 minutes
- `.env` files excluded from Git (`.gitignore`)
- Donor phone numbers hidden from search results
- Role-based access enforced on every protected endpoint


---

## Slide 7 — Live Demo

**Complete user journey (5 minutes):**

1. **Register** — Create a donor account (name, email, password, role=donor)
2. **Create donor profile** — Add blood group, phone, city, availability, consent to contact
3. **Login as requester** — Separate account with role=requester
4. **Create blood request** — Select blood group, units, hospital, city, urgency
5. **Search donors** — Filter by blood group and location; view consenting donors (phones hidden)
6. **Admin coordination** — Login as admin, link donor to request, update coordination status
7. **Track request** — Watch status change: pending → in_progress → fulfilled
8. **View dashboard** — See role-scoped statistics update in real time

**API demonstration:** Open http://localhost:8000/docs to test endpoints directly with Swagger UI

**Demo credentials:**
- Donor: Register any donor account
- Requester: Register any requester account  
- Admin: Created via `python create_admin.py` after migrations

---

## Slide 8 — Challenges and Learnings

**Challenges solved:**

1. **Role-based authorization** — Ensuring donors can only see open requests, requesters only see their own requests, admins see everything. Solved with dependency injection (`get_current_user` + `require_role`) and ownership checks in every service method.

2. **Request status lifecycle** — Preventing invalid status transitions (e.g., pending → fulfilled directly). Solved with an `allowed_transitions` map that validates every status change.

3. **Donor privacy** — Ensuring phone numbers are never exposed in search results. Solved with separate `DonorSearchOut` schema that excludes contact fields, plus `consent_to_contact` filtering.

4. **Session persistence** — Maintaining login state across page refreshes. Solved with AuthContext that restores token from localStorage and verifies via `/auth/me` on mount.

**Key learnings:**
- Backend authorization is the source of truth; frontend role-gating is UX only
- Pydantic schemas provide automatic validation and clear error messages
- Alembic migrations make schema changes safe and versioned
- Writing tests first catches edge cases (duplicate emails, invalid transitions, unauthorized access)
- Separation of concerns (routes → services → models) makes code maintainable

---

## Slide 9 — Conclusion and Q&A

**What was completed:**
- Full-stack Blood Donation Management System with authentication, role-based access, donor management, request tracking, and admin coordination
- 5 backend API workflow tests passing; ESLint clean; Python compile clean
- Responsive UI tested on mobile, tablet, and desktop
- Security: bcrypt hashing, JWT expiry, role enforcement, privacy-protected search

**Future improvements:**
- Email notifications for status changes
- Donor response to coordination (accept/decline)
- Request auto-expiry
- Hospital directory and donation history
- Distance-based search and admin analytics

**Thank you!** Questions welcome.

**Demo links:**
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- GitHub: https://github.com/puneetg0/Blood-Donation

