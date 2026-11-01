"use client";

import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const API = "http://127.0.0.1:8000";

type Reading = {
  id: number; time: string; temperature: number; humidity: number;
  light: number; motion: number; ac: number; light_on: number;
};
type Event = { id: number; time: string; decision: string; result: string };

const RESULT_COLOR: Record<string, string> = {
  OK: "text-emerald-400", SENT: "text-sky-400", BLOCKED: "text-amber-400", FAILED: "text-red-400",
};

function Card({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
    </div>
  );
}

async function toggle(device: string, state: boolean) {
  await fetch(API + "/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ device, state }),
  });
}

function Device({ name, id, on }: { name: string; id: string; on: boolean }) {
  return (
    <div className={`rounded-2xl border p-5 ${on ? "border-emerald-500/50 bg-emerald-500/10" : "border-slate-800 bg-slate-900/60"}`}>
      <p className="text-sm text-slate-400">{name}</p>
      <div className="mt-2 flex items-center justify-between">
        <p className={`text-2xl font-bold ${on ? "text-emerald-400" : "text-slate-500"}`}>{on ? "ON" : "OFF"}</p>
        <button
          onClick={() => toggle(id, !on)}
          className="rounded-xl bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-sky-400"
        >
          Turn {on ? "OFF" : "ON"}
        </button>
      </div>
    </div>
  );
}

export default function Home() {
  const [state, setState] = useState<Reading | null>(null);
  const [history, setHistory] = useState<Reading[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [online, setOnline] = useState(true);
  const [text, setText] = useState("");
  const [reply, setReply] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [s, h, e] = await Promise.all([
          fetch(API + "/state").then((x) => x.json()),
          fetch(API + "/readings?limit=40").then((x) => x.json()),
          fetch(API + "/events?limit=12").then((x) => x.json()),
        ]);
        if (s.id) setState(s);
        setHistory([...h].reverse());
        setEvents(e);
        setOnline(true);
      } catch {
        setOnline(false);
      }
    }
    load();
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, []);

  async function send() {
    if (!text.trim()) return;
    await fetch(API + "/user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    setReply("Sent to AURA: " + text);
    setText("");
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl space-y-8 px-6 py-8">
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">AURA</h1>
            <p className="text-sm text-slate-400">Autonomous smart room · Living Room</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <span className={`h-2.5 w-2.5 rounded-full ${online ? "animate-pulse bg-emerald-400" : "bg-red-500"}`} />
            {online ? "Live" : "API offline"}
          </div>
        </header>

        <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Card label="🌡️ Temperature" value={state ? state.temperature + "°C" : "-"} />
          <Card label="💧 Humidity" value={state ? state.humidity + "%" : "-"} />
          <Card label="☀️ Light" value={state ? String(state.light) : "-"} />
          <Card label="🚶 Motion" value={state ? (state.motion ? "Detected" : "None") : "-"} />
        </section>

        <section className="grid grid-cols-2 gap-4">
          <Device name="❄️ Air Conditioner" id="ac" on={!!state?.ac} />
          <Device name="💡 Light" id="light" on={!!state?.light_on} />
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 lg:col-span-2">
            <h2 className="mb-4 text-sm font-semibold text-slate-300">Temperature history</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={history}>
                  <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                  <XAxis dataKey="time" tickFormatter={(v) => String(v).slice(11)} stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: 12 }} />
                  <Line type="monotone" dataKey="temperature" stroke="#38bdf8" strokeWidth={2} dot={false} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
            <h2 className="mb-4 text-sm font-semibold text-slate-300">AURA decisions</h2>
            <ul className="space-y-2 text-sm">
              {events.length === 0 && <li className="text-slate-500">No decisions yet</li>}
              {events.map((e) => (
                <li key={e.id} className="flex justify-between gap-2">
                  <span>{e.decision}</span>
                  <span className={RESULT_COLOR[e.result] ?? ""}>{e.result}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="mb-3 text-sm font-semibold text-slate-300">Talk to AURA</h2>
          <div className="flex gap-3">
            <input
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="e.g. شغّل الإضاءة"
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-2 outline-none focus:border-sky-500"
            />
            <button onClick={send} className="rounded-xl bg-sky-500 px-5 py-2 font-semibold text-slate-950 hover:bg-sky-400">
              Send
            </button>
          </div>
          {reply && <p className="mt-3 text-sm text-slate-400">{reply}</p>}
        </section>
      </div>
    </main>
  );
}
