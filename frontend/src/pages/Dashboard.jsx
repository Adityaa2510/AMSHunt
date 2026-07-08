import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts";
import RiskGauge from "../components/RiskGauge.jsx";
import { getRiskScore, getAssets, getScans } from "../api/client.js";

const SEV_COLORS = { critical: "#E5484D", high: "#F2994A", medium: "#F2C94C", low: "#56CCF2", info: "#5B6572" };

export default function Dashboard({ orgId }) {
  const [risk, setRisk] = useState(null);
  const [assetCount, setAssetCount] = useState(0);
  const [recentScans, setRecentScans] = useState([]);

  useEffect(() => {
    if (!orgId) return;
    getRiskScore(orgId).then(setRisk);
    getAssets(orgId).then((a) => setAssetCount(a.length));
    getScans(orgId).then((s) => setRecentScans(s.slice(0, 6)));
  }, [orgId]);

  const severityData = risk
    ? [
        { name: "critical", count: risk.critical_count },
        { name: "high", count: risk.high_count },
        { name: "medium", count: risk.medium_count },
        { name: "low", count: risk.low_count },
      ]
    : [];

  return (
    <div>
      <PageHeader eyebrow="01 — Overview" title="Attack surface, at a glance" />

      <div className="grid grid-cols-3 gap-6 mb-6">
        <div className="panel p-6 flex flex-col items-center justify-center">
          <div className="text-ink-muted text-xs font-mono uppercase tracking-wide mb-3">Exposure Score</div>
          <RiskGauge score={risk?.score ?? 0} grade={risk?.grade ?? "A"} />
        </div>

        <div className="panel p-6">
          <div className="text-ink-muted text-xs font-mono uppercase tracking-wide mb-4">Open Findings by Severity</div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={severityData} layout="vertical" margin={{ left: 8 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="name" tick={{ fill: "#7C8894", fontSize: 11, fontFamily: "IBM Plex Mono" }} width={60} axisLine={false} tickLine={false} />
              <Bar dataKey="count" radius={[0, 2, 2, 0]} barSize={16}>
                {severityData.map((d) => (
                  <Cell key={d.name} fill={SEV_COLORS[d.name]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="panel p-6 flex flex-col justify-center gap-4">
          <Stat label="Discovered assets" value={assetCount} />
          <Stat label="Critical findings" value={risk?.critical_count ?? 0} accent="#E5484D" />
          <Stat label="High findings" value={risk?.high_count ?? 0} accent="#F2994A" />
        </div>
      </div>

      <div className="panel">
        <div className="px-6 py-4 border-b border-line text-ink-muted text-xs font-mono uppercase tracking-wide">Recent Scans</div>
        <table className="w-full text-sm">
          <tbody>
            {recentScans.length === 0 && (
              <tr><td className="px-6 py-8 text-ink-muted text-center" colSpan={4}>No scans run yet. Head to Scans to start one.</td></tr>
            )}
            {recentScans.map((s) => (
              <tr key={s.id} className="border-b border-line-soft last:border-0">
                <td className="px-6 py-3 font-mono text-xs text-ink-muted">{s.scan_type}</td>
                <td className="px-6 py-3 font-mono text-xs">{s.target}</td>
                <td className="px-6 py-3">
                  <StatusPill status={s.status} />
                </td>
                <td className="px-6 py-3 text-ink-muted text-xs text-right">
                  {s.finished_at ? new Date(s.finished_at).toLocaleString() : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function PageHeader({ eyebrow, title }) {
  return (
    <div className="mb-6">
      <div className="text-signal font-mono text-xs tracking-[0.2em] mb-1">{eyebrow}</div>
      <h1 className="font-display font-semibold text-2xl text-ink">{title}</h1>
    </div>
  );
}

function Stat({ label, value, accent }) {
  return (
    <div>
      <div className="text-ink-muted text-xs font-mono uppercase tracking-wide">{label}</div>
      <div className="font-mono text-2xl font-semibold" style={{ color: accent || "#E8EDF2" }}>{value}</div>
    </div>
  );
}

export function StatusPill({ status }) {
  const styles = {
    queued: "text-ink-muted border-line",
    running: "text-signal border-signal/40",
    completed: "text-[#3FB950] border-[#3FB950]/40",
    failed: "text-sev-critical border-sev-critical/40",
  };
  return (
    <span className={`inline-block px-2 py-0.5 rounded border text-[11px] font-mono uppercase ${styles[status] || styles.queued}`}>
      {status}
    </span>
  );
}
