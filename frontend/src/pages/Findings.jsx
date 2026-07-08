import { useEffect, useState } from "react";
import { getFindings, resolveFinding } from "../api/client.js";
import { PageHeader } from "./Dashboard.jsx";
import SeverityBadge from "../components/SeverityBadge.jsx";

const SEVERITIES = ["critical", "high", "medium", "low", "info"];

export default function Findings({ orgId }) {
  const [findings, setFindings] = useState([]);
  const [severity, setSeverity] = useState("");

  function refresh() {
    if (!orgId) return;
    getFindings({ organization_id: orgId, severity: severity || undefined, is_resolved: false }).then(setFindings);
  }

  useEffect(refresh, [orgId, severity]);

  async function handleResolve(id) {
    await resolveFinding(id);
    refresh();
  }

  return (
    <div>
      <PageHeader eyebrow="04 — Triage" title="Open findings" />

      <div className="flex gap-2 mb-4">
        <FilterChip label="All" active={severity === ""} onClick={() => setSeverity("")} />
        {SEVERITIES.map((s) => (
          <FilterChip key={s} label={s} active={severity === s} onClick={() => setSeverity(s)} />
        ))}
      </div>

      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line text-ink-muted text-xs font-mono uppercase tracking-wide">
              <th className="text-left px-6 py-3 font-medium">Severity</th>
              <th className="text-left px-6 py-3 font-medium">Finding</th>
              <th className="text-left px-6 py-3 font-medium">CVE</th>
              <th className="text-left px-6 py-3 font-medium">Discovered</th>
              <th className="text-right px-6 py-3 font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            {findings.length === 0 && (
              <tr><td className="px-6 py-8 text-ink-muted text-center" colSpan={5}>No open findings for this filter.</td></tr>
            )}
            {findings.map((f) => (
              <tr key={f.id} className="border-b border-line-soft last:border-0 align-top">
                <td className="px-6 py-3"><SeverityBadge severity={f.severity} /></td>
                <td className="px-6 py-3">
                  <div className="text-ink">{f.title}</div>
                  {f.description && <div className="text-ink-muted text-xs mt-0.5 max-w-md">{f.description}</div>}
                </td>
                <td className="px-6 py-3 font-mono text-xs text-ink-muted">{f.cve_id || "—"}</td>
                <td className="px-6 py-3 text-ink-muted text-xs">{new Date(f.discovered_at).toLocaleDateString()}</td>
                <td className="px-6 py-3 text-right">
                  <button
                    onClick={() => handleResolve(f.id)}
                    className="text-xs font-mono text-signal hover:text-signal-dim border border-signal/30 rounded px-2 py-1 transition-colors"
                  >
                    Mark resolved
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function FilterChip({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded border text-xs font-mono uppercase tracking-wide transition-colors ${
        active ? "border-signal text-signal bg-signal/10" : "border-line text-ink-muted hover:text-ink"
      }`}
    >
      {label}
    </button>
  );
}
