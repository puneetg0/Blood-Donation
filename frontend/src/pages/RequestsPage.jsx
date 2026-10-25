/** Request creation, editing, tracking, and administrator coordination. */
import { Fragment, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/AuthContext";
import {
  listRequests, createRequest, updateRequest, getApiErrorMessage, getRequestHistory,
  getCoordinations, createCoordination, updateCoordination,
} from "../services/api";
import Navbar from "../components/Navbar";

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

const STATUS_STYLE = {
  pending:     { label: "Pending",     color: "#f59e0b" },
  in_progress: { label: "In Progress", color: "#3b82f6" },
  fulfilled:   { label: "Fulfilled",   color: "#10b981" },
  cancelled:   { label: "Cancelled",   color: "#9ca3af" },
};

const COORD_STYLE = {
  contact_pending: { label: "Not Contacted", color: "#9ca3af" },
  contacted:       { label: "Contacted",     color: "#3b82f6" },
  declined:        { label: "Declined",      color: "#ef4444" },
  completed:       { label: "Completed",     color: "#10b981" },
};

function RequestForm({ request, error, onSave, onCancel }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      blood_group: request?.blood_group ?? BLOOD_GROUPS[0],
      units_required: request?.units_required ?? "",
      urgency: request?.urgency ?? "routine",
      hospital_name: request?.hospital_name ?? "",
      city: request?.city ?? "",
    },
  });

  return (
    <section className="card">
      <h3>{request ? "Edit Blood Request" : "New Blood Request"}</h3>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      <form onSubmit={handleSubmit(onSave)} className="inline-form" noValidate>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="request-blood-group">Blood Group</label>
            <select id="request-blood-group" {...register("blood_group", { required: "Choose a blood group." })}>
              {BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}
            </select>
            {errors.blood_group && <span className="error-text">{errors.blood_group.message}</span>}
          </div>
          <div className="form-group">
            <label htmlFor="request-units">Units Required</label>
            <input
              id="request-units"
              type="number"
              min="1"
              {...register("units_required", {
                required: "Enter the number of units.",
                min: { value: 1, message: "At least 1 unit." },
                valueAsNumber: true,
                validate: (value) => Number.isInteger(value) && value >= 1
                  || "Enter a whole number of at least 1 unit.",
              })}
            />
            {errors.units_required && <span className="error-text">{errors.units_required.message}</span>}
          </div>
          <div className="form-group">
            <label htmlFor="request-urgency">Urgency</label>
            <select id="request-urgency" {...register("urgency")}>
              <option value="routine">Routine</option>
              <option value="urgent">Urgent</option>
              <option value="emergency">Emergency</option>
            </select>
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="request-hospital">Hospital Name</label>
            <input
              id="request-hospital"
              type="text"
              maxLength="150"
              {...register("hospital_name", {
                required: "Hospital name is required.",
                validate: (value) => value.trim().length >= 2 || "Enter at least 2 characters.",
              })}
            />
            {errors.hospital_name && <span className="error-text">{errors.hospital_name.message}</span>}
          </div>
          <div className="form-group">
            <label htmlFor="request-city">City</label>
            <input
              id="request-city"
              type="text"
              maxLength="100"
              {...register("city", {
                required: "City is required.",
                validate: (value) => value.trim().length >= 2 || "Enter at least 2 characters.",
              })}
            />
            {errors.city && <span className="error-text">{errors.city.message}</span>}
          </div>
        </div>
        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Saving…" : request ? "Save changes" : "Submit request"}
          </button>
          <button className="btn btn-outline" type="button" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </button>
        </div>
      </form>
    </section>
  );
}

function RequestHistory({ requestId }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getRequestHistory(requestId)
      .then((response) => {
        if (active) setHistory(response.data);
      })
      .catch((requestError) => {
        if (active) setError(getApiErrorMessage(requestError, "Could not load request history."));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, [requestId]);

  if (loading) return <p className="empty-text">Loading status history…</p>;
  if (error) return <div className="alert alert-error" role="alert">{error}</div>;
  if (history.length === 0) return <p className="empty-text">No status changes have been recorded.</p>;

  return (
    <ol className="history-list">
      {history.map((entry) => (
        <li key={entry.id}>
          <span>
            {entry.previous_status?.replace("_", " ") ?? "Created"} → {entry.new_status.replace("_", " ")}
          </span>
          <time dateTime={entry.created_at}>{new Date(entry.created_at).toLocaleString()}</time>
          {entry.note && <p>{entry.note}</p>}
        </li>
      ))}
    </ol>
  );
}

// ── Small sub-component: the coordination manage panel ────────────────────
function ManagePanel({ request, user, onRequestUpdate }) {
  const [coordinations, setCoordinations] = useState([]);
  const [loading, setLoading]             = useState(true);
  const [donorId, setDonorId]             = useState("");
  const [linkError, setLinkError]         = useState("");
  const [busy, setBusy]                   = useState(false);

  // Load existing coordinations for this request
  useEffect(() => {
    getCoordinations(request.id)
      .then((res) => setCoordinations(res.data))
      .catch((error) => setLinkError(getApiErrorMessage(error, "Could not load coordination records.")))
      .finally(() => setLoading(false));
  }, [request.id]);

  // Linking a donor does not by itself mean coordination has started or a donation is confirmed.
  async function handleLinkDonor() {
    setLinkError("");
    const id = Number(donorId);
    if (!Number.isInteger(id) || id < 1) {
      setLinkError("Enter a valid donor ID.");
      return;
    }

    setBusy(true);
    try {
      const coordRes = await createCoordination({ request_id: request.id, donor_id: id });
      setCoordinations((prev) => [...prev, coordRes.data]);
      setDonorId("");

      if (user?.role === "admin" && request.status === "pending") {
        const reqRes = await updateRequest(request.id, { status: "in_progress" });
        onRequestUpdate(reqRes.data);
      }
    } catch (err) {
      setLinkError(getApiErrorMessage(err, "Could not link donor."));
    } finally {
      setBusy(false);
    }
  }

  async function handleCoordStatus(coordId, newStatus) {
    setLinkError("");
    setBusy(true);
    try {
      const res = await updateCoordination(coordId, { coordination_status: newStatus });
      setCoordinations((prev) => prev.map((c) => (c.id === coordId ? res.data : c)));
    } catch (error) {
      setLinkError(getApiErrorMessage(error, "Could not update coordination status."));
    } finally {
      setBusy(false);
    }
  }

  async function handleFulfill() {
    setLinkError("");
    setBusy(true);
    try {
      const res = await updateRequest(request.id, { status: "fulfilled" });
      onRequestUpdate(res.data);
    } catch (error) {
      setLinkError(getApiErrorMessage(error, "Could not update request."));
    } finally {
      setBusy(false);
    }
  }

  async function handleStartCoordination() {
    setLinkError("");
    setBusy(true);
    try {
      const res = await updateRequest(request.id, { status: "in_progress" });
      onRequestUpdate(res.data);
    } catch (error) {
      setLinkError(getApiErrorMessage(error, "Could not update request status."));
    } finally {
      setBusy(false);
    }
  }

  async function handleCancelRequest() {
    setLinkError("");
    setBusy(true);
    try {
      const res = await updateRequest(request.id, { status: "cancelled" });
      onRequestUpdate(res.data);
    } catch (error) {
      setLinkError(getApiErrorMessage(error, "Could not cancel request."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="manage-panel">
      <div className="manage-header">
        <div>
          <strong>{request.hospital_name}</strong> · {request.city} ·{" "}
          <span className="badge">{request.blood_group}</span> ·{" "}
          {request.units_required} unit(s)
        </div>
        <div className="manage-actions">
          {/* Mark fulfilled — only when in_progress */}
          {request.status === "in_progress" && (
            <button className="btn btn-success" onClick={handleFulfill} disabled={busy}>
              Mark fulfilled
            </button>
          )}
          {user?.role === "admin" && request.status === "pending" && (
            <button className="btn btn-outline" onClick={handleStartCoordination} disabled={busy}>
              Start coordination
            </button>
          )}
          {user?.role === "admin" && ["pending", "in_progress"].includes(request.status) && (
            <button className="btn-text danger" onClick={handleCancelRequest} disabled={busy}>
              Cancel request
            </button>
          )}
        </div>
      </div>

      {linkError && <div className="alert alert-error" role="alert">{linkError}</div>}

      {/* ── Link a donor ── */}
      {(request.status === "pending" || request.status === "in_progress") && (
        <div className="link-donor-row">
          <input
            type="number"
            placeholder="Enter Donor ID"
            value={donorId}
            onChange={(e) => setDonorId(e.target.value)}
            className="donor-id-input"
            min="1"
            aria-label="Donor ID"
          />
          <button className="btn btn-outline" onClick={handleLinkDonor} disabled={busy || !donorId}>
            {busy ? "Saving…" : "Link donor"}
          </button>
          <span className="hint-text">
            Enter an ID from the donor search results. Only consenting, available donors can be linked.
          </span>
        </div>
      )}

      {/* ── Coordination list ── */}
      <div className="coord-list">
        <p className="coord-title">
          Linked donors ({loading ? "…" : coordinations.length})
        </p>

        {!loading && coordinations.length === 0 && (
          <p className="empty-text">No donors linked yet. Use the form above to link one.</p>
        )}

        {coordinations.map((c) => (
          <div key={c.id} className="coord-row">
            <span className="coord-donor">Donor #{c.donor_id}</span>

            {/* Current status badge */}
            <span
              className="status-pill"
              style={{ background: COORD_STYLE[c.coordination_status]?.color }}
            >
              {COORD_STYLE[c.coordination_status]?.label}
            </span>

            {/* Action buttons — move status forward */}
            <div className="coord-btns">
              {c.coordination_status === "contact_pending" && (
                <button
                  className="btn-text"
                  onClick={() => handleCoordStatus(c.id, "contacted")}
                  disabled={busy}
                >
                  Mark Contacted
                </button>
              )}
              {c.coordination_status === "contacted" && (
                <>
                  <button
                    className="btn-text"
                    onClick={() => handleCoordStatus(c.id, "completed")}
                    disabled={busy}
                  >
                    ✅ Confirmed
                  </button>
                  <button
                    className="btn-text danger"
                    onClick={() => handleCoordStatus(c.id, "declined")}
                    disabled={busy}
                  >
                    ❌ Declined
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────
export default function RequestsPage() {
  const { user } = useAuth();

  const [requests, setRequests]       = useState([]);
  const [loading, setLoading]         = useState(true);
  const [showForm, setShowForm]       = useState(false);
  const [filterStatus, setFilter]     = useState("");
  const [formError, setFormError]     = useState("");
  const [loadError, setLoadError]     = useState("");
  const [searchTerm, setSearchTerm]   = useState("");
  const [filterBloodGroup, setFilterBloodGroup] = useState("");
  const [requestOffset, setRequestOffset] = useState(0);
  const [historyId, setHistoryId] = useState(null);
  const [managingId, setManagingId]   = useState(null); // which request is open
  const [editingRequest, setEditingRequest] = useState(null);

  useEffect(() => {
    setLoading(true);
    setLoadError("");
    let active = true;
    const timer = setTimeout(() => {
      const params = { offset: requestOffset, limit: 51 };
      if (filterStatus) params.status = filterStatus;
      if (filterBloodGroup) params.blood_group = filterBloodGroup;
      if (searchTerm.trim()) params.city = searchTerm.trim();
      listRequests(params)
        .then((res) => {
          if (active) setRequests(res.data);
        })
        .catch((error) => {
          if (active) {
            setRequests([]);
            setLoadError(getApiErrorMessage(error, "Could not load blood requests."));
          }
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    }, 250);

    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [filterStatus, filterBloodGroup, searchTerm, requestOffset]);

  async function onSubmit(data) {
    setFormError("");
    data.units_required = Number(data.units_required);
    try {
      if (editingRequest) {
        const res = await updateRequest(editingRequest.id, data);
        handleRequestUpdate(res.data);
      } else {
        const res = await createRequest(data);
        setRequests((prev) => [res.data, ...prev]);
      }
      setRequestOffset(0);
      setFilter("");
      setFilterBloodGroup("");
      setSearchTerm("");
      setShowForm(false);
      setEditingRequest(null);
    } catch (err) {
      setFormError(getApiErrorMessage(err, "Could not create request."));
    }
  }

  // Called by ManagePanel when it changes a request's status
  function handleRequestUpdate(updated) {
    setRequests((prev) => {
      const matchesFilter = !filterStatus || updated.status === filterStatus;
      if (!matchesFilter) return prev.filter((request) => request.id !== updated.id);
      return prev.map((request) => (request.id === updated.id ? updated : request));
    });
  }

  async function handleCancel(id) {
    setLoadError("");
    try {
      const res = await updateRequest(id, { status: "cancelled" });
      handleRequestUpdate(res.data);
      if (managingId === id) setManagingId(null);
    } catch (error) {
      setLoadError(getApiErrorMessage(error, "Could not cancel request."));
    }
  }

  return (
    <>
      <Navbar />
      <main className="page-container">

        {/* ── Header ── */}
        <div className="page-header">
          <h2>Blood Requests</h2>
          <button
            className="btn btn-primary"
            type="button"
            onClick={() => {
              setShowForm((visible) => !visible);
              setEditingRequest(null);
              setFormError("");
            }}
          >
            {showForm ? "Cancel" : "+ New Request"}
          </button>
        </div>

        {/* ── Create or edit form ── */}
        {showForm && (
          <RequestForm
            key={editingRequest?.id ?? "new"}
            request={editingRequest}
            error={formError}
            onSave={onSubmit}
            onCancel={() => {
              setShowForm(false);
              setEditingRequest(null);
              setFormError("");
            }}
          />
        )}

        {/* ── Filter bar ── */}
        <section className="card">
          <div className="filter-bar">
            <label htmlFor="request-status-filter">Status</label>
            <select
              id="request-status-filter"
              value={filterStatus}
              onChange={(event) => {
                setFilter(event.target.value);
                setRequestOffset(0);
                setManagingId(null);
              }}
            >
              <option value="">All visible statuses</option>
              {Object.entries(STATUS_STYLE).map(([value, option]) => (
                <option key={value} value={value}>{option.label}</option>
              ))}
            </select>
            <label htmlFor="request-blood-filter">Blood group</label>
            <select
              id="request-blood-filter"
              value={filterBloodGroup}
              onChange={(event) => {
                setFilterBloodGroup(event.target.value);
                setRequestOffset(0);
              }}
            >
              <option value="">All groups</option>
              {BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}
            </select>
            <label htmlFor="request-search">Location</label>
            <input
              id="request-search"
              type="search"
              value={searchTerm}
              onChange={(event) => {
                setSearchTerm(event.target.value);
                setRequestOffset(0);
              }}
              placeholder="Search by city"
            />
            {searchTerm || filterBloodGroup ? (
              <button
                className="btn-text"
                type="button"
                onClick={() => {
                  setSearchTerm("");
                  setFilterBloodGroup("");
                  setRequestOffset(0);
                }}
              >
                Clear filters
              </button>
            ) : null}
          </div>
        </section>

        {/* ── Requests list ── */}
        <section className="card">
          {loadError && <div className="alert alert-error" role="alert">{loadError}</div>}
          {loading ? (
            <p className="empty-text">Loading…</p>
          ) : requests.length === 0 ? (
            <p className="empty-text">
              {requestOffset > 0 ? "No more requests on this page." : "No requests match these filters."}
            </p>
          ) : (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Blood Group</th>
                    <th>Units</th>
                    <th>Hospital</th>
                    <th>City</th>
                    <th>Urgency</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.slice(0, 50).map((r) => (
                    <Fragment key={r.id}>
                      <tr key={r.id}>
                        <td><span className="badge">{r.blood_group}</span></td>
                        <td>{r.units_required}</td>
                        <td>{r.hospital_name}</td>
                        <td>{r.city}</td>
                        <td className={`urgency-${r.urgency}`}>{r.urgency}</td>
                        <td>
                          <span className="status-pill" style={{ background: STATUS_STYLE[r.status]?.color }}>
                            {STATUS_STYLE[r.status]?.label}
                          </span>
                        </td>
                        <td className="action-cell">
                          {/* Manage — open coordination panel */}
                          {(r.status === "pending" || r.status === "in_progress")
                            && user?.role === "admin" && (
                            <button
                              className="btn-text"
                              onClick={() => setManagingId(managingId === r.id ? null : r.id)}
                            >
                              {managingId === r.id ? "Close" : "Manage"}
                            </button>
                          )}
                          {(r.requester_id === user?.id || user?.role === "admin")
                            && ["pending", "in_progress"].includes(r.status) && (
                            <button
                              className="btn-text"
                              onClick={() => {
                                setEditingRequest(r);
                                setFormError("");
                                setShowForm(true);
                                setManagingId(null);
                              }}
                            >
                              Edit
                            </button>
                          )}
                          {/* Request owners can cancel open requests. */}
                          {r.requester_id === user?.id
                            && ["pending", "in_progress"].includes(r.status) && (
                            <button className="btn-text danger" onClick={() => handleCancel(r.id)}>
                              Cancel
                            </button>
                          )}
                          {(r.requester_id === user?.id || user?.role === "admin") && (
                            <button
                              className="btn-text"
                              onClick={() => setHistoryId(historyId === r.id ? null : r.id)}
                              aria-expanded={historyId === r.id}
                            >
                              {historyId === r.id ? "Hide history" : "History"}
                            </button>
                          )}
                        </td>
                      </tr>

                      {/* Inline manage panel — expands below the row */}
                      {managingId === r.id && (
                        <tr key={`manage-${r.id}`}>
                          <td colSpan="7" className="manage-cell">
                            <ManagePanel
                              request={r}
                              user={user}
                              onRequestUpdate={handleRequestUpdate}
                            />
                          </td>
                        </tr>
                      )}
                      {historyId === r.id && (
                        <tr key={`history-${r.id}`}>
                          <td colSpan="7" className="manage-cell">
                            <div className="history-panel">
                              <h3>Status history</h3>
                              <RequestHistory requestId={r.id} />
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {!loading && (
            <div className="pagination-controls" aria-label="Request list pages">
              <button
                className="btn btn-outline"
                type="button"
                onClick={() => setRequestOffset((offset) => Math.max(0, offset - 50))}
                disabled={loading || requestOffset === 0}
              >
                Previous
              </button>
              <span>Page {Math.floor(requestOffset / 50) + 1}</span>
              <button
                className="btn btn-outline"
                type="button"
                onClick={() => setRequestOffset((offset) => offset + 50)}
                disabled={loading || requests.length <= 50}
              >
                Next
              </button>
            </div>
          )}
        </section>

      </main>
    </>
  );
}
