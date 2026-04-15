import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { apiFetch } from "@/lib/api"
import { useEffect, useState } from "react"
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

type DashboardSummary = {
  portfolio_id: number
  total_value: number
  cash: number
  invested_percent: number
}

type AllocationItem = {
  name: string
  value: number
}

type AllocationResponse = {
  portfolio_id: number
  allocation: AllocationItem[]
}

type HistoryItem = {
  label: string
  value: number
}

type HistoryResponse = {
  portfolio_id: number
  history: HistoryItem[]
}

const pieColors = [
  "#0891b2",
  "#0f172a",
  "#14b8a6",
  "#38bdf8",
  "#64748b",
  "#06b6d4",
]

function formatCurrency(value: number) {
  return `$${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function formatPercent(value: number) {
  return `${value.toFixed(1)}%`
}

function DashboardCard({
  title,
  value,
  subtitle,
}: {
  title: string
  value: string
  subtitle: string
}) {
  return (
    <Card className="rounded-2xl border-slate-200 shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-slate-500">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-semibold tracking-tight text-slate-900">
          {value}
        </p>
        <p className="mt-2 text-sm text-slate-500">{subtitle}</p>
      </CardContent>
    </Card>
  )
}

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [allocation, setAllocation] = useState<AllocationItem[]>([])
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchDashboardData(showLoading = false) {
      try {
        if (showLoading) {
          setLoading(true)
        }

        setError(null)

        const [summaryRes, allocationRes, historyRes] = await Promise.all([
          apiFetch("http://127.0.0.1:8000/api/dashboard/summary"),
          apiFetch("http://127.0.0.1:8000/api/dashboard/allocation"),
          apiFetch("http://127.0.0.1:8000/api/dashboard/history"),
        ])

        if (!summaryRes.ok) throw new Error("Failed to fetch dashboard summary")
        if (!allocationRes.ok) throw new Error("Failed to fetch allocation data")
        if (!historyRes.ok) throw new Error("Failed to fetch history data")

        const summaryData: DashboardSummary = await summaryRes.json()
        const allocationData: AllocationResponse = await allocationRes.json()
        const historyData: HistoryResponse = await historyRes.json()

        setSummary((prev) => {
          const prevJson = JSON.stringify(prev)
          const nextJson = JSON.stringify(summaryData)
          return prevJson !== nextJson ? summaryData : prev
        })

        setAllocation((prev) => {
          const prevJson = JSON.stringify(prev)
          const nextJson = JSON.stringify(allocationData.allocation)
          return prevJson !== nextJson ? allocationData.allocation : prev
        })

        setHistory((prev) => {
          const prevJson = JSON.stringify(prev)
          const nextJson = JSON.stringify(historyData.history)
          return prevJson !== nextJson ? historyData.history : prev
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        if (showLoading) {
          setLoading(false)
        }
      }
    }

    fetchDashboardData(true)

    const handlePortfolioUpdate = () => {
      fetchDashboardData(false)
    }

    window.addEventListener("portfolio-data-updated", handlePortfolioUpdate)

    const intervalId = window.setInterval(() => {
      fetchDashboardData(false)
    }, 10000)

    return () => {
      window.removeEventListener("portfolio-data-updated", handlePortfolioUpdate)
      window.clearInterval(intervalId)
    }
  }, [])

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Home
          </h1>
          <Badge variant="secondary" className="rounded-full">
            Overview
          </Badge>
        </div>
        <p className="text-slate-600">
          Overview of portfolio value, allocation, and recent performance.
        </p>
      </header>

      {error && (
        <Card className="rounded-2xl border-red-200 shadow-sm">
          <CardContent className="pt-6">
            <p className="font-medium text-red-600">Error: {error}</p>
          </CardContent>
        </Card>
      )}

      <section className="grid gap-4 md:grid-cols-3">
        <DashboardCard
          title="Total Portfolio Value"
          value={loading || !summary ? "Loading..." : formatCurrency(summary.total_value)}
          subtitle="Latest simulated portfolio valuation"
        />

        <DashboardCard
          title="Cash Available"
          value={loading || !summary ? "Loading..." : formatCurrency(summary.cash)}
          subtitle="Capital currently not allocated to assets"
        />

        <DashboardCard
          title="Invested Exposure"
          value={loading || !summary ? "Loading..." : formatPercent(summary.invested_percent)}
          subtitle="Dynamic allocation based on confidence"
        />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Portfolio Value Trend</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            {loading ? (
              <div className="flex h-full items-center justify-center text-slate-500">
                Loading chart...
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" />
                  <YAxis />
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#0891b2"
                    fill="#67e8f9"
                    fillOpacity={0.18}
                    strokeWidth={2.5}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Allocation Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            {loading ? (
              <div className="flex h-full items-center justify-center text-slate-500">
                Loading chart...
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Tooltip formatter={(value) => `${Number(value).toFixed(2)}%`} />
                  <Pie
                    data={allocation}
                    dataKey="value"
                    nameKey="name"
                    outerRadius={100}
                  >
                    {allocation.map((entry, index) => (
                      <Cell
                        key={`${entry.name}-${index}`}
                        fill={pieColors[index % pieColors.length]}
                      />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </section>

      <Card className="rounded-2xl border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Dashboard Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-slate-600">
          <p>
            PortaAI currently maintains a confidence-adjusted allocation between
            cash and selected assets.
          </p>
          <p>
            Portfolio decisions are driven by XGBoost forecasts, transformer-based
            sentiment analysis, and explainable AI signals.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}