import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { apiFetch } from "@/lib/api"
import { useEffect, useState } from "react"

type ExplanationReason = {
  feature: string
  value: number
  shap: number
  direction: "UP" | "DOWN" | "NEUTRAL"
}

type ExplanationItem = {
  symbol: string
  predicted_return: number
  reasons: ExplanationReason[]
  summary: string
}

type ExplainabilityResponse = {
  portfolio_id: number
  explanations: ExplanationItem[]
}

function DirectionBadge({ direction }: { direction: string }) {
  if (direction === "UP") {
    return (
      <Badge className="rounded-full bg-emerald-600 hover:bg-emerald-700">
        Pushes Up
      </Badge>
    )
  }

  if (direction === "DOWN") {
    return (
      <Badge className="rounded-full bg-red-600 hover:bg-red-700">
        Pushes Down
      </Badge>
    )
  }

  return (
    <Badge className="rounded-full bg-slate-200 text-slate-700">
      Neutral
    </Badge>
  )
}

function formatSigned(value: number, digits = 6) {
  const formatted = value.toFixed(digits)
  return value > 0 ? `+${formatted}` : formatted
}

function valueColor(value: number) {
  if (value > 0) return "text-emerald-600 font-medium"
  if (value < 0) return "text-red-600 font-medium"
  return "text-slate-600"
}

export default function Explainability() {
  const [explanations, setExplanations] = useState<ExplanationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchExplainability(showLoading = false) {
      try {
        if (showLoading) {
          setLoading(true)
        }

        setError(null)

        const response = await apiFetch("http://127.0.0.1:8000/api/dashboard/explainability")

        if (!response.ok) {
          throw new Error("Failed to fetch explainability data")
        }

        const data: ExplainabilityResponse = await response.json()

        setExplanations((prev) => {
          const prevJson = JSON.stringify(prev)
          const nextJson = JSON.stringify(data.explanations)
          return prevJson !== nextJson ? data.explanations : prev
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error")
      } finally {
        if (showLoading) {
          setLoading(false)
        }
      }
    }

    fetchExplainability(true)

    const handlePortfolioUpdate = () => {
      fetchExplainability(false)
    }

    window.addEventListener("portfolio-data-updated", handlePortfolioUpdate)

    const intervalId = window.setInterval(() => {
      fetchExplainability(false)
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

      {error && (
        <Card className="rounded-2xl border-red-200 shadow-sm">
          <CardContent className="pt-6">
            <p className="font-medium text-red-600">Error: {error}</p>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <Card className="rounded-2xl border-slate-200 shadow-sm">
          <CardContent className="pt-6">
            <p className="text-slate-600">Loading explainability data...</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 xl:grid-cols-2">
          {explanations.map((item) => (
            <Card
              key={item.symbol}
              className="rounded-2xl border-slate-200 shadow-sm"
            >
              <CardHeader className="space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <CardTitle className="text-xl">{item.symbol}</CardTitle>

                  <Badge
                    className={`rounded-full ${
                      item.predicted_return >= 0
                        ? "bg-emerald-600 hover:bg-emerald-700"
                        : "bg-red-600 hover:bg-red-700"
                    }`}
                  >
                    {formatSigned(item.predicted_return, 6)}
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
                      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                        <p className="font-medium text-slate-900">
                          {reason.feature}
                        </p>
                        <DirectionBadge direction={reason.direction} />
                      </div>

                      <div className="grid gap-2 text-sm md:grid-cols-2">
                        <p className="text-slate-600">
                          <span className="font-medium text-slate-800">
                            Feature Value:
                          </span>{" "}
                          <span className={valueColor(reason.value)}>
                            {formatSigned(reason.value, 6)}
                          </span>
                        </p>

                        <p className="text-slate-600">
                          <span className="font-medium text-slate-800">
                            SHAP Impact:
                          </span>{" "}
                          <span className={valueColor(reason.shap)}>
                            {formatSigned(reason.shap, 6)}
                          </span>
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="rounded-xl border border-cyan-100 bg-cyan-50 p-4">
                  <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-cyan-800">
                    Model Interpretation
                  </h3>
                  <p className="text-sm leading-6 text-slate-700">
                    {item.summary}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card className="rounded-2xl border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle>Why Explainability Matters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-slate-600">
          <p>
            PortaAI uses SHAP to make model predictions more transparent. Instead of
            only showing the final asset forecast, the platform also reveals which
            features contributed most strongly to the prediction.
          </p>
          <p>
            This makes the system easier to interpret, validate, and present in a
            real-world portfolio management setting.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}