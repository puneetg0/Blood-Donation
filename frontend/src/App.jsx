import { Routes, Route, Navigate } from "react-router-dom";
import LoginPage      from "./pages/LoginPage";
import RegisterPage   from "./pages/RegisterPage";
import DashboardPage  from "./pages/DashboardPage";
import DonorsPage     from "./pages/DonorsPage";
import RequestsPage   from "./pages/RequestsPage";
import MyCoordinations from "./pages/MyCoordinationsPage";
import ProtectedRoute from "./components/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login"    element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected — user must be logged in */}
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/donors"    element={<ProtectedRoute><DonorsPage /></ProtectedRoute>} />
      <Route path="/requests"  element={<ProtectedRoute><RequestsPage /></ProtectedRoute>} />
      <Route path="/my-coordinations" element={<ProtectedRoute><MyCoordinations /></ProtectedRoute>} />

      {/* Default */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
