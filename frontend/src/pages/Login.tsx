import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { saveToken } from "@/lib/auth"
import { BrainCircuit } from "lucide-react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
type LoginResponse = {
  access_token: string
  token_type: string
  user: {
    id: number
    email: string
  }
}

export default function Login() {
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()

    try {
      setLoading(true)
      setError(null)

      const response = await fetch("http://127.0.0.1:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      })

      if (!response.ok) {
        throw new Error("Invalid email or password")
      }

      const data: LoginResponse = await response.json()
      saveToken(data.access_token)

      navigate("/app/dashboard")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="grid w-full max-w-5xl gap-8 lg:grid-cols-2">
        <div className="flex flex-col justify-center space-y-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-500/15 text-cyan-600">
              <BrainCircuit className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                PortaAI
              </h1>
              <p className="text-slate-600">AI-Driven Portfolio Management</p>
            </div>
          </div>

          <div className="space-y-3">
            <h2 className="text-4xl font-bold leading-tight text-slate-900">
              Smarter portfolio decisions with forecasting, sentiment, and explainability.
            </h2>
            <p className="max-w-xl text-base text-slate-600">
              A modern AI platform for portfolio allocation, trade simulation, and transparent decision support.
            </p>
          </div>
        </div>

        <Card className="rounded-3xl border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="text-2xl">Sign in</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="...@example.com"
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-cyan-500"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-cyan-500"
                />
              </div>

              {error && (
                <p className="text-sm font-medium text-red-600">{error}</p>
              )}

              <Button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-cyan-600 hover:bg-cyan-700"
              >
                {loading ? "Signing in..." : "Enter Dashboard"}
              </Button>

              <p className="text-center text-sm text-slate-500">
                Secure login powered by FastAPI authentication
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}