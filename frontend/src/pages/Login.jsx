import { useState } from "react";
import { api } from "../api";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/auth/login", { method: "POST", body: { username, password } });
      localStorage.setItem("token", data.access_token);
      onLogin(data.user);
    } catch (err) { setError(err.message); }
  }

  return (
    <form className="card narrow" onSubmit={submit}>
      <h2>Hyrje</h2>
      <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input type="password" placeholder="Fjalëkalimi" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button>Hyr</button>
      {error && <p className="msg">{error}</p>}
    </form>
  );
}