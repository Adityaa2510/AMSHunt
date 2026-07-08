import { useEffect, useState } from "react";
import { getExecutiveSummary } from "../api/client.js";
import { PageHeader } from "./Dashboard.jsx";
import RiskGauge from "../components/RiskGauge.jsx";
import SeverityBadge from "../components/SeverityBadge.jsx";

export default function Reports({ orgId }) {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    if (orgId) getExecutiveSummary(orgId).then(setSummary);
  }, [orgId]);

  if (!summary) {
    return (
      <div>
        <PageHeader eyebrow="05 — Reporting" title="Executive summary" />
        <div className="text-ink-muted text-sm">Generating summary…</div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader eyebrow="05 — Reporting" title="Executive summary" />

      <div className="panel p-8 mb-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="text-ink-muted text-xs font-mono uppercase tracking-wide mb-1">{summary.organization.root_domain}</div>
            <h2 className="font-display font-semibold text-xl text-ink">{summary.organization.name}</h2>
          </div>
          <RiskGauge score={summary.risk.score} grade={summary.risk.grade} />
        </div>
        <p className="text-ink-muted text-sm leading-relaxed max-w-2xl">{summary.narrative}</p>
      </div>

      <div className="panel">
        <div className="px-6 py-4 border-b border-line text-ink-muted text-xs font-mono uppercase tracking-wide">
          Top Findings Requiring Attention
        </div>
        <table className="w-full text-sm">
          <tbody>
            {summary.top_findings.length === 0 && (
              <tr><td className="px-6 py-8 text-ink-muted text-center" colSpan={3}>No critical or high findings — clean bill of health.</td></tr>
            )}
            {summary.top_findings.map((f, i) => (
              <tr key={i} className="border-b border-line-soft last:border-0">
                <td className="px-6 py-3"><SeverityBadge severity={f.severity} /></td>
                <td className="px-6 py-3 text-ink">{f.title}</td>
                <td className="px-6 py-3 text-ink-muted text-xs text-right">{new Date(f.discovered_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-ink-muted text-xs font-mono">
        Want this as a downloadable PDF? Wire this same JSON payload into ReportLab on the backend.
      </div>
    </div>
  );
}
