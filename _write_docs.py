import os

base = "docs"

files = {}

files["proposal.md"] = """# Blood Donation Manager — Proposal

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
"""
files["user-stories.md"] = """# Blood Donation Manager — User Stories

## User Personas

### Donors
People who want to register their donor details, manage their contact preferences, and update their self-reported availability.

### Blood Requesters
People coordinating a blood need who want to submit a request, search authorized donor listings, and follow the request's status. A requester account associates each request with its owner.

### Administrators
Authorized staff who review donor records and requests, manage request statuses, and monitor the system dashboard.

Access to private information and actions will depend on the user's role and, where relevant, ownership of the record.

## MVP Features and Priorities

| Priority | Feature | MVP behavior |
|---|---|---|
| P0 | Authentication | Register, log in, log out, and protect private pages and API routes. |
| P0 | Role-based access | Support donor, requester, and administrator permissions. |
| P0 | Donor registration | Save a donor's name, blood group, city, contact details, and contact consent. |
| P0 | Donor profile and availability | Let donors view and update their profile and self-reported availability. |
| P0 | Donor search | Filter authorized donor records by blood group, city, and availability. |
| P0 | Blood requests | Create, view, update permitted fields, and cancel requests according to permissions. |
| P0 | Request status tracking | Track pending, in-progress, fulfilled, and cancelled states. |
| P0 | Admin dashboard | Show summary counts for donors and requests. |
| P0 | Validation and responsive UI | Validate required inputs and provide usable mobile and desktop layouts. |
| P0 | API and workflow tests | Test valid, invalid, and unauthorized operations and key user journeys. |
| P1 | Notifications | Notify users about new requests and status changes. |
| P1 | Advanced location search | Search by distance or more precise geographic location. |
| P1 | Analytics and reports | Report on donor registrations and request outcomes. |
| P1 | Donation history | Record verified past donation events. |

## User Stories and Acceptance Criteria

| ID | User story | Acceptance criteria |
|---|---|---|
| US-01 | As a donor, I want to register my profile so that my donor information can be maintained. | Valid details are saved; invalid fields and duplicate account identifiers are rejected with clear messages. |
| US-02 | As a donor, I want to update my availability so that my profile reflects whether I am willing to be contacted. | My updated availability is saved and reflected in authorized search results. |
| US-03 | As a requester, I want to search by blood group and location so that I can find relevant donor records. | Results match the selected filters and do not reveal fields the requester is not authorized to see. |
| US-04 | As a requester, I want to create a blood request so that the need is recorded in one place. | A request with valid blood group, location, units, urgency, and required details is saved with an initial status. |
| US-05 | As a requester, I want to track my request so that I know its current status. | The requester can view their request and its current status; unrelated users cannot access private request details. |
| US-06 | As an administrator, I want to review blood requests so that they can be coordinated consistently. | Only an authorized administrator can perform administrative actions, and valid changes are saved. |
| US-07 | As an administrator, I want to manage donor records so that inaccurate records can be addressed. | Donor record changes are restricted to authorized administrators and relevant changes are traceable. |
| US-08 | As a user, I want to use the application on a mobile device so that I can access its essential features on different screen sizes. | Forms, navigation, and record lists remain usable on supported mobile and desktop layouts. |
| US-09 | As a user, I want clear validation messages so that I can correct mistakes when submitting information. | Invalid input is rejected with a message that identifies what needs correction. |
| US-10 | As an administrator, I want to view summary statistics so that I can monitor registrations and requests. | Dashboard totals are derived from stored records and follow documented status definitions. |

### Definition of Done

A story is complete when its behavior, validation, authorization, relevant tests, and documentation are in place.
"""
files["problem-statement.md"] = """# Blood Donation Manager — Problem Statement

## Core Problems

Blood donation coordination can involve urgent requests and information spread across phone contacts, spreadsheets, messaging groups, and social media. These channels make it difficult to find current information or know what has happened to a request.

### Problem areas

- **Scattered donor information:** Records in multiple places are hard to search and keep current.
- **Time-consuming discovery:** Finding potential donors by blood group and location can require manually checking many records.
- **Unclear availability:** A donor's current willingness to be contacted may not be known.
- **Untracked requests:** A requester may not know whether a request is new, being coordinated, fulfilled, or cancelled.
- **Limited oversight:** Administrators may lack a consistent view of donor records and open requests.
- **Privacy risks:** Contact details should not be exposed to people who do not need them.

## Proposed Solution

**Blood Donation Manager** is a responsive web application that centralizes donor registration, self-reported availability, authorized donor search, blood request submission, and request status tracking. The application provides structured records and controlled access to personal information so users can coordinate more efficiently, while leaving medical eligibility and compatibility decisions to qualified professionals.

## Scope Note

The application supports coordination only. It does not provide medical advice, determine donor eligibility or blood compatibility, or guarantee that a donor can fulfill a request. Donor availability is self-reported and is not a clinical assessment.
"""