import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"
import Topbar from "./Topbar"

export default function AppShell() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar />

      {/* Main content shifted right */}
      <div className="ml-72 flex min-h-screen flex-col">
        <Topbar />

        <main className="flex-1 p-6">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}