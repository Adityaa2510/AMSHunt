import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Assets from "./pages/Assets.jsx";
import Scans from "./pages/Scans.jsx";
import Findings from "./pages/Findings.jsx";
import Reports from "./pages/Reports.jsx";
import { getOrganizations, createOrganization } from "./api/client.js";

export default function App() {
  const [organizations, setOrganizations] = useState([]);
  const [activeOrgId, setActiveOrgId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getOrganizations()
      .then((orgs) => {
        setOrganizations(orgs);
        if (orgs.length > 0) setActiveOrgId(orgs[0].id);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleCreateOrg(name, rootDomain) {
    const org = await createOrganization({ name, root_domain: rootDomain });
    setOrganizations((prev) => [...prev, org]);
    setActiveOrgId(org.id);
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-ink-muted font-mono text-sm">Loading console…</div>;
  }

  return (
    <div className="min-h-screen flex">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar
          organizations={organizations}
          activeOrgId={activeOrgId}
          onSelectOrg={setActiveOrgId}
          onCreateOrg={handleCreateOrg}
        />
        <main className="flex-1 p-8 overflow-y-auto">
          {!activeOrgId ? (
            <EmptyState onCreateOrg={handleCreateOrg} />
          ) : (
            <Routes>
              <Route path="/" element={<Dashboard orgId={activeOrgId} />} />
              <Route path="/assets" element={<Assets orgId={activeOrgId} />} />
              <Route path="/scans" element={<Scans orgId={activeOrgId} />} />
              <Route path="/findings" element={<Findings orgId={activeOrgId} />} />
              <Route path="/reports" element={<Reports orgId={activeOrgId} />} />
            </Routes>
          )}
        </main>
      </div>
    </div>
  );
}

function Topbar({ organizations, activeOrgId, onSelectOrg }) {
  const active = organizations.find((o) => o.id === activeOrgId);
  return (
    <header className="h-14 border-b border-line bg-panel flex items-center justify-between px-8">
      <div className="text-sm text-ink-muted">
        Target: <span className="text-ink font-mono">{active?.root_domain || "none selected"}</span>
      </div>
      {organizations.length > 1 && (
        <select
          value={activeOrgId || ""}
          onChange={(e) => onSelectOrg(e.target.value)}
          className="bg-panel-raised border border-line rounded px-2 py-1 text-sm text-ink"
        >
          {organizations.map((o) => (
            <option key={o.id} value={o.id}>{o.name}</option>
          ))}
        </select>
      )}
    </header>
  );
}

function EmptyState({ onCreateOrg }) {
  const [name, setName] = useState("");
  const [domain, setDomain] = useState("");

  return (
    <div className="max-w-md mx-auto mt-24 panel p-8 text-center">
      <div className="text-signal font-mono text-xs tracking-[0.2em] mb-2">NO TARGET REGISTERED</div>
      <h2 className="font-display font-semibold text-xl mb-4">Register your first organization</h2>
      <p className="text-ink-muted text-sm mb-6">
        This maps to a root domain. Every discovered subdomain, port, and finding attaches here.
      </p>
      <div className="space-y-3 text-left">
        <input
          className="w-full bg-void border border-line rounded px-3 py-2 text-sm"
          placeholder="Organization name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          className="w-full bg-void border border-line rounded px-3 py-2 text-sm font-mono"
          placeholder="root-domain.com"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
        />
        <button
          className="w-full bg-signal text-void font-medium rounded px-3 py-2 text-sm hover:bg-signal-dim transition-colors"
          onClick={() => name && domain && onCreateOrg(name, domain)}
        >
          Create organization
        </button>
      </div>
    </div>
  );
}
