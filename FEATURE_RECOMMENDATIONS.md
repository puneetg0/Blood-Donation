# Blood Donation Manager — Feature Recommendations

**Goal:** Features that improve the BDM (Blood Donation Management) workflow  
**Priority:** P0 = Critical for workflow, P1 = High value, P2 = Nice to have

---

## P0 — Critical Workflow Features

### F1. Email Notifications for Request Status Changes
**Problem:** Requesters don't know when their request status changes unless they manually check the app.  
**Solution:** Send email when status changes (pending → in_progress → fulfilled/cancelled).  
**Backend:** Add email service (SMTP via `smtplib` or `fastapi-mail`), trigger in `request_service.update_request()` when status changes.  
**Frontend:** No changes needed; backend sends automatically.  
**Effort:** 4-6 hours  
**Workflow impact:** High — keeps requesters informed without manual checking.

### F2. Donor Availability Toggle on Dashboard
**Problem:** Donors must navigate to Donors page to update availability.  
**Solution:** Add a quick "Set Availability" toggle on the donor dashboard.  
**Backend:** PATCH /donors/me with availability_status. Already exists.  
**Frontend:** Add toggle switch on DashboardPage for donor role.  
**Effort:** 2-3 hours  
**Workflow impact:** High — encourages donors to keep availability current.

### F3. Request Expiry / Auto-Cancellation
**Problem:** Requests can stay "pending" forever if no one fulfills them.  
**Solution:** Auto-cancel requests past `required_by` date or after 7 days of inactivity.  
**Backend:** Add a scheduled task (APScheduler or cron) that marks expired requests as cancelled.  
**Frontend:** Show "Expired" badge on old pending requests.  
**Effort:** 4-6 hours  
**Workflow impact:** High — keeps request list clean and relevant.

### F4. Donor Response to Coordination (Accept/Decline)
**Problem:** Admins link donors to requests, but donors can't respond.  
**Solution:** Add a donor portal where linked donors can accept or decline a coordination request.  
**Backend:** New endpoint `POST /coordinations/{id}/respond` (donor role only), updates coordination_status to contacted/declined.  
**Frontend:** New page "My Coordinations" showing linked requests with Accept/Decline buttons.  
**Effort:** 6-8 hours  
**Workflow impact:** High — completes the coordination loop.

---

## P1 — High Value Features

### F5. Blood Bank / Hospital Integration Directory
**Problem:** Requesters manually enter hospital names; no standardized list.  
**Solution:** Pre-defined hospital/blood bank directory with addresses and contact info.  
**Backend:** New `Hospital` model (id, name, city, contact_phone, blood_types_stocked). Endpoint `GET /hospitals`.  
**Frontend:** Dropdown of hospitals in request form instead of free text.  
**Effort:** 5-7 hours  
**Workflow impact:** Medium — standardizes hospital data, enables future integrations.

### F6. Donation History Tracker
**Problem:** No record of past donations for donors.  
**Solution:** Let donors log past donations (date, hospital, units, blood group).  
**Backend:** New `Donation` model linked to Donor. CRUD endpoints.  
**Frontend:** New page "My Donation History" with form to add donations and list view.  
**Effort:** 5-7 hours  
**Workflow impact:** Medium — helps donors track their contribution, builds engagement.

### F7. Search by Distance / Location Radius
**Problem:** Search by city only; no proximity search.  
**Solution:** Add latitude/longitude to donors and requests; search within X km radius.  
**Backend:** Add `latitude`, `longitude` columns to Donor. Use PostGIS or Haversine formula in SQL.  
**Frontend:** Add radius selector (5km, 10km, 25km, 50km) to donor search.  
**Effort:** 8-10 hours  
**Workflow impact:** Medium — more precise donor discovery for urgent needs.

### F8. Analytics & Reports (Admin)
**Problem:** Admin dashboard shows only counts; no trends.  
**Solution:** Add charts for donations per month, requests by blood group, fulfillment rate.  
**Backend:** Aggregation endpoints (e.g., `GET /admin/reports/monthly`, `GET /admin/reports/blood-group`).  
**Frontend:** Charts using Recharts or Chart.js on new Admin Reports page.  
**Effort:** 6-8 hours  
**Workflow impact:** Medium — helps admins understand demand patterns.

---

## P2 — Nice to Have

### F9. SMS Notifications (Twilio)
**Problem:** Not all users check email regularly.  
**Solution:** SMS alerts for urgent requests and status changes.  
**Effort:** 4-6 hours (Twilio API integration)

### F10. Donor Eligibility Checklist
**Problem:** Donors don't know if they're eligible before registering.  
**Solution:** Simple questionnaire (age, weight, recent travel, medications) with guidance.  
**Effort:** 3-4 hours (frontend only, informational)

### F11. Password Reset / Forgot Password
**Problem:** No way to recover account if password is forgotten.  
**Solution:** Password reset flow with email token.  
**Effort:** 5-7 hours

### F12. Multi-language Support (i18n)
**Problem:** App is English-only.  
**Solution:** Add react-i18next for Hindi/regional language support.  
**Effort:** 8-10 hours

### F13. Dark Mode
**Problem:** Some users prefer dark interface.  
**Solution:** CSS dark mode toggle with localStorage persistence.  
**Effort:** 2-3 hours

### F14. Social Sharing of Requests
**Problem:** Requesters can't easily share urgent needs.  
**Solution:** Shareable link + WhatsApp/SMS share button for each request.  
**Effort:** 2-3 hours

---

## Recommended Implementation Order

| Phase | Features | Effort | Why First |
|-------|----------|--------|-----------|
| **Phase 1** | F1 (Email notifications), F2 (Donor availability toggle) | 6-9 hours | Immediate workflow value, low effort |
| **Phase 2** | F3 (Request expiry), F4 (Donor respond to coordination) | 10-14 hours | Completes the core coordination loop |
| **Phase 3** | F5 (Hospital directory), F6 (Donation history) | 10-14 hours | Enhances donor experience |
| **Phase 4** | F7 (Distance search), F8 (Analytics) | 14-18 hours | Advanced features for scale |
| **Phase 5** | F9-F14 (P2 features) | 25-35 hours | Polish and differentiation |

**Total estimated effort for P0+P1:** ~30-40 hours (about 1-2 weeks part-time)
