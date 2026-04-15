import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { apiFetch } from "@/lib/api"
import { useEffect, useState } from "react"

type Position = {
  symbol: string
  quantity: number
  avg_cost: number
  current_weight: number
  status: string
}

type PositionsResponse = {
  portfolio_id: number
  positions: Position[]
}

function formatPercent(value: number) {
  return `${value.toFixed(2)}%`
}

function formatQuantity(value: number) {
  return value.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 4,
  })
}

function formatCurrency(value: number) {
  return `$${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

export default function Positions() {
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPositions(showLoading = false) {
      try {
        if (showLoading) {
          setLoading(true)
        }

        setError(null)

        const response = await apiFetch("http://127.0.0.1:8000/api/dashboard/positions")

        if (!response.ok) {
          throw new Error("Failed to fetch positions")
        }

        const data: PositionsResponse = await response.json()

        setPositions((prev) => {
          const prevJson = JSON.stringify(prev)
          const nextJson = JSON.stringify(data.positions)
          return prevJson !== nextJson ? data.positions : prev
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        if (showLoading) {
          setLoading(false)
        }
      }
    }

    fetchPositions(true)

    const handlePortfolioUpdate = () => {
      fetchPositions(false)
    }

    window.addEventListener("portfolio-data-updated", handlePortfolioUpdate)

    const intervalId = window.setInterval(() => {
      fetchPositions(false)
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
            Positions
          </h1>
          <Badge variant="secondary" className="rounded-full">
            Holdings
          </Badge>
        </div>
        <p className="text-slate-600">
          Current portfolio holdings, average cost, and allocation weights.
        </p>
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
          <CardTitle>Current Holdings</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-slate-600">Loading positions...</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Asset</TableHead>
                  <TableHead>Quantity</TableHead>
                  <TableHead>Average Cost</TableHead>
                  <TableHead>Weight</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {positions.map((position) => (
                  <TableRow key={position.symbol}>
                    <TableCell className="font-medium text-slate-900">
                      {position.symbol}
                    </TableCell>
                    <TableCell className="font-medium text-slate-800">
                      {formatQuantity(position.quantity)}
                    </TableCell>
                    <TableCell className="font-medium text-slate-800">
                      {formatCurrency(position.avg_cost)}
                    </TableCell>
                    <TableCell className="font-medium text-slate-800">
                      {formatPercent(position.current_weight)}
                    </TableCell>
                    <TableCell>
                      <Badge className="rounded-full bg-cyan-600 hover:bg-cyan-700">
                        {position.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card className="rounded-2xl border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Positions Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-slate-600">
          <p>
            PortaAI currently holds a diversified set of positions selected by
            the decision engine based on quantitative signals, sentiment, and
            confidence-adjusted allocation rules.
          </p>
          <p>
            Position sizing is determined by the portfolio allocation engine and
            updated after each rebalance cycle.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}