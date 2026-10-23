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
export const updateRequest    = (id, data) => api.patch(`/requests/${id}`, data);
export const deleteRequest    = (id)       => api.delete(`/requests/${id}`);

export default api;
