import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Dashboard", key: "01" },
  { to: "/assets", label: "Assets", key: "02" },
  { to: "/scans", label: "Scans", key: "03" },
  { to: "/findings", label: "Findings", key: "04" },
  { to: "/reports", label: "Reports", key: "05" },
];

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 border-r border-line bg-panel flex flex-col">
      <div className="px-5 py-5 border-b border-line">
        <div className="text-signal font-mono text-xs tracking-[0.2em]">ASM</div>
        <div className="text-ink font-display font-semibold text-sm mt-0.5">Surface Console</div>
      </div>
      <nav className="flex-1 py-3">
        {LINKS.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-2.5 text-sm border-l-2 transition-colors ${
                isActive
                  ? "border-signal text-ink bg-panel-raised"
                  : "border-transparent text-ink-muted hover:text-ink hover:bg-panel-raised/50"
              }`
            }
          >
            <span className="font-mono text-[10px] text-ink-muted">{l.key}</span>
            {l.label}
          </NavLink>
        ))}
      </nav>
      <div className="px-5 py-4 border-t border-line text-[11px] text-ink-muted font-mono">
        Nmap · Subfinder · httpx<br />Nuclei · WhatWeb
      </div>
    </aside>
  );
}
