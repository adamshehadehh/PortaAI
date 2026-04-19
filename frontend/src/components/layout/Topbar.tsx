import { Badge } from "@/components/ui/badge"
import { apiFetch } from "@/lib/api"
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

type CurrentUserResponse = {
  id: number
  email: string
}

export default function Topbar() {
  const navigate = useNavigate()
  const [unreadCount, setUnreadCount] = useState(0)
  const [userEmail, setUserEmail] = useState<string | null>(null)

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
    window.addEventListener("notifications-updated", fetchNotifications)

    const intervalId = window.setInterval(() => {
      fetchNotifications()
    }, 10000)

    return () => {
      window.removeEventListener("notifications-updated", fetchNotifications)
      window.clearInterval(intervalId)
    }
  }, [])

  useEffect(() => {
    async function fetchCurrentUser() {
      try {
        const response = await apiFetch("http://127.0.0.1:8000/api/users/me")

        if (!response.ok) {
          return
        }

        const data: CurrentUserResponse = await response.json()
        setUserEmail(data.email)
      } catch {
        // ignore small topbar user fetch errors
      }
    }

    fetchCurrentUser()
  }, [])

  const userInitial = userEmail
    ? (() => {
        const match = userEmail.match(/[a-zA-Z]/)
        return match ? match[0].toUpperCase() : "?"
      })()
    : "?"

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4 shadow-sm">
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
              {unreadCount >= 20 ? "20+" : unreadCount}
            </span>
          )}
        </button>

        <div
          title={userEmail ?? ""}
          className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-cyan-600 to-blue-600 text-sm font-semibold text-white"
        >
          {userInitial}
        </div>
      </div>
    </header>
  )
}