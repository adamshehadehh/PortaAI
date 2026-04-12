import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Settings() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Settings
          </h1>
          <Badge variant="secondary" className="rounded-full">
            Configuration
          </Badge>
        </div>
        <p className="text-slate-600">
          Configure portfolio preferences, asset selection, and system behavior.
        </p>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Portfolio Configuration</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600">
              Manage portfolio name, base currency, and initial capital.
            </p>
            <p className="mt-3 text-sm text-slate-400">
              Coming soon — backend integration required
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Asset Universe</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600">
              Select which assets PortaAI can trade within the portfolio.
            </p>
            <p className="mt-3 text-sm text-slate-400">
              Coming soon — dynamic asset selection
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Allocation & Risk Controls</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600">
              Adjust investment limits, rebalance frequency, and risk preferences.
            </p>
            <p className="mt-3 text-sm text-slate-400">
              Coming soon — configurable strategy parameters
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-600">
              Control alerts for trades, portfolio changes, and AI signals.
            </p>
            <p className="mt-3 text-sm text-slate-400">
              Coming soon — notification preferences
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="rounded-2xl border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Settings Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-600">
            The settings panel will allow users to customize how PortaAI manages
            their portfolio, including asset selection, allocation strategies,
            and risk preferences. These features will be fully enabled after
            backend integration.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}