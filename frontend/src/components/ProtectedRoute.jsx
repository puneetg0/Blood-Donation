import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Wraps a route and redirects to /login if the user is not authenticated.
 * Shows nothing while the session is being restored from localStorage.
 */
export default function ProtectedRoute({ children }) {
  const { user, token, loading, sessionError, retrySession } = useAuth();

  if (loading) {
    return <main className="auth-page" aria-live="polite">Verifying your session…</main>;
  }

  if (user) return children;
  if (!token) return <Navigate to="/login" replace />;

  return (
    <main className="auth-page">
      <section className="auth-card" role="alert">
        <h1>Session unavailable</h1>
        <p className="subtitle">
          {sessionError || "Your session could not be verified. Check your connection and try again."}
        </p>
        <button className="btn btn-primary" type="button" onClick={retrySession}>
          Retry
        </button>
        <p className="mt-sm"><Link className="link-text" to="/login">Sign in again</Link></p>
      </section>
    </main>
  );
}
