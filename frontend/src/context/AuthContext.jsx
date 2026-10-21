/**
 * AuthContext — provides { user, token, login, logout } to the entire app.
 *
 * On mount, the context restores any token found in localStorage and
 * verifies it by calling /api/auth/me. If the token is expired or invalid
 * it is removed automatically.
 */
import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { loginUser as apiLogin, registerUser as apiRegister, getMe } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]   = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [loading, setLoading] = useState(true);

  // Restore session on page reload
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem("access_token");
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const saveToken = (t) => {
    localStorage.setItem("access_token", t);
    setToken(t);
  };

  /** Log in with email + password. Returns the response data. */
  const login = useCallback(async (credentials) => {
    const res = await apiLogin(credentials);
    saveToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  }, []);

  /** Register a new account. Returns the response data. */
  const register = useCallback(async (payload) => {
    const res = await apiRegister(payload);
    saveToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  }, []);

  /** Clear session. */
  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

/** Convenience hook — throws if used outside AuthProvider. */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
