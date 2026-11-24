import { useEffect, useState } from "react";
import { api } from "../api";

const TYPES = { genders: "Gjinitë", categories: "Kategoritë", brands: "Brendet", sizes: "Masat", colors: "Ngjyrat" };

export default function Lookups() {
  const [type, setType] = useState("categories");
  const [items, setItems] = useState([]);
  const [name, setName] = useState("");
  const [msg, setMsg] = useState("");

  const load = () => api(`/${type}`).then(setItems);
  useEffect(() => { load(); }, [type]);

  const run = async (fn) => { try { await fn(); setMsg(""); load(); } catch (e) { setMsg(e.message); } };

  return (
    <div>
      <h2>Menaxho: {TYPES[type]}</h2>
      <select value={type} onChange={(e) => setType(e.target.value)}>
        {Object.entries(TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
      </select>
      <form className="filters" onSubmit={(e) => { e.preventDefault(); run(async () => { await api(`/${type}`, { method: "POST", body: { name } }); setName(""); }); }}>
        <input required placeholder="Emri i ri" value={name} onChange={(e) => setName(e.target.value)} />
        <button>Shto</button>
      </form>
      {msg && <p className="msg">{msg}</p>}
      <ul>
        {items.map((i) => (
          <li key={i.id}>
            {i.name}{" "}
            <button onClick={() => { const n = prompt("Emri i ri:", i.name); if (n) run(() => api(`/${type}/${i.id}`, { method: "PUT", body: { name: n } })); }}>Riemërto</button>
            <button onClick={() => run(() => api(`/${type}/${i.id}`, { method: "DELETE" }))}>Fshi</button>
          </li>
        ))}
      </ul>
    </div>
  );
}