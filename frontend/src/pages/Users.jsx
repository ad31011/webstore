import { useEffect, useState } from "react";
import { api } from "../api";

const EMPTY = { username: "", email: "", password: "", role: "simple" };

export default function Users() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [msg, setMsg] = useState("");

  const load = () => api("/users").then(setUsers).catch((e) => setMsg(e.message));
  useEffect(() => { load(); }, []);

  const run = async (fn) => { try { await fn(); setMsg(""); load(); } catch (e) { setMsg(e.message); } };

  return (
    <div>
      <h2>Përdoruesit</h2>
      <form className="filters" onSubmit={(e) => { e.preventDefault(); run(async () => { await api("/users", { method: "POST", body: form }); setForm(EMPTY); }); }}>
        <input required placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <input required placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input required type="password" placeholder="Fjalëkalimi (min 6)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          <option>admin</option><option>advanced</option><option>simple</option>
        </select>
        <button>Krijo</button>
      </form>
      {msg && <p className="msg">{msg}</p>}
      <table>
        <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Roli</th><th>Aktiv</th><th></th></tr></thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.id}</td><td>{u.username}</td><td>{u.email}</td>
              <td>
                <select value={u.role} onChange={(e) => run(() => api(`/users/${u.id}`, { method: "PUT", body: { role: e.target.value } }))}>
                  <option>admin</option><option>advanced</option><option>simple</option>
                </select>
              </td>
              <td>
                <input type="checkbox" checked={u.is_active}
                       onChange={(e) => run(() => api(`/users/${u.id}`, { method: "PUT", body: { is_active: e.target.checked } }))} />
              </td>
              <td><button onClick={() => window.confirm("Ta fshij?") && run(() => api(`/users/${u.id}`, { method: "DELETE" }))}>Fshi</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}