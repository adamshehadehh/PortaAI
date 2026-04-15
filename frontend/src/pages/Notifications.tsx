import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { apiFetch } from "@/lib/api"
import { useEffect, useState } from "react"

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

export default function Notifications() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [markAllLoading, setMarkAllLoading] = useState(false)
  const [clearReadLoading, setClearReadLoading] = useState(false)

  useEffect(() => {
    async function fetchNotifications(showLoading = false) {
      try {
        if (showLoading) setLoading(true)
        setError(null)

        const response = await apiFetch("http://127.0.0.1:8000/api/notifications")

        if (!response.ok) {
          throw new Error("Failed to fetch notifications")
        }

        const data: NotificationsResponse = await response.json()

        setNotifications((prev) => {
          const prevJson = JSON.stringify(prev)
          const nextJson = JSON.stringify(data.notifications)
          return prevJson !== nextJson ? data.notifications : prev
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        if (showLoading) setLoading(false)
      }
    }

    fetchNotifications(true)

    const handleNotificationsUpdated = () => {
      fetchNotifications(false)
    }

    window.addEventListener("notifications-updated", handleNotificationsUpdated)

    const intervalId = window.setInterval(() => {
      fetchNotifications(false)
    }, 10000)

    return () => {
      window.removeEventListener("notifications-updated", handleNotificationsUpdated)
      window.clearInterval(intervalId)
    }
  }, [])

  async function markAsRead(id: number) {
    try {
      const response = await apiFetch(
        `http://127.0.0.1:8000/api/notifications/${id}/read`,
        {
          method: "POST",
        }
      )

      if (!response.ok) {
        throw new Error("Failed to mark notification as read")
      }

      setNotifications((prev) =>
        prev.map((notification) =>
          notification.id === id
            ? { ...notification, is_read: true }
            : notification
        )
      )

      window.dispatchEvent(new Event("notifications-updated"))
    } catch (err) {
      console.error(err)
    }
  }

  async function handleMarkAllAsRead() {
    try {
      setMarkAllLoading(true)

      const response = await apiFetch(
        "http://127.0.0.1:8000/api/notifications/read-all",
        {
          method: "POST",
        }
      )

      if (!response.ok) {
        throw new Error("Failed to mark all notifications as read")
      }

      setNotifications((prev) =>
        prev.map((notification) => ({ ...notification, is_read: true }))
      )

      window.dispatchEvent(new Event("notifications-updated"))
    } catch (err) {
      console.error(err)
    } finally {
      setMarkAllLoading(false)
    }
  }

  async function handleClearRead() {
    try {
      setClearReadLoading(true)

      const response = await apiFetch(
        "http://127.0.0.1:8000/api/notifications/clear-read",
        {
          method: "DELETE",
        }
      )

      if (!response.ok) {
        throw new Error("Failed to clear read notifications")
      }

      setNotifications((prev) =>
        prev.filter((notification) => !notification.is_read)
      )

      window.dispatchEvent(new Event("notifications-updated"))
    } catch (err) {
      console.error(err)
    } finally {
      setClearReadLoading(false)
    }
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length
  const readCount = notifications.filter((n) => n.is_read).length

  return (
    <div className="space-y-6">
      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Notifications
          </h1>
          <Badge variant="secondary" className="rounded-full">
            Alerts
          </Badge>
          <Badge className="rounded-full bg-cyan-600 hover:bg-cyan-700">
            {unreadCount} Unread
          </Badge>
        </div>

        <p className="text-slate-600">
          User-specific portfolio alerts and system activity.
        </p>

        <div className="flex flex-wrap gap-3">
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                variant="outline"
                className="rounded-xl"
                disabled={loading || unreadCount === 0 || markAllLoading}
              >
                {markAllLoading ? "Working..." : "Mark all as read"}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Mark all notifications as read?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will mark every unread notification as read.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleMarkAllAsRead}>
                  Confirm
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button
                variant="outline"
                className="rounded-xl border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
                disabled={loading || readCount === 0 || clearReadLoading}
              >
                {clearReadLoading ? "Working..." : "Clear read notifications"}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Clear all read notifications?</AlertDialogTitle>
                <AlertDialogDescription>
                  This will permanently remove all read notifications from the list.
                  Unread notifications will stay.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleClearRead}
                  className="bg-red-600 hover:bg-red-700"
                >
                  Clear read
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </header>

      {error && (
        <Card className="rounded-2xl border-red-200 shadow-sm">
          <CardContent className="pt-6">
            <p className="font-medium text-red-600">Error: {error}</p>
          </CardContent>
        </Card>
      )}

      <Card className="rounded-2xl border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Recent Notifications</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <p className="text-slate-600">Loading notifications...</p>
          ) : notifications.length === 0 ? (
            <p className="text-slate-600">No notifications yet.</p>
          ) : (
            notifications.map((notification) => (
              <div
                key={notification.id}
                className={`rounded-xl border p-4 ${
                  notification.is_read
                    ? "border-slate-200 bg-white"
                    : "border-cyan-200 bg-cyan-50"
                }`}
              >
                <div className="mb-2 flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      {notification.title}
                    </h3>
                    <p className="mt-1 text-sm text-slate-700">
                      {notification.message}
                    </p>
                    <p className="mt-2 text-xs text-slate-500">
                      {notification.created_at}
                    </p>
                  </div>

                  <div className="flex flex-col items-end gap-2">
                    <Badge
                      className={
                        notification.is_read
                          ? "rounded-full bg-slate-200 text-slate-700"
                          : "rounded-full bg-cyan-600 hover:bg-cyan-700"
                      }
                    >
                      {notification.is_read ? "Read" : "Unread"}
                    </Badge>

                    {!notification.is_read && (
                      <button
                        onClick={() => markAsRead(notification.id)}
                        className="text-sm font-medium text-cyan-700 hover:underline"
                      >
                        Mark as read
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}