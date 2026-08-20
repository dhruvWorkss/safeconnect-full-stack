export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export type ApiCase = {
  id: number;
  status: string;
  priority: string;
  report: {
    public_id: string;
    risk_score: number;
    category: string;
    created_at: string;
    reported_user_detail: { display_name: string; username: string };
  };
};

async function request(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("safeconnect_access") : null;
  const response = await fetch(`${API_URL}${path}`, { ...options, headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers } });
  if (!response.ok) throw new Error(`API ${response.status}`);
  return response.json();
}

export const api = {
  health: () => fetch(`${API_URL}/health/`).then((response) => response.json()),
  login: (username: string, password: string) => fetch(`${API_URL}/auth/token/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) }).then(async (response) => { if (!response.ok) throw new Error("Invalid credentials"); const data = await response.json(); localStorage.setItem("safeconnect_access", data.access); localStorage.setItem("safeconnect_refresh", data.refresh); return data; }),
  cases: () => request("/cases/?ordering=-report__risk_score"),
  act: (id: number, action: string, notes = "") => request(`/cases/${id}/act/`, { method: "POST", body: JSON.stringify({ action, notes }) }),
  stats: () => request("/dashboard/stats/"),
};
