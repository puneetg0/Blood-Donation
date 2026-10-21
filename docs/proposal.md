# Blood Donation Manager — Proposal

**Planned development period:** Days 23–29  
**Project type:** Full-stack web application

## Project Overview

Blood Donation Manager is a web application for organizing donor profiles and blood requests in one place. Donors can maintain their profile and contact availability, requesters can submit and follow requests, and administrators can review records and coordinate the workflow.

### Technology choices

| Area | Choice |
|---|---|
| Frontend | React and Tailwind CSS |
| Backend | Python and FastAPI |
| Database | PostgreSQL |
| ORM and validation | SQLAlchemy and Pydantic |
| Version control | Git and GitHub |

### Important boundary

This application supports coordination only. It does not provide medical advice, determine donor eligibility or blood compatibility, or guarantee that a donor can fulfill a request. Donor availability is self-reported and is not a clinical assessment. The system will help organize coordination, not replace hospitals, blood banks, medical professionals, or clinical screening.

## Scope

The project addresses the following problem areas:

- **Scattered donor information:** Records in multiple places are hard to search and keep current.
- **Time-consuming discovery:** Finding potential donors by blood group and location can require manually checking many records.
- **Unclear availability:** A donor's current willingness to be contacted may not be known.
- **Untracked requests:** A requester may not know whether a request is new, being coordinated, fulfilled, or cancelled.
- **Limited oversight:** Administrators may lack a consistent view of donor records and open requests.
- **Privacy risks:** Contact details should not be exposed to people who do not need them.

The proposed solution is a centralized, searchable system with role-based access, donor availability, request tracking, and a record of status changes.

### MVP scope

The first release focuses on P0 features: authentication, role-based access, donor registration, donor profile and availability management, authorized donor search, blood request creation and tracking, request status lifecycle (pending, in-progress, fulfilled, cancelled), admin dashboard, input validation, responsive UI, and API/workflow testing.

P1 enhancements (notifications, advanced location search, analytics, donation history) are deferred to after the MVP.

### Why this project

It addresses a meaningful social need while providing a manageable opportunity to build a complete web application. Core workflows are clear enough for an MVP, while technical requirements cover requirement analysis, reusable React interfaces, REST API development, authentication and authorization, relational database design, migrations, frontend/backend integration, testing, and documentation.

## Target Users

- **Donors:** People who want to register donor details, manage contact preferences, and update self-reported availability.
- **Blood requesters:** People coordinating a blood need who want to submit a request, search authorized donor listings, and follow request status.
- **Administrators:** Authorized staff who review donor records and requests, manage request statuses, and monitor the system dashboard.

Access to private information and actions depends on the user's role and, where relevant, ownership of the record.

## Project Objectives

1. Maintain donor profiles and blood requests in a centralized database.
2. Let donors manage their profile and contact availability.
3. Let authorized users search donor records by blood group, city, and availability.
4. Provide a clear lifecycle for submitting and tracking blood requests.
5. Enforce authentication, role permissions, and record ownership in the backend.
6. Validate user input and preserve data relationships.
7. Deliver a responsive interface for desktop and mobile screens.
8. Test the main API and user workflows and document how to run the project.
