# Blood Donation Manager

## Project Overview

Blood Donation Manager is a web application designed to organize blood donor information and manage blood donation requests in a centralized system. The project aims to simplify donor search, maintain donor availability records, and track blood requests efficiently.

The application will be developed as a full-stack project using React for the frontend, FastAPI for the backend, and PostgreSQL for database management.

## Problem Statement

Blood donor information and blood requests are often shared through phone calls, messaging applications, and manually maintained records. This can make it difficult to find potential donors, verify their reported availability, and track the progress of blood requests.

Blood Donation Manager aims to address these challenges by providing a structured platform for donor registration, donor search, and blood request management.

## Project Objectives

- Maintain donor profiles and blood group information.
- Search potential donors by blood group and city.
- Record and manage blood donation requests.
- Track request statuses.
- Implement authentication and role-based access.
- Provide a responsive and user-friendly interface.
- Maintain accurate and organized records.

## Planned Features

### Donor Management
- Register donor information.
- Store blood group and location details.
- Update donor profiles and reported availability.

### Blood Request Management
- Create blood requests.
- Record hospital, location, blood group, and required units.
- Track request status.
- View and manage existing requests.

### Donor Search
- Search donors by blood group.
- Filter donors by city and reported availability.
- Display relevant donor information according to access permissions.

### Dashboard
- Display donor registration counts.
- Show pending and fulfilled blood requests.
- Provide a summary of request statuses.

### Authentication and Security
- User registration and login.
- Role-based access control.
- Input validation and protected API endpoints.
- Protection of donor contact information.

## Technology Stack

**Frontend**
- React
- JavaScript
- Tailwind CSS

**Backend**
- Python
- FastAPI
- Pydantic
- SQLAlchemy

**Database**
- PostgreSQL

**Tools**
- Git
- GitHub
- Visual Studio Code
- Postman or FastAPI Swagger UI

## Initial Data Model

The initial Python data model includes two main classes:

- `Donor`: Stores donor ID, name, blood group, city, phone number, and reported availability.
- `BloodRequest`: Stores request ID, patient name, blood group, required units, hospital name, city, and request status.

These classes will serve as the initial foundation for implementing database models and API endpoints.

## Planned Folder Structure

```text
blood-donation-manager/
├── frontend/
├── backend/
├── docs/
├── .env.example
├── .gitignore
└── README.md
```

The frontend and backend directories will contain their respective application code. The documentation directory will contain project requirements, database design, application flow, and development plans.

## Development Plan

| Day | Planned Work |
|---|---|
| Day 1 | Research, requirements, data model, and project setup |
| Day 2 | Backend setup and database configuration |
| Day 3 | Authentication and donor management |
| Day 4 | Blood request APIs and donor search |
| Day 5 | React frontend development |
| Day 6 | Frontend-backend integration and testing |
| Day 7 | Bug fixing, documentation, and deployment preparation |

## Project Status

**Current Stage:** Initial Planning and Data Modeling

The project is currently in the planning stage. Requirements, core features, initial data models, and the development roadmap are being defined before full implementation begins.

## Future Improvements

- Email or SMS notifications.
- Advanced location-based donor search.
- Donation history management.
- Improved reporting and analytics.
- Deployment to a production environment.

## Important Note

This application is intended to support donor information management and blood donation coordination. It does not replace professional medical advice, blood compatibility testing, or medical eligibility assessments. Donor availability is self-reported and does not guarantee eligibility to donate.

## Author

Puneet Goswami
