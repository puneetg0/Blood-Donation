import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="navbar">
      <span className="brand">🩸 Blood Donation Manager</span>

      <div className="nav-links">
        <NavLink to="/dashboard" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          Dashboard
        </NavLink>
        <NavLink to="/donors" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          Donors
        </NavLink>
        <NavLink to="/requests" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          Requests
        </NavLink>
        <span className="nav-user">{user?.full_name}</span>
        <button onClick={handleLogout} className="btn-logout">Sign out</button>
      </div>
    </nav>
  );
}
