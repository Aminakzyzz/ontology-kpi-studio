import { useState } from "react";
import { ArrowUpRight, Database, Network, ShieldCheck, Sparkles } from "lucide-react";

const SUGGESTIONS = [
  "What is the on-time delivery rate?",
  "Show revenue by region",
  "Which months had late deliveries?",
];

function Results({ result }) {
  if (!result) return <div className="empty"><Sparkles size={28} /><p>Ask a question about the local operations dataset.</p></div>;
  const columns = Object.keys(result.rows[0] || {});
  return <section className="result"><div className="result-head"><div><p className="eyebrow">SEMANTIC ANSWER</p><h2>{result.title}</h2><p>{result.summary}</p></div><span className="pill">{result.mode}</span></div>
    <div className="metric-grid">{result.rows.map((row, i) => <article className="metric" key={i}>{Object.entries(row).map(([key, value]) => <div key={key}><span>{key.replaceAll("_", " ")}</span><strong>{typeof value === "number" ? value.toLocaleString() : value}</strong></div>)}</article>)}</div>
    {columns.length > 1 && <table><thead><tr>{columns.map(c => <th key={c}>{c.replaceAll("_", " ")}</th>)}</tr></thead><tbody>{result.rows.map((row,i)=><tr key={i}>{columns.map(c=><td key={c}>{String(row[c])}</td>)}</tr>)}</tbody></table>}
    <details><summary>Generated read-only SQL</summary><code>{result.sql}</code></details></section>;
}

export default function App() {
  const [question, setQuestion] = useState(""); const [result, setResult] = useState(null); const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function ask(text = question) { if (!text.trim()) return; setLoading(true); setError(""); setQuestion(text); try { const res = await fetch("/api/ask", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({question:text})}); const body = await res.json(); if(!res.ok) throw new Error(body.detail); setResult(body); } catch(e) { setError(e.message); } finally { setLoading(false); } }
  return <main><aside><div className="brand"><div className="brand-mark">O</div><div><b>Ontology KPI</b><span>Studio</span></div></div><nav><a className="active">Workspace</a><a>Saved views</a><a>Ontology</a></nav><div className="source"><Database size={16}/><div><small>DATA SOURCE</small><b>Local SQLite</b><span>Read-only demo</span></div></div><div className="foot">v0.1.0 · local-first</div></aside><div className="shell"><header><div><p className="eyebrow">SEMANTIC ANALYTICS</p><h1>Ask questions with context.</h1></div><div className="trust"><ShieldCheck size={17}/> Grounded queries</div></header><section className="hero"><div><span className="tag"><Network size={14}/> Ontology-backed</span><h2>Understand the metric<br/><em>before</em> running the query.</h2><p>A portable analytics workspace with transparent, read-only SQL and an inspectable domain model.</p></div><div className="model"><small>SEMANTIC LAYER</small><b>Operations ontology</b><p>4 concepts · 2 relationships</p><button>Inspect model <ArrowUpRight size={15}/></button></div></section><section className="workspace"><div className="ask"><label htmlFor="question">Ask the data</label><div className="composer"><input id="question" value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>e.key==="Enter"&&ask()} placeholder="e.g. Show revenue by region"/><button onClick={()=>ask()} disabled={loading}>{loading?"Working…":"Ask"}</button></div><div className="suggestions">{SUGGESTIONS.map(s=><button key={s} onClick={()=>ask(s)}>{s}</button>)}</div>{error&&<p className="error">{error}</p>}</div><Results result={result}/></section></div></main>;
}

