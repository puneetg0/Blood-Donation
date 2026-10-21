# Blood Donation Manager — Database Design

PostgreSQL is the system of record. SQLAlchemy maps application models to tables, and Pydantic schemas validate API input and output. Foreign keys enforce relationships, and indexes support common searches.

## Tables

### users

| Column | Type | Constraints / purpose |
|---|---|---|
| id | Integer | Primary key |
| ull_name | String | Account holder's name |
| email | String | Unique login identifier |
| password_hash | String | Secure password hash; never store a plain-text password |
| ole | Enum | donor, equester, or dmin |
| is_active | Boolean | Whether the account can access the application |
| created_at | Timestamp | Account creation time |

### donors

| Column | Type | Constraints / purpose |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users.id; unique for one donor profile per account |
| lood_group | Enum | ABO/Rh group |
| phone | String | Contact number; protected personal information |
| city | String | City or locality used in search |
| vailability_status | Enum | vailable, unavailable, or unknown |
| consent_to_contact | Boolean | Contact preference |
| updated_at | Timestamp | Last profile update |

### lood_requests

| Column | Type | Constraints / purpose |
|---|---|---|
| id | Integer | Primary key |
| equester_id | Integer | Foreign key to users.id |
| lood_group | Enum | Requested blood group |
| units_required | Integer | Must be a positive value |
| hospital_name | String | Hospital or medical facility |
| city | String | Request location |
| urgency | Enum | outine, urgent, or emergency |
| equired_by | Timestamp | Requested time or deadline |
| status | Enum | pending, in_progress, ulfilled, or cancelled |
| created_at | Timestamp | Request creation time |

### donation_coordination

| Column | Type | Constraints / purpose |
|---|---|---|
| id | Integer | Primary key |
| equest_id | Integer | Foreign key to lood_requests.id |
| donor_id | Integer | Foreign key to donors.id |
| coordination_status | Enum | contact_pending, contacted, declined, or completed |
| created_at | Timestamp | Coordination record creation time |

Each coordination row connects one potential donor with one request. Coordination is not proof of eligibility or successful donation.

### equest_status_history

| Column | Type | Constraints / purpose |
|---|---|---|
| id | Integer | Primary key |
| equest_id | Integer | Foreign key to lood_requests.id |
| changed_by | Integer | Foreign key to users.id |
| previous_status | String / enum | Status before the change |
| 
ew_status | String / enum | Status after the change |
| 
ote | Text | Optional reason or update |
| created_at | Timestamp | Change timestamp |

This table provides a traceable history of request status changes.

## Entity Relationships

`mermaid
erDiagram
    USERS ||--o| DONORS : has
    USERS ||--o{ BLOOD_REQUESTS : creates
    BLOOD_REQUESTS ||--o{ DONATION_COORDINATION : includes
    DONORS ||--o{ DONATION_COORDINATION : participates
    BLOOD_REQUESTS ||--o{ REQUEST_STATUS_HISTORY : records
    USERS ||--o{ REQUEST_STATUS_HISTORY : changes

    USERS {
        int id PK
        string full_name
        string email UK
        string password_hash
        string role
    }
    DONORS {
        int id PK
        int user_id FK
        string blood_group
        string phone
        string city
        string availability_status
        boolean consent_to_contact
    }
    BLOOD_REQUESTS {
        int id PK
        int requester_id FK
        string blood_group
        int units_required
        string city
        string urgency
        string status
    }
    DONATION_COORDINATION {
        int id PK
        int request_id FK
        int donor_id FK
        string coordination_status
    }
    REQUEST_STATUS_HISTORY {
        int id PK
        int request_id FK
        int changed_by FK
        string previous_status
        string new_status
    }
`

## Domain Classes

The main application entities are modeled as User, Donor, and BloodRequest classes (or their SQLAlchemy/Pydantic equivalents):

- **User:** Account identity with id, ull_name, email, password_hash, ole, is_active, created_at.
- **Donor:** Donor profile linked to user_id, with lood_group, phone, city, vailability_status, consent_to_contact, updated_at.
- **BloodRequest:** Request linked to equester_id, with lood_group, units_required, hospital_name, city, urgency, equired_by, status, created_at.
