import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { apiFetch } from "@/lib/api"
import { useEffect, useState } from "react"

type SettingsResponse = {
  in_app_notifications_enabled: boolean
  email_notifications_enabled: boolean
  trade_notifications_enabled: boolean
  rebalance_notifications_enabled: boolean
  rebalance_frequency: string
}

export default function Settings() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchSettings() {
      try {
        setLoading(true)
        setError(null)

        const response = await apiFetch("http://127.0.0.1:8000/api/settings")

        if (!response.ok) {
          throw new Error("Failed to fetch settings")
        }

        const data: SettingsResponse = await response.json()
        setSettings(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        setLoading(false)
      }
    }

    fetchSettings()
  }, [])

  async function handleSave() {
    if (!settings) return

    try {
      setSaving(true)
      setMessage(null)
      setError(null)

      const response = await apiFetch("http://127.0.0.1:8000/api/settings", {
        method: "PUT",
        body: JSON.stringify(settings),
      })

      if (!response.ok) {
        throw new Error("Failed to save settings")
      }

      const data = await response.json()
      setMessage(data.message || "Settings updated successfully")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
    } finally {
      setSaving(false)
    }
  }

  function updateField<K extends keyof SettingsResponse>(key: K, value: SettingsResponse[K]) {
    if (!settings) return
    setSettings({ ...settings, [key]: value })
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Settings
          </h1>
          <Badge variant="secondary" className="rounded-full">
            Preferences
          </Badge>
        </div>
        <p className="text-slate-600">
          Manage notification behavior and portfolio rebalance preferences.
        </p>
      </header>

      {error && (
        <Card className="rounded-2xl border-red-200 shadow-sm">
          <CardContent className="pt-6">
            <p className="font-medium text-red-600">Error: {error}</p>
          </CardContent>
        </Card>
      )}

      {message && (
        <Card className="rounded-2xl border-emerald-200 shadow-sm">
          <CardContent className="pt-6">
            <p className="font-medium text-emerald-600">{message}</p>
          </CardContent>
        </Card>
      )}

      {loading || !settings ? (
        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardContent className="pt-6">
            <p className="text-slate-600">Loading settings...</p>
          </CardContent>
        </Card>
      ) : (
        <>
          <Card className="rounded-2xl border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <label className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-slate-900">In-app notifications</p>
                  <p className="text-sm text-slate-500">Show notifications inside PortaAI.</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.in_app_notifications_enabled}
                  onChange={(e) =>
                    updateField("in_app_notifications_enabled", e.target.checked)
                  }
                  className="h-5 w-5"
                />
              </label>

              <label className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-slate-900">Email notifications</p>
                  <p className="text-sm text-slate-500">Receive alerts by email later when enabled.</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.email_notifications_enabled}
                  onChange={(e) =>
                    updateField("email_notifications_enabled", e.target.checked)
                  }
                  className="h-5 w-5"
                />
              </label>

              <label className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-slate-900">Trade notifications</p>
                  <p className="text-sm text-slate-500">Notify when BUY or SELL trades are executed.</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.trade_notifications_enabled}
                  onChange={(e) =>
                    updateField("trade_notifications_enabled", e.target.checked)
                  }
                  className="h-5 w-5"
                />
              </label>

              <label className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-medium text-slate-900">Rebalance notifications</p>
                  <p className="text-sm text-slate-500">Notify when a rebalance cycle completes.</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.rebalance_notifications_enabled}
                  onChange={(e) =>
                    updateField("rebalance_notifications_enabled", e.target.checked)
                  }
                  className="h-5 w-5"
                />
              </label>
            </CardContent>
          </Card>

          <Card className="rounded-2xl border-slate-200 shadow-sm">
            <CardHeader>
              <CardTitle>Strategy Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="space-y-2">
                <label className="font-medium text-slate-900">Rebalance frequency</label>
                <select
                  value={settings.rebalance_frequency}
                  onChange={(e) => updateField("rebalance_frequency", e.target.value)}
                  className="w-full rounded-xl border border-slate-300 px-3 py-2"
                >
                  <option value="weekly">Weekly</option>
                  <option value="daily">Daily</option>
                  <option value="monthly">Monthly</option>
                </select>
                <p className="text-sm text-slate-500">
                  Controls the preferred strategy rebalance frequency.
                </p>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end">
            <Button
              onClick={handleSave}
              disabled={saving}
              className="rounded-xl bg-cyan-600 hover:bg-cyan-700"
            >
              {saving ? "Saving..." : "Save Settings"}
            </Button>
          </div>
        </>
      )}
    </div>
  )
}