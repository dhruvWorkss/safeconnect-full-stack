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
  const [session, setSession] = useState<{name:string;role:string;workspace:string;company:string} | null>(null);
  const [loginError, setLoginError] = useState("");
  const [caseItems, setCaseItems] = useState(demoCases);
  const [active, setActive] = useState(demoCases[0]);
  const [apiOnline, setApiOnline] = useState(false);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All cases");
  const [resolved, setResolved] = useState<string[]>([]);
  const [toast, setToast] = useState("");
  const [activeNav, setActiveNav] = useState("Overview");
  const [reportOpen, setReportOpen] = useState(false);
  const visible = useMemo(() => caseItems.filter((item) => !resolved.includes(item.id) && (filter === "All cases" || item.severity === filter) && `${item.id} ${item.user} ${item.reason}`.toLowerCase().includes(query.toLowerCase())), [query, filter, resolved, caseItems]);
  useEffect(() => {
    const saved=localStorage.getItem("safeconnect_user"); if (saved && localStorage.getItem("safeconnect_access_v2")) setSession(JSON.parse(saved));
  }, []);
  useEffect(() => {
    if (!session) return;
    const connect = async () => {
      try {
        await api.health(); setApiOnline(true);
        const payload: { results?: ApiCase[] } = await api.cases();
        const records=(payload.results || []).map((item) => { const name=item.report.reported_user_detail.display_name || item.report.reported_user_detail.username; return { backendId:item.id, reportedUserId:item.report.reported_user_detail.id, id:item.report.public_id, user:name, initials:name.split(" ").map((part:string)=>part[0]).join("").slice(0,2).toUpperCase(), reason:item.report.category.replace("_"," "), risk:item.report.risk_score, severity:item.priority[0].toUpperCase()+item.priority.slice(1), time:"Live", channel:"Django API", color:"#6654d9" }; });
        if (records.length) { setCaseItems(records); setActive(records[0]); }
      } catch { setApiOnline(false); }
    };
    connect();
  }, [session]);
  const act = async (message: string, resolve = false, actionName?: string) => { if (actionName && "backendId" in active) { try { await api.act((active as typeof active & {backendId:number}).backendId, actionName); } catch { setToast("API action failed — check moderator login"); return; } } if (resolve) setResolved((items) => [...items, active.id]); setToast(message); setTimeout(() => setToast(""), 2600); };

  const signIn = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setLoginError(""); const data=new FormData(event.currentTarget);
    try { const result=await api.login(String(data.get("workspace")),String(data.get("username")),String(data.get("password"))); setSession(result.user); }
    catch (error) { setLoginError(error instanceof Error ? error.message : "Unable to sign in"); }
  };
  const navigate = (name: string) => { setActiveNav(name); if (name === "Case queue") { setFilter("All cases"); setQuery(""); } setToast(`${name} view opened`); setTimeout(() => setToast(""), 1800); };
  const showNotifications = async () => { try { const data=await api.notifications(); setToast(`${data.count ?? data.results?.length ?? 0} notifications in your workspace`); } catch { setToast("Unable to load notifications"); } setTimeout(() => setToast(""),2600); };
  const submitReport = async (event: React.FormEvent<HTMLFormElement>) => { event.preventDefault(); const data=new FormData(event.currentTarget); if (!("reportedUserId" in active)) { setToast("Select a live Django case first"); return; } try { await api.createReport((active as typeof active & {reportedUserId:number}).reportedUserId,String(data.get("category")),String(data.get("description"))); setReportOpen(false); setToast("New report created and added to moderation workflow"); } catch { setToast("This active report may already exist; choose another category"); } setTimeout(()=>setToast(""),3200); };
  if (!session) return <main className="login-page"><section className="login-story"><div className="brand login-brand"><span className="brand-mark">S</span><span>SafeConnect</span></div><div className="story-copy"><span className="secure-label">ENTERPRISE TRUST &amp; SAFETY</span><h1>Your community.<br/><em>Protected.</em></h1><p>One command center for the people, policies, and decisions that keep your platform safe.</p><div className="trust-points"><span><b>99.99%</b> platform uptime</span><span><b>&lt; 9 min</b> median response</span><span><b>Complete</b> auditability</span></div></div><div className="story-orbit"><i/><i/><i/></div><small className="story-foot">SOC 2 READY · ENCRYPTED · TENANT ISOLATED</small></section><section className="login-panel"><div className="login-box"><span className="step">SECURE WORKSPACE ACCESS</span><h2>Welcome back</h2><p>Sign in with your company credentials.</p><form onSubmit={signIn}><label>Company workspace<input name="workspace" defaultValue="nova-social" placeholder="your-company" required/></label><label>Employee username<input name="username" defaultValue="moderator" placeholder="name@company.com" required/></label><label>Password<div className="password-wrap"><input name="password" type="password" defaultValue="SafeConnect123!" required/><span>◉</span></div></label><div className="login-meta"><label><input type="checkbox" defaultChecked/> Keep me signed in</label><button type="button">Forgot password?</button></div>{loginError && <div className="login-error">{loginError}</div>}<button className="login-submit" type="submit">Enter workspace <span>→</span></button></form><div className="sso-divider"><span>or continue with company SSO</span></div><div className="sso-row"><button>G&nbsp; Google</button><button>▦&nbsp; Microsoft</button></div><small className="demo-hint">Demo access is pre-filled for Nova Social.</small></div></section></main>;

  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">S</span><span>SafeConnect</span></div>
      <nav><p className="nav-label">Workspace</p>{[["⌂","Overview"],["◎","Case queue"],["♧","User reports"],["◫","Appeals"]].map(([icon,name])=><button key={name} className={`nav-item ${activeNav===name?"active":""}`} onClick={()=>navigate(name)}><span>{icon}</span> {name}{name==="Case queue"&&<b>{visible.length}</b>}</button>)}<p className="nav-label second">Intelligence</p>{[["⌁","Trends"],["◇","Audit log"],["⚙","Policy center"]].map(([icon,name])=><button key={name} className={`nav-item ${activeNav===name?"active":""}`} onClick={()=>navigate(name)}><span>{icon}</span> {name}</button>)}</nav>
      <div className="sidebar-card"><span className="pulse-dot"/><div><strong>{apiOnline ? "API connected" : "Demo mode"}</strong><small>{apiOnline ? "Django services operational" : "Start backend on port 8000"}</small></div></div>
      <button className="profile profile-button" onClick={() => {api.logout();setSession(null)}}><span className="avatar small">{session.name.split(" ").map(n=>n[0]).join("").slice(0,2)}</span><div><strong>{session.name}</strong><small>{session.company} · {session.role}</small></div><span>↪</span></button>
    </aside>
    <section className="workspace">
      <header className="topbar"><div><p className="eyebrow">{session.company.toUpperCase()} / TRUST &amp; SAFETY / {activeNav.toUpperCase()}</p><h1>{activeNav === "Overview" ? `Good morning, ${session.name.split(" ")[0]}.` : activeNav}</h1></div><div className="top-actions"><button className="icon-button" aria-label="Notifications" onClick={showNotifications}>♢<i/></button><button className="primary" onClick={() => setReportOpen(true)}>＋ New report</button></div></header>
      <div className="metrics">
        <article><div className="metric-head"><span>Open cases</span><b className="badge violet">Live</b></div><strong>48</strong><p><em>↓ 12%</em> from last week</p><div className="spark"><i/><i/><i/><i/><i/><i/></div></article>
        <article><div className="metric-head"><span>Critical priority</span><b className="badge red">Action</b></div><strong>7</strong><p><em className="red-text">↑ 2</em> since yesterday</p><div className="spark red-spark"><i/><i/><i/><i/><i/><i/></div></article>
        <article><div className="metric-head"><span>Median response</span><b className="badge green">On target</b></div><strong>8m 42s</strong><p><em>↓ 1m 18s</em> this month</p><div className="spark green-spark"><i/><i/><i/><i/><i/><i/></div></article>
        <article><div className="metric-head"><span>Resolution rate</span><b className="badge blue">30 days</b></div><strong>94.6%</strong><p><em>↑ 3.2%</em> improvement</p><div className="ring"><span>95</span></div></article>
      </div>
      <div className="content-grid">
        <section className="queue panel"><div className="panel-header"><div><h2>{activeNav === "Overview" ? "Priority queue" : activeNav}</h2><p>Live workspace records ranked by risk and urgency</p></div><button className="link-button" onClick={()=>{setQuery("");setFilter("All cases");setActiveNav("Case queue")}}>View all <span>→</span></button></div>
          <div className="toolbar"><label><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search cases or people..." /></label><select aria-label="Filter severity" value={filter} onChange={(e) => setFilter(e.target.value)}><option>All cases</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select></div>
          <div className="table-head"><span>Reporter / Case</span><span>Category</span><span>Risk</span><span>Status</span><span></span></div><div className="case-list">
            {visible.map((item) => <button key={item.id} className={`case-row ${active.id === item.id ? "selected" : ""}`} onClick={() => setActive(item)}><span className="person"><i className="avatar" style={{background:item.color}}>{item.initials}</i><span><strong>{item.user}</strong><small>{item.id} · {item.time}</small></span></span><span className="category"><strong>{item.reason}</strong><small>{item.channel}</small></span><span className="risk"><i style={{width:`${item.risk}%`}}/><b>{item.risk}</b></span><span className={`severity ${item.severity.toLowerCase()}`}>{item.severity}</span><span className="chevron">›</span></button>)}{!visible.length && <div className="empty">No cases match this view.</div>}
          </div></section>
        <aside className="case-detail panel"><div className="case-top"><div><span className={`severity ${active.severity.toLowerCase()}`}>{active.severity} risk</span><h2>{active.id}</h2></div><button aria-label="More options">•••</button></div>
          <div className="reporter-card"><span className="avatar large" style={{background:active.color}}>{active.initials}</span><div><small>REPORTED USER</small><strong>{active.user}</strong><p>@{active.user.toLowerCase().replace(" ", ".")} · Joined 2023</p></div><button onClick={()=>act(`${active.user}'s safety profile opened`)}>View profile ↗</button></div>
          <div className="risk-score"><div className="risk-title"><span>Risk assessment</span><strong>{active.risk}<small>/100</small></strong></div><div className="risk-track"><i style={{width:`${active.risk}%`}}/></div><div className="risk-labels"><span>Low</span><span>Moderate</span><span>Severe</span></div></div>
          <div className="evidence"><div className="section-title"><h3>Flagged content</h3><span>2 signals</span></div><blockquote>“You won’t be laughing when I find out where you live. Keep talking.”</blockquote><div className="signal"><span>!</span><div><strong>Threatening language detected</strong><small>Classifier confidence: 96.4%</small></div></div></div>
          <div className="context"><h3>Account context</h3><div><span>Prior reports<strong>4</strong></span><span>Prior actions<strong>1 warning</strong></span><span>Account age<strong>2.4 years</strong></span></div></div>
          <div className="action-box"><button className="resolve" onClick={() => act(`${active.id} resolved and archived`, true, "resolve")}>Resolve case</button><button className="escalate" onClick={() => act(`${active.id} escalated to senior review`, false, "escalate")}>Escalate</button></div><button className="history" onClick={() => act("Audit history loaded")}>View full case history <span>→</span></button>
        </aside>
      </div>
    </section>{reportOpen&&<div className="modal-backdrop" onClick={()=>setReportOpen(false)}><form className="report-modal" onSubmit={submitReport} onClick={e=>e.stopPropagation()}><button type="button" className="modal-close" onClick={()=>setReportOpen(false)}>×</button><span className="step">NEW SAFETY REPORT</span><h2>Report {active.user}</h2><p>Create a real report in the Django moderation workflow.</p><label>Category<select name="category" defaultValue="harassment"><option value="harassment">Harassment</option><option value="threat">Threat</option><option value="hate">Hate speech</option><option value="impersonation">Impersonation</option><option value="spam">Spam</option><option value="other">Other</option></select></label><label>Incident details<textarea name="description" required minLength={10} placeholder="Describe what happened and why it needs review..."/></label><div className="modal-actions"><button type="button" onClick={()=>setReportOpen(false)}>Cancel</button><button className="primary" type="submit">Create report</button></div></form></div>}{toast && <div className="toast"><span>✓</span>{toast}</div>}
  </main>;
}
