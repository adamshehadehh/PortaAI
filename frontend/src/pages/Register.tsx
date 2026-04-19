import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { apiFetch } from "@/lib/api"
import { saveToken } from "@/lib/auth"
import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"

type RegisterResponse = {
  access_token: string
  token_type: string
  user: {
    id: number
    email: string
  }
  portfolio: {
    id: number
    name: string
  }
}

export default function Register() {
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault()

    try {
      setLoading(true)
      setError(null)

      const response = await apiFetch("http://127.0.0.1:8000/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail || "Registration failed")
      }

      const data: RegisterResponse = await response.json()

      saveToken(data.access_token)

      await new Promise((resolve) => setTimeout(resolve, 150))

      navigate("/app/dashboard", { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <Card className="w-full max-w-md rounded-2xl border-slate-200 shadow-sm">
        <CardHeader className="space-y-3 text-center">
          <div className="flex justify-center">
            <Badge className="rounded-full bg-cyan-600 hover:bg-cyan-700">
              PortaAI
            </Badge>
          </div>
          <CardTitle className="text-2xl font-bold text-slate-900">
            Create your account
          </CardTitle>
          <p className="text-sm text-slate-500">
            Register to create your portfolio and access the platform.
          </p>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleRegister} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full rounded-xl border border-slate-300 px-3 py-2 outline-none transition focus:border-cyan-500"
                placeholder="you@example.com"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full rounded-xl border border-slate-300 px-3 py-2 outline-none transition focus:border-cyan-500"
                placeholder="Enter your password"
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
              {loading ? "Creating account..." : "Register"}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-medium text-cyan-700 hover:underline"
            >
              Log in
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}