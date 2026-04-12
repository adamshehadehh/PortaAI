import { Badge } from "@/components/ui/badge"

export default function Topbar() {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
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
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-700">
          A
        </div>
      </div>
    </header>
  )
}