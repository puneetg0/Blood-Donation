/**
 * DashboardPage — shows live counts fetched from the API.
 * Counts are derived from the actual stored records.
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  getApiErrorMessage,
  getDashboardSummary,
} from "../services/api";
import Navbar from "../components/Navbar";

const ROLE_LABEL = { donor: "Donor", requester: "Blood Requester", admin: "Administrator" };

export default function DashboardPage() {
  const { user } = useAuth();

  // Stats loaded from the API
  const [stats, setStats] = useState({ donors: 0, pending: 0, fulfilled: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setError("");
    getDashboardSummary().then(({ data }) => {
      setStats({
        donors: data.total_donors,
        pending: user?.role === "donor" ? data.total_requests : data.pending_requests,
        fulfilled: data.fulfilled_requests,
      });
    }).catch((requestError) => {
      setError(getApiErrorMessage(requestError, "Could not load dashboard information."));
    }).finally(() => setLoading(false));
  }, [user?.role]);

  return (
    <>
      <Navbar />

      <main className="page-container">
        <h2>Welcome, {user?.full_name}</h2>
        <p className="page-subtitle">Role: {ROLE_LABEL[user?.role] ?? user?.role}</p>

        {error && <div className="alert alert-error" role="alert">{error}</div>}

        {/* Live stat cards */}
        <div className="stat-grid">
          <div className="stat-card">
            <div className="value">{loading ? "…" : stats.donors}</div>
            <div className="label">{user?.role === "admin" ? "Registered Donors" : "Available Donors"}</div>
          </div>
          <div className="stat-card">
            <div className="value">{loading ? "…" : stats.pending}</div>
            <div className="label">{user?.role === "requester" ? "My Pending Requests" : "Open Requests"}</div>
          </div>
          {user?.role !== "donor" && (
            <div className="stat-card">
              <div className="value">{loading ? "…" : stats.fulfilled}</div>
              <div className="label">{user?.role === "requester" ? "My Fulfilled Requests" : "Fulfilled Requests"}</div>
            </div>
          )}
        </div>

        {/* Quick links */}
        <div className="quick-links">
          <h3>Quick actions</h3>
          <div className="quick-grid">
            <Link to="/donors" className="quick-card">
              <span className="quick-icon">🔍</span>
              <span>Search Donors</span>
            </Link>
            <Link to="/requests" className="quick-card">
              <span className="quick-icon">📋</span>
              <span>View Requests</span>
            </Link>
            {user?.role === "donor" && (
              <Link to="/donors" className="quick-card">
                <span className="quick-icon">👤</span>
                <span>My Donor Profile</span>
              </Link>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
