import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Wraps a route and redirects to /login if the user is not authenticated.
 * Shows nothing while the session is being restored from localStorage.
 */
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return null; // or a spinner

  return user ? children : <Navigate to="/login" replace />;
}
