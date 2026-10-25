# Blood Donation Manager — API Reference

Base URL: `http://localhost:8000/api`

Interactive documentation (Swagger UI): `http://localhost:8000/docs`

---

## Authentication

All endpoints require a valid JWT Bearer token unless marked as **public**.
Include the token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained via `POST /auth/register` or `POST /auth/login`.

---

## Roles

| Role | Description |
|------|-------------|
| `requester` | Can create/view own blood requests, search donors |
| `donor` | Can create/update own donor profile, view open requests |
| `admin` | Full access to all records, coordination management, admin dashboard |

---

## Endpoints

### Auth

#### POST /auth/register
Create a new account. Public. Returns a JWT token.

**Request body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "role": "requester"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| full_name | string | Yes | 2–100 characters |
| email | string | Yes | Valid email format, max 254 chars |
| password | string | Yes | 8–72 UTF-8 bytes |
| role | string | No | `"requester"` or `"donor"` (default: `"requester"`). `"admin"` is rejected. |

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": { "id": 1, "full_name": "John Doe", ... }
}
```

**Errors:** `409` email exists · `422` validation error

---

#### POST /auth/login
Authenticate with email + password. Public. Returns a JWT token.

**Request body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response (200):** Same shape as register.

**Errors:** `401` invalid credentials · `403` account deactivated

---

#### GET /auth/me
Get the profile of the currently authenticated user. Requires auth.

**Response (200):** User object (no password hash).

### Donors

#### POST /donors/
Create a donor profile. Requires `donor` role. One profile per account.

**Request body:**
```json
{
  "blood_group": "O+",
  "phone_number": "+1 (555) 123-4567",
  "city": "Springfield",
  "availability_status": "available",
  "consent_to_contact": true
}
```

**Response (201):** `DonorOut` object.

**Errors:** `403` donor role required · `409` profile already exists

---

#### GET /donors/
Search consenting donors. Requires auth. Returns only public fields (no phone).

**Query params:** `blood_group`, `city`, `availability_status`, `offset`, `limit` (max 100).

**Response (200):** Array of `DonorSearchOut` (id, blood_group, city, availability_status).

---

#### GET /donors/me
Get your own donor profile. Requires auth. Returns full profile including phone.

**Response (200):** `DonorOut` object.

---

#### GET /donors/{donor_id}
Get a donor profile by ID. Owners view their own; admins view any.

**Response (200):** `DonorOut` object.

**Errors:** `404` not found · `403` not authorized

---

#### PATCH /donors/{donor_id}
Update your donor profile. Partial update supported.

**Response (200):** Updated `DonorOut` object.

---

#### DELETE /donors/{donor_id}
Delete your donor profile. Not allowed if coordination history exists.

**Response (204):** No content.

**Errors:** `409` has coordination history

### Blood Requests

#### POST /requests/
Create a blood request. Requires auth. Requester is set to the logged-in user.

**Request body:**
```json
{
  "blood_group": "O+",
  "units_required": 2,
  "hospital_name": "City Hospital",
  "city": "Springfield",
  "urgency": "urgent",
  "required_by": "2026-11-01T10:00:00"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| blood_group | enum | Yes | ABO/Rh group |
| units_required | integer | Yes | ≥ 1 |
| hospital_name | string | Yes | 2–150 characters |
| city | string | Yes | 2–100 characters |
| urgency | enum | No | `routine`, `urgent`, `emergency` (default: `routine`) |
| required_by | datetime | No | ISO 8601 timestamp |

**Response (201):** `BloodRequestOut` object.

---

#### GET /requests/
List requests visible to the caller.

**Role-based visibility:**
- `requester`: Only their own requests
- `donor`: Open requests (`pending`, `in_progress`) only
- `admin`: All requests

**Query params:** `blood_group`, `city`, `status`, `offset`, `limit` (max 100).

**Response (200):** Array of `BloodRequestOut`.

---

#### GET /requests/me
List all requests created by the logged-in user.

**Response (200):** Array of `BloodRequestOut`.

---

#### GET /requests/{request_id}
Get a request by ID. Access rules: owner · donor (open only) · admin (any).

**Response (200):** `BloodRequestOut` object.

---

#### GET /requests/{request_id}/history
Get status change history. Owner or admin only.

**Response (200):** Array of `RequestStatusHistoryOut`.

---

#### PATCH /requests/{request_id}
Update a request. Partial update supported.

**Status transitions:**
| From | To | Who |
|------|----|-----|
| `pending` | `in_progress`, `cancelled` | Admin or owner (cancel only) |
| `in_progress` | `fulfilled`, `cancelled` | Admin only |
| `fulfilled` / `cancelled` | — | Terminal |

**Request body:** Same fields as create, all optional, plus `status`.

**Response (200):** Updated `BloodRequestOut`.

**Errors:** `409` invalid transition · `403` not authorized

---

#### DELETE /requests/{request_id}
Delete a request. Not allowed if it has coordination or status history — cancel instead.

**Response (204):** No content.

### Coordinations

#### POST /coordinations/
Link a donor to a blood request. Admin only.

**Request body:**
```json
{
  "request_id": 1,
  "donor_id": 5
}
```

**Response (201):** `CoordinationOut` object.

**Errors:** `403` admin only · `404` not found · `409` not available/consenting or already linked

---

#### GET /coordinations/request/{request_id}
List all coordination records for a request. Admin only.

**Response (200):** Array of `CoordinationOut`.

---

#### GET /coordinations/{coordination_id}
Get a single coordination record. Admin only.

**Response (200):** `CoordinationOut` object.

---

#### PATCH /coordinations/{coordination_id}
Update coordination status. Admin only.

**Transitions:** `contact_pending` → `contacted` → `declined`/`completed` (terminal).

**Request body:**
```json
{ "coordination_status": "contacted" }
```

---

#### DELETE /coordinations/{coordination_id}
Remove a coordination record. Admin only.

**Response (204):** No content.

### Dashboard

#### GET /dashboard/summary
Counts scoped to the current user's role. Requires auth.

**Response (200):**
```json
{
  "total_donors": 12,
  "total_requests": 8,
  "pending_requests": 3,
  "in_progress_requests": 2,
  "fulfilled_requests": 2,
  "cancelled_requests": 1
}
```

---

#### GET /admin/dashboard
System-wide summary for administrators only. Same response shape.

---

## Error Responses

All errors return JSON with a `detail` field:

```json
{ "detail": "Human-readable error message" }
```

| Status | Meaning |
|--------|---------|
| 401 | Unauthorized — missing/invalid token |
| 403 | Forbidden — insufficient permissions |
| 404 | Not found |
| 409 | Conflict — business rule violation |
| 422 | Validation error |

---

## Data Models

### User
`id` · `full_name` · `email` · `role` (`admin`/`donor`/`requester`) · `is_active` · `created_at`

### Donor
`id` · `user_id` · `blood_group` · `phone_number` · `city` · `availability_status` · `consent_to_contact` · `updated_at`

### BloodRequest
`id` · `requester_id` · `blood_group` · `units_required` · `hospital_name` · `city` · `urgency` · `required_by` · `status` · `created_at`

### DonationCoordination
`id` · `request_id` · `donor_id` · `coordination_status` · `created_at`

---

## Security

- Passwords hashed with bcrypt.
- JWT tokens use HS256, expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60).
- Donor phone numbers never exposed in search results.
- All mutating endpoints require authentication.