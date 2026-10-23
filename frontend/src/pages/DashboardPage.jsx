/**
 * DashboardPage — shows live counts fetched from the API.
 * Counts are derived from the actual stored records.
 */
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { listDonors, listRequests } from "../services/api";
import Navbar from "../components/Navbar";

const ROLE_LABEL = { donor: "Donor", requester: "Blood Requester", admin: "Administrator" };

export default function DashboardPage() {
  const { user } = useAuth();

  // Stats loaded from the API
  const [stats, setStats] = useState({ donors: 0, pending: 0, fulfilled: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch donors and requests in parallel
    Promise.all([
      listDonors(),
      listRequests({ status: "pending" }),
      listRequests({ status: "fulfilled" }),
    ])
      .then(([donorsRes, pendingRes, fulfilledRes]) => {
        setStats({
          donors:    donorsRes.data.length,
          pending:   pendingRes.data.length,
          fulfilled: fulfilledRes.data.length,
        });
      })
      .catch(() => {}) // keep zeros if fetch fails
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <Navbar />

      <main className="dashboard">
        <h2>Welcome, {user?.full_name}</h2>
        <p className="page-subtitle">Role: {ROLE_LABEL[user?.role] ?? user?.role}</p>

        {/* Live stat cards */}
        <div className="stat-grid">
          <div className="stat-card">
            <div className="value">{loading ? "…" : stats.donors}</div>
            <div className="label">Registered Donors</div>
          </div>
          <div className="stat-card">
            <div className="value">{loading ? "…" : stats.pending}</div>
            <div className="label">Open Requests</div>
          </div>
          <div className="stat-card">
            <div className="value">{loading ? "…" : stats.fulfilled}</div>
            <div className="label">Fulfilled Requests</div>
          </div>
        </div>

        {/* Quick links */}
        <div className="quick-links">
          <h3>Quick actions</h3>
          <div className="quick-grid">
            <a href="/donors" className="quick-card">
              <span className="quick-icon">🔍</span>
              <span>Search Donors</span>
            </a>
            <a href="/requests" className="quick-card">
              <span className="quick-icon">📋</span>
              <span>View Requests</span>
            </a>
            {user?.role === "donor" && (
              <a href="/donors/profile" className="quick-card">
                <span className="quick-icon">👤</span>
                <span>My Donor Profile</span>
              </a>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
