export const API_URL = process.env.NEXT_PUBLIC_API_URL || "/api/backend";

export type ApiCase = {
  id: number;
  status: string;
  priority: string;
  report: {
    public_id: string;
    risk_score: number;
    category: string;
    created_at: string;
    reported_user_detail: { id: number; display_name: string; username: string };
  };
};

async function request(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("safeconnect_access_v2") : null;
  const response = await fetch(`${API_URL}${path}`, { ...options, headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers } });
  if (!response.ok) throw new Error(`API ${response.status}`);
  return response.json();
}

export const api = {
  health: () => fetch(`${API_URL}/health/`).then((response) => response.json()),
  login: (workspace: string, username: string, password: string) => fetch(`${API_URL}/auth/token/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ workspace, username, password }) }).then(async (response) => { if (!response.ok) throw new Error("Check your workspace and credentials"); const data = await response.json(); localStorage.setItem("safeconnect_access_v2", data.access); localStorage.setItem("safeconnect_refresh_v2", data.refresh); localStorage.setItem("safeconnect_user", JSON.stringify(data.user)); return data; }),
  logout: () => { localStorage.removeItem("safeconnect_access_v2"); localStorage.removeItem("safeconnect_refresh_v2"); localStorage.removeItem("safeconnect_user"); },
  cases: () => request("/cases/?ordering=-report__risk_score"),
  notifications: () => request("/notifications/"),
  auditLogs: () => request("/audit-logs/?ordering=-created_at"),
  createReport: (reported_user: number, category: string, description: string) => request("/reports/", { method: "POST", body: JSON.stringify({ reported_user, category, description }) }),
  act: (id: number, action: string, notes = "") => request(`/cases/${id}/act/`, { method: "POST", body: JSON.stringify({ action, notes }) }),
  stats: () => request("/dashboard/stats/"),
};
