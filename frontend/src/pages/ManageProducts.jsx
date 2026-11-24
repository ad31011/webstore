import { useEffect, useState } from "react";
import { api } from "../api";

const EMPTY = { name: "", description: "", price: "", initial_quantity: "",
                gender_id: "", category_id: "", brand_id: "", color_id: "", size_id: "" };
const SELECTS = [["gender_id", "genders"], ["category_id", "categories"], ["brand_id", "brands"],
                 ["color_id", "colors"], ["size_id", "sizes"]];

export default function ManageProducts({ role }) {
  const [products, setProducts] = useState([]);
  const [lookups, setLookups] = useState({});
  const [form, setForm] = useState(EMPTY);
  const [editId, setEditId] = useState(null);
  const [msg, setMsg] = useState("");

  const load = () => api("/products").then(setProducts).catch((e) => setMsg(e.message));

  useEffect(() => {
    load();
    Promise.all(SELECTS.map(([, l]) => api(`/${l}`))).then((res) => {
      const o = {};
      SELECTS.forEach(([, l], i) => (o[l] = res[i]));
      setLookups(o);
    });
  }, []);

  async function run(fn, okMsg = "U krye!") {
    try { await fn(); setMsg(okMsg); load(); } catch (err) { setMsg(err.message); }
  }

  function save(e) {
    e.preventDefault();
    const body = { ...form, price: Number(form.price), initial_quantity: Number(form.initial_quantity) };
    SELECTS.forEach(([k]) => (body[k] = body[k] === "" ? null : Number(body[k])));
    run(async () => {
      await api(editId ? `/products/${editId}` : "/products", { method: editId ? "PUT" : "POST", body });
      setForm(EMPTY);
      setEditId(null);
    }, "U ruajt!");
  }

  function edit(p) {
    setEditId(p.id);
    setForm({
      name: p.name, description: p.description || "", price: p.price, initial_quantity: p.initial_quantity,
      gender_id: p.gender_id ?? "", category_id: p.category_id ?? "", brand_id: p.brand_id ?? "",
      color_id: p.color_id ?? "", size_id: p.size_id ?? "",
    });
  }

  const remove = (p) => window.confirm(`Ta fshij "${p.name}"?`) &&
    run(() => api(`/products/${p.id}`, { method: "DELETE" }));

  const stock = (p) => {
    const v = prompt("Sasia fillestare e re:", p.initial_quantity);
    if (v !== null) run(() => api(`/products/${p.id}/stock`, { method: "PATCH", body: { initial_quantity: Number(v) } }));
  };

  const discount = (p) => {
    const pct = prompt("Përqindja e zbritjes (p.sh. 20):");
    if (!pct) return;
    const days = prompt("Sa ditë zgjat?", "7");
    if (!days) return;
    const start = new Date();
    const end = new Date();
    end.setDate(end.getDate() + Number(days));
    const fmt = (d) => d.toISOString().slice(0, 10);
    run(() => api(`/products/${p.id}/discounts`, {
      method: "POST", body: { percentage: Number(pct), start_date: fmt(start), end_date: fmt(end) },
    }));
  };

  return (
    <div>
      <h2>{editId ? `Edito produktin #${editId}` : "Shto produkt"}</h2>
      <form className="filters" onSubmit={save}>
        <input required placeholder="Emri" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input placeholder="Përshkrimi" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <input required type="number" step="0.01" placeholder="Çmimi" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} />
        <input required type="number" placeholder="Sasia" value={form.initial_quantity} onChange={(e) => setForm({ ...form, initial_quantity: e.target.value })} />
        {SELECTS.map(([key, list]) => (
          <select key={key} value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })}>
            <option value="">{list}</option>
            {(lookups[list] || []).map((o) => <option key={o.id} value={o.id}>{o.name}</option>)}
          </select>
        ))}
        <button>{editId ? "Ruaj ndryshimet" : "Shto"}</button>
        {editId && <button type="button" onClick={() => { setEditId(null); setForm(EMPTY); }}>Anulo</button>}
      </form>
      {msg && <p className="msg">{msg}</p>}

      <table>
        <thead>
          <tr><th>ID</th><th>Emri</th><th>Çmimi</th><th>Final</th><th>Stok (fillestar/aktual)</th><th>Brendi</th><th>Veprime</th></tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td><td>{p.name}</td><td>{p.price} €</td><td>{p.final_price} €</td>
              <td>{p.initial_quantity} / {p.current_quantity}</td><td>{p.brand}</td>
              <td>
                <button onClick={() => edit(p)}>Edito</button>
                <button onClick={() => stock(p)}>Stoku</button>
                {role === "admin" && <button onClick={() => discount(p)}>Zbritje</button>}
                {role !== "simple" && <button onClick={() => remove(p)}>Fshi</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}