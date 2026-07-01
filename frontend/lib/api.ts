const BASE = "http://localhost:8000";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem("token");
  return fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
}
