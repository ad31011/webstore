const BASE = "http://localhost:8000/api";

// Funksion i përbashkët për të gjitha thirrjet e API-së
export async function api(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = localStorage.getItem("token");
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(BASE + path, {
    method, headers, body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const d = data?.detail;
    throw new Error(typeof d === "string" ? d : d ? JSON.stringify(d) : `Gabim ${res.status}`);
  }
  return data;
}