import { useEffect, useState } from "react";
import { api } from "../api";

const STATUSES = ["pending", "confirmed", "shipped", "delivered", "cancelled"];

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [msg, setMsg] = useState("");

  const load = () => api("/orders").then(setOrders).catch((e) => setMsg(e.message));
  useEffect(() => { load(); }, []);

  async function changeStatus(id, status) {
    try { await api(`/orders/${id}/status`, { method: "PATCH", body: { status } }); setMsg(""); load(); }
    catch (e) { setMsg(e.message); }
  }

  return (
    <div>
      <h2>Porositë</h2>
      {msg && <p className="msg">{msg}</p>}
      <table>
        <thead><tr><th>#</th><th>Klienti</th><th>Data</th><th>Produktet</th><th>Totali</th><th>Statusi</th></tr></thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td>{o.id}</td>
              <td>{o.client_name}</td>
              <td>{new Date(o.created_at).toLocaleString()}</td>
              <td>{o.items.map((i) => `${i.product_name} ×${i.quantity}`).join(", ")}</td>
              <td>{o.total_amount} €</td>
              <td>
                <select value={o.status} onChange={(e) => changeStatus(o.id, e.target.value)}>
                  {STATUSES.map((s) => <option key={s}>{s}</option>)}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}