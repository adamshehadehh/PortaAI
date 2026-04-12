import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Area,
  AreaChart,
  CartesianGrid,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { allocationData, portfolioHistory, portfolioSummary } from "@/data/mockData"

export default function Dashboard() {
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
          Overview of portfolio value, cash, allocation, and recent performance.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Total Portfolio Value</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold text-slate-900">
              ${portfolioSummary.totalValue.toFixed(2)}
            </p>
            <p className="mt-2 text-sm text-slate-500">
              Latest simulated portfolio valuation
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Cash Available</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold text-slate-900">
              ${portfolioSummary.cash.toFixed(2)}
            </p>
            <p className="mt-2 text-sm text-slate-500">
              Capital currently not allocated to assets
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Invested Exposure</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold text-slate-900">
              {portfolioSummary.investedPercent.toFixed(1)}%
            </p>
            <p className="mt-2 text-sm text-slate-500">
              Dynamic allocation based on confidence
            </p>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Portfolio Value Trend</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={portfolioHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#0891b2"
                  fill="#67e8f9"
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle>Allocation Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Tooltip />
                <Pie
                  data={allocationData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={100}
                  fill="#0891b2"
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </section>

      <Card className="rounded-2xl border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Dashboard Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-600">
            PortaAI currently maintains a balanced allocation between cash and
            selected assets, with decisions driven by XGBoost forecasts,
            transformer-based sentiment analysis, and explainable AI signals.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}