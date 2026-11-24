import { useEffect, useState } from "react";
import { api } from "./api";
import Login from "./pages/Login";
import Shop from "./pages/Shop";
import ManageProducts from "./pages/ManageProducts";
import Lookups from "./pages/Lookups";
import Orders from "./pages/Orders";
import Reports from "./pages/Reports";
import Users from "./pages/Users";

export default function App() {
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("shop");

  useEffect(() => {
    if (localStorage.getItem("token")) {
      api("/auth/me").then(setUser).catch(() => localStorage.removeItem("token"));
    }
  }, []);

  const role = user?.role;
  const isManager = role === "admin" || role === "advanced";
  const tabs = [
    ["shop", "Dyqani", true],
    ["products", "Menaxho produktet", !!user],
    ["lookups", "Kategori/Brende", isManager],
    ["orders", "Porositë", isManager],
    ["reports", "Raportet", isManager],
    ["users", "Përdoruesit", role === "admin"],
  ];

  const logout = () => { localStorage.removeItem("token"); setUser(null); setPage("shop"); };

  return (
    <div className="container">
      <nav>
        {tabs.filter((t) => t[2]).map(([key, label]) => (
          <button key={key} className={page === key ? "active" : ""} onClick={() => setPage(key)}>{label}</button>
        ))}
        <span className="spacer" />
        {user
          ? <>{user.username} ({user.role}) <button onClick={logout}>Dil</button></>
          : <button onClick={() => setPage("login")}>Hyr</button>}
      </nav>

      {page === "login" && <Login onLogin={(u) => { setUser(u); setPage("products"); }} />}
      {page === "shop" && <Shop />}
      {page === "products" && user && <ManageProducts role={role} />}
      {page === "lookups" && isManager && <Lookups />}
      {page === "orders" && isManager && <Orders />}
      {page === "reports" && isManager && <Reports />}
      {page === "users" && role === "admin" && <Users />}
    </div>
  );
}
