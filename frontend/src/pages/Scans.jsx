import { useEffect, useState } from "react";
import { getScans, createScan, getAssets } from "../api/client.js";
import { PageHeader, StatusPill } from "./Dashboard.jsx";

const SCAN_TYPES = [
  { value: "discovery", label: "Discovery (subfinder + httpx)", needsAsset: false },
  { value: "port_scan", label: "Port Scan (nmap)", needsAsset: true },
  { value: "tech_detect", label: "Tech + SSL (httpx/whatweb)", needsAsset: true },
  { value: "vuln_scan", label: "Vulnerability Scan (nuclei)", needsAsset: true },
];

export default function Scans({ orgId }) {
  const [scans, setScans] = useState([]);
  const [assets, setAssets] = useState([]);
  const [scanType, setScanType] = useState("discovery");
  const [target, setTarget] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function refresh() {
    if (!orgId) return;
    getScans(orgId).then(setScans);
    getAssets(orgId).then(setAssets);
  }

  useEffect(refresh, [orgId]);
  useEffect(() => {
    const interval = setInterval(refresh, 5000); // poll for status updates while scans run
    return () => clearInterval(interval);
  }, [orgId]);

  const needsAsset = SCAN_TYPES.find((s) => s.value === scanType)?.needsAsset;

  async function handleSubmit(e) {
    e.preventDefault();
    if (!target) return;
    setSubmitting(true);
    try {
      await createScan({ organization_id: orgId, scan_type: scanType, target });
      setTarget("");
      refresh();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <PageHeader eyebrow="03 — Pipeline" title="Run and monitor scans" />

      <form onSubmit={handleSubmit} className="panel p-5 mb-6 flex items-end gap-3">
        <div className="flex-1">
          <label className="block text-ink-muted text-xs font-mono uppercase tracking-wide mb-1.5">Scan Type</label>
          <select
            value={scanType}
            onChange={(e) => setScanType(e.target.value)}
            className="w-full bg-void border border-line rounded px-3 py-2 text-sm"
          >
            {SCAN_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
        </div>
        <div className="flex-1">
          <label className="block text-ink-muted text-xs font-mono uppercase tracking-wide mb-1.5">
            Target {needsAsset ? "(existing asset)" : "(root domain)"}
          </label>
          {needsAsset ? (
            <select value={target} onChange={(e) => setTarget(e.target.value)} className="w-full bg-void border border-line rounded px-3 py-2 text-sm font-mono">
              <option value="">Select an asset…</option>
              {assets.map((a) => <option key={a.id} value={a.value}>{a.value}</option>)}
            </select>
          ) : (
            <input
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="example.com"
              className="w-full bg-void border border-line rounded px-3 py-2 text-sm font-mono"
            />
          )}
        </div>
        <button
          disabled={submitting || !target}
          className="bg-signal text-void font-medium rounded px-4 py-2 text-sm hover:bg-signal-dim transition-colors disabled:opacity-40"
        >
          {submitting ? "Queuing…" : "Run scan"}
        </button>
      </form>

      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line text-ink-muted text-xs font-mono uppercase tracking-wide">
              <th className="text-left px-6 py-3 font-medium">Type</th>
              <th className="text-left px-6 py-3 font-medium">Target</th>
              <th className="text-left px-6 py-3 font-medium">Status</th>
              <th className="text-left px-6 py-3 font-medium">Result</th>
              <th className="text-left px-6 py-3 font-medium">Started</th>
            </tr>
          </thead>
          <tbody>
            {scans.length === 0 && (
              <tr><td className="px-6 py-8 text-ink-muted text-center" colSpan={5}>No scans queued yet.</td></tr>
            )}
            {scans.map((s) => (
              <tr key={s.id} className="border-b border-line-soft last:border-0">
                <td className="px-6 py-3 font-mono text-xs text-ink-muted uppercase">{s.scan_type}</td>
                <td className="px-6 py-3 font-mono text-ink">{s.target}</td>
                <td className="px-6 py-3"><StatusPill status={s.status} /></td>
                <td className="px-6 py-3 text-ink-muted text-xs font-mono">
                  {s.error_message ? <span className="text-sev-critical">{s.error_message}</span> : JSON.stringify(s.result_summary)}
                </td>
                <td className="px-6 py-3 text-ink-muted text-xs">{s.started_at ? new Date(s.started_at).toLocaleTimeString() : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
