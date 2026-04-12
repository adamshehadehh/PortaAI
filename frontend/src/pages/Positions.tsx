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
import { positions } from "@/data/mockData"

function formatPercent(value: number) {
  return `${value.toFixed(2)}%`
}

export default function Positions() {
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

      <Card className="rounded-2xl border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Current Holdings</CardTitle>
        </CardHeader>
        <CardContent>
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
                  <TableCell className="font-medium">{position.symbol}</TableCell>
                  <TableCell>{position.quantity}</TableCell>
                  <TableCell>${position.avgCost.toFixed(2)}</TableCell>
                  <TableCell>{formatPercent(position.currentWeight)}</TableCell>
                  <TableCell>
                    <Badge className="rounded-full bg-cyan-600 hover:bg-cyan-600">
                      {position.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card className="rounded-2xl border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Positions Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-600">
            PortaAI currently holds a diversified set of positions selected by
            the decision engine based on quantitative signals, sentiment, and
            confidence-adjusted allocation rules.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}