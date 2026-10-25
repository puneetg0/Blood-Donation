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
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Auth ──────────────────────────────────────────────────────────────────
export const registerUser = (data) => api.post("/auth/register", data);
export const loginUser    = (data) => api.post("/auth/login", data);
export const getMe        = ()     => api.get("/auth/me");

// ── Donors ────────────────────────────────────────────────────────────────
export const createDonor      = (data)     => api.post("/donors/", data);
export const getMyDonorProfile= ()         => api.get("/donors/me");
export const listDonors       = (params)   => api.get("/donors/", { params });
export const updateDonor      = (id, data) => api.patch(`/donors/${id}`, data);

// ── Blood Requests ────────────────────────────────────────────────────────
export const createRequest    = (data)     => api.post("/requests/", data);
export const listRequests     = (params)   => api.get("/requests/", { params });
export const listMyRequests   = ()         => api.get("/requests/me");
export const getRequestHistory= (id)       => api.get(`/requests/${id}/history`);
export const updateRequest    = (id, data) => api.patch(`/requests/${id}`, data);
export const deleteRequest    = (id)       => api.delete(`/requests/${id}`);

// ── Coordinations ─────────────────────────────────────────────────────────
export const createCoordination  = (data)     => api.post("/coordinations/", data);
export const getCoordinations    = (requestId)=> api.get(`/coordinations/request/${requestId}`);
export const updateCoordination  = (id, data) => api.patch(`/coordinations/${id}`, data);

// ── Administration ────────────────────────────────────────────────────────
export const getAdminDashboard = () => api.get("/admin/dashboard");
export const getDashboardSummary = () => api.get("/dashboard/summary");

export function getApiErrorMessage(error, fallback) {
  const detail = error.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => {
      const field = Array.isArray(item.loc) ? item.loc.at(-1) : null;
      return field ? `${field}: ${item.msg}` : item.msg;
    }).join(" ");
  }
  if (!error.response) return "Unable to reach the server. Check your connection and try again.";
  return fallback;
}

export default api;
