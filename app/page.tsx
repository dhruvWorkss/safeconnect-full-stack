"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type ApiCase } from "./api";

const demoCases = [
  { id: "SC-2841", user: "Maya Chen", initials: "MC", reason: "Targeted harassment", risk: 92, severity: "Critical", time: "2m ago", channel: "Community", color: "#e45f59" },
  { id: "SC-2839", user: "Noah Williams", initials: "NW", reason: "Credible threat", risk: 86, severity: "Critical", time: "8m ago", channel: "Direct message", color: "#d98b47" },
  { id: "SC-2834", user: "Priya Nair", initials: "PN", reason: "Hate speech", risk: 71, severity: "High", time: "21m ago", channel: "Community", color: "#765ce8" },
  { id: "SC-2828", user: "Luca Martin", initials: "LM", reason: "Impersonation", risk: 58, severity: "Medium", time: "34m ago", channel: "Profile", color: "#3b8ac4" },
  { id: "SC-2816", user: "Aisha Khan", initials: "AK", reason: "Repeated spam", risk: 34, severity: "Low", time: "1h ago", channel: "Community", color: "#3e9a7b" },
];

export default function Home() {
  const [caseItems, setCaseItems] = useState(demoCases);
  const [active, setActive] = useState(demoCases[0]);
  const [apiOnline, setApiOnline] = useState(false);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All cases");
  const [resolved, setResolved] = useState<string[]>([]);
  const [toast, setToast] = useState("");
  const visible = useMemo(() => caseItems.filter((item) => !resolved.includes(item.id) && (filter === "All cases" || item.severity === filter) && `${item.id} ${item.user} ${item.reason}`.toLowerCase().includes(query.toLowerCase())), [query, filter, resolved, caseItems]);
  useEffect(() => {
    const connect = async () => {
      try {
        await api.health(); setApiOnline(true);
        if (!localStorage.getItem("safeconnect_access") && ["localhost","127.0.0.1"].includes(location.hostname)) await api.login("moderator","SafeConnect123!");
        const payload: { results?: ApiCase[] } = await api.cases();
        const records=(payload.results || []).map((item) => { const name=item.report.reported_user_detail.display_name || item.report.reported_user_detail.username; return { backendId:item.id, id:item.report.public_id, user:name, initials:name.split(" ").map((part:string)=>part[0]).join("").slice(0,2).toUpperCase(), reason:item.report.category.replace("_"," "), risk:item.report.risk_score, severity:item.priority[0].toUpperCase()+item.priority.slice(1), time:"Live", channel:"Django API", color:"#6654d9" }; });
        if (records.length) { setCaseItems(records); setActive(records[0]); }
      } catch { setApiOnline(false); }
    };
    connect();
  }, []);
  const act = async (message: string, resolve = false, actionName?: string) => { if (actionName && "backendId" in active) { try { await api.act((active as typeof active & {backendId:number}).backendId, actionName); } catch { setToast("API action failed — check moderator login"); return; } } if (resolve) setResolved((items) => [...items, active.id]); setToast(message); setTimeout(() => setToast(""), 2600); };

  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">S</span><span>SafeConnect</span></div>
      <nav><p className="nav-label">Workspace</p><button className="nav-item active"><span>⌂</span> Overview</button><button className="nav-item"><span>◎</span> Case queue <b>12</b></button><button className="nav-item"><span>♧</span> User reports</button><button className="nav-item"><span>◫</span> Appeals</button><p className="nav-label second">Intelligence</p><button className="nav-item"><span>⌁</span> Trends</button><button className="nav-item"><span>◇</span> Audit log</button><button className="nav-item"><span>⚙</span> Policy center</button></nav>
      <div className="sidebar-card"><span className="pulse-dot"/><div><strong>{apiOnline ? "API connected" : "Demo mode"}</strong><small>{apiOnline ? "Django services operational" : "Start backend on port 8000"}</small></div></div>
      <div className="profile"><span className="avatar small">JD</span><div><strong>Jordan Davis</strong><small>Senior moderator</small></div><span>•••</span></div>
    </aside>
    <section className="workspace">
      <header className="topbar"><div><p className="eyebrow">TRUST &amp; SAFETY / OVERVIEW</p><h1>Good morning, Jordan.</h1></div><div className="top-actions"><button className="icon-button" aria-label="Notifications">♢<i/></button><button className="primary" onClick={() => act("Report intake opened")}>＋ New report</button></div></header>
      <div className="metrics">
        <article><div className="metric-head"><span>Open cases</span><b className="badge violet">Live</b></div><strong>48</strong><p><em>↓ 12%</em> from last week</p><div className="spark"><i/><i/><i/><i/><i/><i/></div></article>
        <article><div className="metric-head"><span>Critical priority</span><b className="badge red">Action</b></div><strong>7</strong><p><em className="red-text">↑ 2</em> since yesterday</p><div className="spark red-spark"><i/><i/><i/><i/><i/><i/></div></article>
        <article><div className="metric-head"><span>Median response</span><b className="badge green">On target</b></div><strong>8m 42s</strong><p><em>↓ 1m 18s</em> this month</p><div className="spark green-spark"><i/><i/><i/><i/><i/><i/></div></article>
        <article><div className="metric-head"><span>Resolution rate</span><b className="badge blue">30 days</b></div><strong>94.6%</strong><p><em>↑ 3.2%</em> improvement</p><div className="ring"><span>95</span></div></article>
      </div>
      <div className="content-grid">
        <section className="queue panel"><div className="panel-header"><div><h2>Priority queue</h2><p>Cases ranked by risk and urgency</p></div><button className="link-button">View all <span>→</span></button></div>
          <div className="toolbar"><label><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search cases or people..." /></label><select aria-label="Filter severity" value={filter} onChange={(e) => setFilter(e.target.value)}><option>All cases</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select></div>
          <div className="table-head"><span>Reporter / Case</span><span>Category</span><span>Risk</span><span>Status</span><span></span></div><div className="case-list">
            {visible.map((item) => <button key={item.id} className={`case-row ${active.id === item.id ? "selected" : ""}`} onClick={() => setActive(item)}><span className="person"><i className="avatar" style={{background:item.color}}>{item.initials}</i><span><strong>{item.user}</strong><small>{item.id} · {item.time}</small></span></span><span className="category"><strong>{item.reason}</strong><small>{item.channel}</small></span><span className="risk"><i style={{width:`${item.risk}%`}}/><b>{item.risk}</b></span><span className={`severity ${item.severity.toLowerCase()}`}>{item.severity}</span><span className="chevron">›</span></button>)}{!visible.length && <div className="empty">No cases match this view.</div>}
          </div></section>
        <aside className="case-detail panel"><div className="case-top"><div><span className={`severity ${active.severity.toLowerCase()}`}>{active.severity} risk</span><h2>{active.id}</h2></div><button aria-label="More options">•••</button></div>
          <div className="reporter-card"><span className="avatar large" style={{background:active.color}}>{active.initials}</span><div><small>REPORTED USER</small><strong>{active.user}</strong><p>@{active.user.toLowerCase().replace(" ", ".")} · Joined 2023</p></div><button>View profile ↗</button></div>
          <div className="risk-score"><div className="risk-title"><span>Risk assessment</span><strong>{active.risk}<small>/100</small></strong></div><div className="risk-track"><i style={{width:`${active.risk}%`}}/></div><div className="risk-labels"><span>Low</span><span>Moderate</span><span>Severe</span></div></div>
          <div className="evidence"><div className="section-title"><h3>Flagged content</h3><span>2 signals</span></div><blockquote>“You won’t be laughing when I find out where you live. Keep talking.”</blockquote><div className="signal"><span>!</span><div><strong>Threatening language detected</strong><small>Classifier confidence: 96.4%</small></div></div></div>
          <div className="context"><h3>Account context</h3><div><span>Prior reports<strong>4</strong></span><span>Prior actions<strong>1 warning</strong></span><span>Account age<strong>2.4 years</strong></span></div></div>
          <div className="action-box"><button className="resolve" onClick={() => act(`${active.id} resolved and archived`, true, "resolve")}>Resolve case</button><button className="escalate" onClick={() => act(`${active.id} escalated to senior review`, false, "escalate")}>Escalate</button></div><button className="history" onClick={() => act("Audit history loaded")}>View full case history <span>→</span></button>
        </aside>
      </div>
    </section>{toast && <div className="toast"><span>✓</span>{toast}</div>}
  </main>;
}
