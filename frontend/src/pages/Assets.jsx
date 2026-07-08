import { useEffect, useState } from "react";
import { getAssets } from "../api/client.js";
import { PageHeader } from "./Dashboard.jsx";

export default function Assets({ orgId }) {
  const [assets, setAssets] = useState([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    if (orgId) getAssets(orgId).then(setAssets);
  }, [orgId]);

  const visible = assets.filter((a) => a.value.toLowerCase().includes(filter.toLowerCase()));

  return (
    <div>
      <PageHeader eyebrow="02 — Inventory" title="Discovered assets" />

      <input
        className="w-full max-w-sm bg-panel border border-line rounded px-3 py-2 text-sm font-mono mb-4"
        placeholder="Filter by hostname or IP…"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />

      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line text-ink-muted text-xs font-mono uppercase tracking-wide">
              <th className="text-left px-6 py-3 font-medium">Asset</th>
              <th className="text-left px-6 py-3 font-medium">Type</th>
              <th className="text-left px-6 py-3 font-medium">First Seen</th>
              <th className="text-left px-6 py-3 font-medium">Last Seen</th>
              <th className="text-left px-6 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {visible.length === 0 && (
              <tr><td className="px-6 py-8 text-ink-muted text-center" colSpan={5}>
                No assets yet. Run a discovery scan from the Scans page to populate this list.
              </td></tr>
            )}
            {visible.map((a) => (
              <tr key={a.id} className="border-b border-line-soft last:border-0 hover:bg-panel-raised/40">
                <td className="px-6 py-3 font-mono text-ink">{a.value}</td>
                <td className="px-6 py-3 text-ink-muted font-mono text-xs uppercase">{a.asset_type}</td>
                <td className="px-6 py-3 text-ink-muted text-xs">{new Date(a.first_seen).toLocaleDateString()}</td>
                <td className="px-6 py-3 text-ink-muted text-xs">{new Date(a.last_seen).toLocaleDateString()}</td>
                <td className="px-6 py-3">
                  <span className={`text-xs font-mono ${a.is_active ? "text-[#3FB950]" : "text-ink-muted"}`}>
                    {a.is_active ? "● active" : "○ inactive"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
