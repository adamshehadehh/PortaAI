import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import AppShell from "@/components/layout/AppShell"
import ProtectedRoute from "@/components/layout/ProtectedRoute"
import Dashboard from "@/pages/Dashboard"
import Explainability from "@/pages/Explainability"
import Login from "@/pages/Login"
import Positions from "@/pages/Positions"
import Predictions from "@/pages/Predictions"
import Settings from "@/pages/Settings"
import Trades from "@/pages/Trades"
import Notifications from "@/pages/Notifications"
import Register from "@/pages/Register"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="positions" element={<Positions />} />
          <Route path="predictions" element={<Predictions />} />
          <Route path="trades" element={<Trades />} />
          <Route path="explainability" element={<Explainability />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}