# Blood Donation Manager — User Stories

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
