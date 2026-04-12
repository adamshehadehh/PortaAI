import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { explanations } from "@/data/mockData"

function DirectionBadge({ direction }: { direction: string }) {
  if (direction === "UP") {
    return <Badge className="rounded-full">Pushes Up</Badge>
  }

  if (direction === "DOWN") {
    return (
      <Badge variant="destructive" className="rounded-full">
        Pushes Down
      </Badge>
    )
  }

  return (
    <Badge variant="secondary" className="rounded-full">
      Neutral
    </Badge>
  )
}

function formatSigned(value: number, digits = 6) {
  const formatted = value.toFixed(digits)
  return value > 0 ? `+${formatted}` : formatted
}

export default function Explainability() {
  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            Explainability
          </h1>
          <Badge variant="secondary" className="rounded-full">
            SHAP Insights
          </Badge>
        </div>
        <p className="text-slate-600">
          SHAP-based explanations showing why the model predicted each asset’s return.
        </p>
      </header>

      <div className="grid gap-6 xl:grid-cols-2">
        {explanations.map((item) => (
          <Card
            key={item.symbol}
            className="rounded-2xl border-slate-200 shadow-sm"
          >
            <CardHeader className="space-y-3">
              <div className="flex items-center justify-between">
                <CardTitle>{item.symbol}</CardTitle>
                <Badge className="rounded-full bg-cyan-600 hover:bg-cyan-600">
                  Predicted Return {formatSigned(item.predictedReturn, 6)}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <div className="space-y-3">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                  Top 3 Feature Drivers
                </h3>

                {item.reasons.map((reason) => (
                  <div
                    key={`${item.symbol}-${reason.feature}`}
                    className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                  >
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <p className="font-medium text-slate-900">{reason.feature}</p>
                      <DirectionBadge direction={reason.direction} />
                    </div>

                    <div className="grid gap-2 text-sm text-slate-600 md:grid-cols-2">
                      <p>
                        <span className="font-medium text-slate-800">Feature Value:</span>{" "}
                        {formatSigned(reason.value, 6)}
                      </p>
                      <p>
                        <span className="font-medium text-slate-800">SHAP Impact:</span>{" "}
                        {formatSigned(reason.shap, 6)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="rounded-xl border border-cyan-100 bg-cyan-50 p-4">
                <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-cyan-800">
                  Model Interpretation
                </h3>
                <p className="text-sm leading-6 text-slate-700">{item.summary}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="rounded-2xl border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Why Explainability Matters</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-600">
            PortaAI uses SHAP to make model predictions more transparent. Instead of
            only showing the final asset forecast, the platform also reveals which
            features contributed most strongly to the prediction and whether each one
            pushed the forecast upward or downward.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}