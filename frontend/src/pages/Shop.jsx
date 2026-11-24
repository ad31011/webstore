import { useEffect, useState } from "react";
import { api } from "../api";

const LOOKUPS = { genders: "gender", categories: "category", brands: "brand", sizes: "size", colors: "color" };

export default function Shop() {
  const [lookups, setLookups] = useState({});
  const [filters, setFilters] = useState({ q: "", price_min: "", price_max: "", availability: "" });
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [client, setClient] = useState({ first_name: "", last_name: "", email: "", phone: "", address: "" });
  const [msg, setMsg] = useState("");

  useEffect(() => {
    const names = Object.keys(LOOKUPS);
    Promise.all(names.map((n) => api(`/${n}`))).then((res) => {
      const obj = {};
      names.forEach((n, i) => (obj[n] = res[i]));
      setLookups(obj);
    });
    search();
  }, []);

  async function search(e) {
    e?.preventDefault();
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v !== "" && v != null) params.append(k, v); });
    try { setProducts(await api(`/products/search?${params}`)); } catch (err) { setMsg(err.message); }
  }

  const setF = (k, v) => setFilters({ ...filters, [k]: v });

  function addToCart(p) {
    const found = cart.find((c) => c.product.id === p.id);
    if (found) setCart(cart.map((c) => (c.product.id === p.id ? { ...c, quantity: c.quantity + 1 } : c)));
    else setCart([...cart, { product: p, quantity: 1 }]);
  }

  const total = cart.reduce((s, c) => s + c.product.final_price * c.quantity, 0);

  async function checkout(e) {
    e.preventDefault();
    setMsg("");
    try {
      const c = await api("/clients", { method: "POST", body: client });
      const order = await api("/orders", {
        method: "POST",
        body: { client_id: c.id, items: cart.map((i) => ({ product_id: i.product.id, quantity: i.quantity })) },
      });
      setMsg(`Porosia #${order.id} u krijua! Totali: ${order.total_amount} €`);
      setCart([]);
      search();
    } catch (err) { setMsg(err.message); }
  }

  return (
    <div>
      <h2>Kërko produkte</h2>
      <form className="filters" onSubmit={search}>
        <input placeholder="Emri..." value={filters.q} onChange={(e) => setF("q", e.target.value)} />
        {Object.entries(LOOKUPS).map(([list, key]) => (
          <select key={key} value={filters[key] || ""} onChange={(e) => setF(key, e.target.value)}>
            <option value="">{key} (të gjitha)</option>
            {(lookups[list] || []).map((o) => <option key={o.id} value={o.name}>{o.name}</option>)}
          </select>
        ))}
        <input type="number" placeholder="Çmimi min" value={filters.price_min} onChange={(e) => setF("price_min", e.target.value)} />
        <input type="number" placeholder="Çmimi max" value={filters.price_max} onChange={(e) => setF("price_max", e.target.value)} />
        <select value={filters.availability} onChange={(e) => setF("availability", e.target.value)}>
          <option value="">Disponueshmëria</option>
          <option value="in_stock">Në stok</option>
          <option value="out_of_stock">Pa stok</option>
        </select>
        <button>Kërko</button>
      </form>

      {msg && <p className="msg">{msg}</p>}

      <div className="grid">
        {products.map((p) => (
          <div key={p.id} className="card">
            <h3>{p.name}</h3>
            <p>{p.brand} · {p.category} · {p.gender}</p>
            <p>Ngjyra: {p.color} · Masa: {p.size}</p>
            <p>
              {p.discount_percent > 0
                ? <><s>{p.price} €</s> <b>{p.final_price} €</b> (-{p.discount_percent}%)</>
                : <b>{p.price} €</b>}
            </p>
            <p>Në stok: {p.current_quantity}</p>
            <button disabled={p.current_quantity <= 0} onClick={() => addToCart(p)}>Shto në shportë</button>
          </div>
        ))}
      </div>

      <h2>Shporta</h2>
      {cart.length === 0 ? <p>Shporta është bosh.</p> : (
        <>
          <ul>
            {cart.map((c) => (
              <li key={c.product.id}>
                {c.product.name} × {c.quantity} = {(c.product.final_price * c.quantity).toFixed(2)} €{" "}
                <button onClick={() => setCart(cart.filter((x) => x !== c))}>Hiq</button>
              </li>
            ))}
          </ul>
          <p><b>Totali: {total.toFixed(2)} €</b></p>
          <form className="card narrow" onSubmit={checkout}>
            <h3>Të dhënat e klientit</h3>
            {Object.keys(client).map((k) => (
              <input key={k} placeholder={k} required={k !== "phone" && k !== "address"}
                     value={client[k]} onChange={(e) => setClient({ ...client, [k]: e.target.value })} />
            ))}
            <button>Porosit</button>
          </form>
        </>
      )}
    </div>
  );
}