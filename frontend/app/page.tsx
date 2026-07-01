"use client";

import { useState } from "react";
import { Chat } from "../components/Chat";
import { createSession, login, register } from "../lib/api";

export default function HomePage() {
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("password123");
  const [token, setToken] = useState<string>("");
  const [sessionId, setSessionId] = useState<string>("");
  const [error, setError] = useState<string>("");

  async function authenticate(mode: "login" | "register") {
    setError("");
    try {
      const auth = mode === "login" ? await login(email, password) : await register(email, password);
      setToken(auth.access_token);
      const session = await createSession(auth.access_token, "SaaS MVP Chat");
      setSessionId(session.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "认证失败");
    }
  }

  if (token && sessionId) {
    return (
      <main className="container">
        <header className="hero">
          <h1>Xuan Agent</h1>
          <p>多用户 SaaS MVP · 当前会话：{sessionId}</p>
        </header>
        <Chat token={token} sessionId={sessionId} />
      </main>
    );
  }

  return (
    <main className="container narrow">
      <section className="card">
        <h1>Xuan Agent SaaS MVP</h1>
        <p>注册或登录后进入独立用户 workspace。</p>
        <label>
          邮箱
          <input value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label>
          密码
          <input
            value={password}
            type="password"
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error ? <p className="error">{error}</p> : null}
        <div className="row">
          <button onClick={() => authenticate("register")}>注册并进入</button>
          <button className="secondary" onClick={() => authenticate("login")}>
            登录
          </button>
        </div>
      </section>
    </main>
  );
}
