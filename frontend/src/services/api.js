/**
 * Axios instance pre-configured for the Blood Donation Manager API.
 * The token is attached automatically via a request interceptor.
 */
import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

// Attach stored JWT on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Auth endpoints ─────────────────────────────────────────────────────────

/** POST /api/auth/register */
export const registerUser = (data) => api.post("/auth/register", data);

/** POST /api/auth/login */
export const loginUser = (data) => api.post("/auth/login", data);

/** GET /api/auth/me */
export const getMe = () => api.get("/auth/me");

export default api;
