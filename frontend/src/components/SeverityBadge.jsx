const STYLES = {
  critical: "bg-sev-critical/15 text-sev-critical border-sev-critical/40",
  high: "bg-sev-high/15 text-sev-high border-sev-high/40",
  medium: "bg-sev-medium/15 text-sev-medium border-sev-medium/40",
  low: "bg-sev-low/15 text-sev-low border-sev-low/40",
  info: "bg-sev-info/15 text-sev-info border-sev-info/40",
};

export default function SeverityBadge({ severity }) {
  const cls = STYLES[severity] || STYLES.info;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-[11px] font-mono uppercase tracking-wide ${cls}`}>
      {severity}
    </span>
  );
}
