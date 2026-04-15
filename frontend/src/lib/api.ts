import { getToken, removeToken } from "./auth"

export async function apiFetch(url: string, options: RequestInit = {}) {
  const token = getToken()

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })

  // HANDLE 401 HERE
  if (response.status === 401) {
    removeToken()
    window.location.href = "/login"
    return response
  }

  return response
}