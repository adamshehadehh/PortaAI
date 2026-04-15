import { Badge } from "@/components/ui/badge"
import { apiFetch } from "@/lib/api"
import { removeToken } from "@/lib/auth"
import { Bell } from "lucide-react"
import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

type NotificationItem = {
  id: number
  title: string
  message: string
  is_read: boolean
  created_at: string
}

type NotificationsResponse = {
  notifications: NotificationItem[]
}

export default function Topbar() {
  const navigate = useNavigate()
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    async function fetchNotifications() {
      try {
        const response = await apiFetch("http://127.0.0.1:8000/api/notifications")

        if (!response.ok) {
          return
        }

        const data: NotificationsResponse = await response.json()
        const unread = data.notifications.filter((n) => !n.is_read).length
        setUnreadCount(unread)
      } catch {
        // ignore topbar notification fetch errors for now
      }
    }

    fetchNotifications()
    // listen for updates
    window.addEventListener("notifications-updated", fetchNotifications)
    const intervalId = window.setInterval(() => {
      fetchNotifications()
    }, 10000)
    return () => {
      window.removeEventListener("notifications-updated", fetchNotifications)
      window.clearInterval(intervalId)
    }
  }, [])

  function handleLogout() {
    removeToken()
    navigate("/login")
  }

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">PortaAI Dashboard</h2>
        <p className="text-sm text-slate-500">
          Intelligent portfolio management with forecasting and sentiment.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <Badge className="rounded-full bg-cyan-600 hover:bg-cyan-600">
          Live Demo Mode
        </Badge>

        <button
          onClick={() => navigate("/app/notifications")}
          className="relative rounded-xl border border-slate-200 p-2 text-slate-700 transition hover:bg-slate-50"
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-xs font-semibold text-white">
              {unreadCount}
            </span>
          )}
        </button>

        <button
          onClick={handleLogout}
          className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
        >
          Logout
        </button>

        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-700">
          A
        </div>
      </div>
    </header>
  )
}