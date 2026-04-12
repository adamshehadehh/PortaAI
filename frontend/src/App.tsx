import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import AppShell from "@/components/layout/AppShell"
import Dashboard from "@/pages/Dashboard"
import Explainability from "@/pages/Explainability"
import Login from "@/pages/Login"
import Positions from "@/pages/Positions"
import Predictions from "@/pages/Predictions"
import Settings from "@/pages/Settings"
import Trades from "@/pages/Trades"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />

        <Route path="/app" element={<AppShell />}>
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="positions" element={<Positions />} />
          <Route path="predictions" element={<Predictions />} />
          <Route path="trades" element={<Trades />} />
          <Route path="explainability" element={<Explainability />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}