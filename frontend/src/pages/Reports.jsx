import { useEffect, useState } from "react";
import { api } from "../api";

function Table({ rows }) {
  if (!rows?.length) return <p>Nuk ka të dhëna.</p>;
  const cols = Object.keys(rows[0]);
  return (
    <table>
      <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
      <tbody>{rows.map((r, i) => <tr key={i}>{cols.map((c) => <td key={c}>{String(r[c])}</td>)}</tr>)}</tbody>
    </table>
  );
}

export default function Reports() {
  const [daily, setDaily] = useState([]);
  const [monthly, setMonthly] = useState([]);
  const [top, setTop] = useState([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    Promise.all([api("/reports/daily-earnings"), api("/reports/monthly-earnings"), api("/reports/top-products?limit=5")])
      .then(([d, m, t]) => { setDaily(d); setMonthly(m); setTop(t); })
      .catch((e) => setMsg(e.message));
  }, []);

  return (
    <div>
      {msg && <p className="msg">{msg}</p>}
      <h2>Fitimet ditore</h2><Table rows={daily} />
      <h2>Fitimet mujore</h2><Table rows={monthly} />
      <h2>Produktet më të shitura</h2><Table rows={top} />
    </div>
  );
}