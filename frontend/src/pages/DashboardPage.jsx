import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ROLE_LABEL = { donor: "Donor", requester: "Blood Requester", admin: "Administrator" };

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <>
      <nav className="navbar">
        <span className="brand">🩸 Blood Donation Manager</span>
        <div className="nav-links">
          <span>
            {user?.full_name} · {ROLE_LABEL[user?.role] ?? user?.role}
          </span>
          <button onClick={handleLogout}>Sign out</button>
        </div>
      </nav>

      <main className="dashboard">
        <h2>Dashboard</h2>

        <div className="stat-grid">
          <div className="stat-card">
            <div className="value">—</div>
            <div className="label">Registered donors</div>
          </div>
          <div className="stat-card">
            <div className="value">—</div>
            <div className="label">Open requests</div>
          </div>
          <div className="stat-card">
            <div className="value">—</div>
            <div className="label">Fulfilled requests</div>
          </div>
        </div>

        <p style={{ marginTop: "2rem", color: "#666" }}>
          More features coming soon. You are logged in as{" "}
          <strong>{user?.email}</strong>.
        </p>
      </main>
    </>
  );
}
