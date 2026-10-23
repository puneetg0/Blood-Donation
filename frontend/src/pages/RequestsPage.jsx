/**
 * RequestsPage — view all blood requests and create a new one.
 * React rendering lifecycle: data is fetched on mount via useEffect.
 * The list re-renders automatically when a new request is added.
 */
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/AuthContext";
import { listRequests, createRequest, updateRequest, deleteRequest } from "../services/api";
import Navbar from "../components/Navbar";

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

// Map status values to readable labels and colors
const STATUS_STYLE = {
  pending:     { label: "Pending",     color: "#f59e0b" },
  in_progress: { label: "In Progress", color: "#3b82f6" },
  fulfilled:   { label: "Fulfilled",   color: "#10b981" },
  cancelled:   { label: "Cancelled",   color: "#9ca3af" },
};

export default function RequestsPage() {
  const { user } = useAuth();

  const [requests, setRequests]   = useState([]);
  const [loading, setLoading]     = useState(true);
  const [showForm, setShowForm]   = useState(false);
  const [filterStatus, setFilter] = useState("");
  const [formError, setFormError] = useState("");

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm();

  // Fetch requests whenever the status filter changes
  useEffect(() => {
    setLoading(true);
    const params = filterStatus ? { status: filterStatus } : {};
    listRequests(params)
      .then((res) => setRequests(res.data))
      .catch(() => setRequests([]))
      .finally(() => setLoading(false));
  }, [filterStatus]);

  // Create a new blood request
  async function onSubmit(data) {
    setFormError("");
    try {
      const res = await createRequest(data);
      // Add the new request to the top of the list without refetching
      setRequests((prev) => [res.data, ...prev]);
      reset();
      setShowForm(false);
    } catch (err) {
      setFormError(err.response?.data?.detail ?? "Could not create request.");
    }
  }

  // Cancel a request (owner only)
  async function handleCancel(id) {
    try {
      const res = await updateRequest(id, { status: "cancelled" });
      // Update just that one item in the list
      setRequests((prev) => prev.map((r) => (r.id === id ? res.data : r)));
    } catch {
      alert("Could not cancel request.");
    }
  }

  return (
    <>
      <Navbar />

      <main className="page-container">

        {/* ── Header row ── */}
        <div className="page-header">
          <h2>Blood Requests</h2>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "+ New Request"}
          </button>
        </div>

        {/* ── Create Request Form ── */}
        {showForm && (
          <section className="card">
            <h3>New Blood Request</h3>

            {formError && <div className="alert alert-error">{formError}</div>}

            <form onSubmit={handleSubmit(onSubmit)} className="inline-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Blood Group</label>
                  <select {...register("blood_group", { required: "Required" })}>
                    {BLOOD_GROUPS.map((bg) => <option key={bg}>{bg}</option>)}
                  </select>
                  {errors.blood_group && <span className="error-text">{errors.blood_group.message}</span>}
                </div>

                <div className="form-group">
                  <label>Units Required</label>
                  <input
                    type="number" min="1"
                    {...register("units_required", {
                      required: "Required",
                      min: { value: 1, message: "At least 1 unit." },
                      valueAsNumber: true,
                    })}
                  />
                  {errors.units_required && <span className="error-text">{errors.units_required.message}</span>}
                </div>

                <div className="form-group">
                  <label>Urgency</label>
                  <select {...register("urgency")}>
                    <option value="routine">Routine</option>
                    <option value="urgent">Urgent</option>
                    <option value="emergency">Emergency</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Hospital Name</label>
                  <input type="text" {...register("hospital_name", { required: "Required" })} />
                  {errors.hospital_name && <span className="error-text">{errors.hospital_name.message}</span>}
                </div>

                <div className="form-group">
                  <label>City</label>
                  <input type="text" {...register("city", { required: "Required" })} />
                  {errors.city && <span className="error-text">{errors.city.message}</span>}
                </div>
              </div>

              <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Submitting…" : "Submit Request"}
              </button>
            </form>
          </section>
        )}

        {/* ── Filter Bar ── */}
        <section className="card">
          <div className="filter-bar">
            <span>Filter by status:</span>
            {["", "pending", "in_progress", "fulfilled", "cancelled"].map((s) => (
              <button
                key={s}
                className={`filter-btn ${filterStatus === s ? "active" : ""}`}
                onClick={() => setFilter(s)}
              >
                {s === "" ? "All" : STATUS_STYLE[s]?.label}
              </button>
            ))}
          </div>
        </section>

        {/* ── Requests List ── */}
        <section className="card">
          {loading ? (
            <p className="empty-text">Loading…</p>
          ) : requests.length === 0 ? (
            <p className="empty-text">No requests found.</p>
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
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.map((r) => (
                    <tr key={r.id}>
                      <td><span className="badge">{r.blood_group}</span></td>
                      <td>{r.units_required}</td>
                      <td>{r.hospital_name}</td>
                      <td>{r.city}</td>
                      <td className={`urgency-${r.urgency}`}>{r.urgency}</td>
                      <td>
                        <span
                          className="status-pill"
                          style={{ background: STATUS_STYLE[r.status]?.color }}
                        >
                          {STATUS_STYLE[r.status]?.label}
                        </span>
                      </td>
                      <td>
                        {/* Only the owner can cancel their own pending request */}
                        {r.requester_id === user?.id && r.status === "pending" && (
                          <button
                            className="btn-text"
                            onClick={() => handleCancel(r.id)}
                          >
                            Cancel
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

      </main>
    </>
  );
}
