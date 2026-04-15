import { NavLink } from "react-router-dom"
import {
  BarChart3,
  Bell,
  Briefcase,
  BrainCircuit,
  House,
  Settings,
  TrendingUp,
} from "lucide-react"

const navItems = [
  { to: "/app/dashboard", label: "Home", icon: House },
  { to: "/app/positions", label: "Positions", icon: Briefcase },
  { to: "/app/predictions", label: "Predictions", icon: TrendingUp },
  { to: "/app/trades", label: "Trades", icon: BarChart3 },
  { to: "/app/explainability", label: "Explainability", icon: BrainCircuit },
  { to: "/app/notifications", label: "Notifications", icon: Bell },
  { to: "/app/settings", label: "Settings", icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-72 flex-col border-r border-slate-800 bg-[#0f172a] text-white">      <div className="border-b border-slate-800 px-6 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-cyan-500/15 text-cyan-300">
            <BrainCircuit className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">PortaAI</h1>
            <p className="text-sm text-slate-400">AI Portfolio Manager</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-4 py-6">
        {navItems.map((item) => {
          const Icon = item.icon

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  "flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition",
                  isActive
                    ? "bg-cyan-500/15 text-cyan-300"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white",
                ].join(" ")
              }
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      <div className="border-t border-slate-800 px-6 py-4">
        <p className="text-xs text-slate-400">
          Forecasting, sentiment, allocation, and explainability.
        </p>
      </div>
    </aside>
  )
}