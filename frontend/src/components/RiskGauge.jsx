/**
 * Signature element: a radial "exposure sweep" gauge, 0-100.
 * Reads like a radar/scan sweep rather than a generic progress ring -
 * a single arc that fills clockwise from 9 o'clock to 3 o'clock (180deg),
 * colored by how exposed the org currently is.
 */
const SIZE = 180;
const STROKE = 14;
const RADIUS = (SIZE - STROKE) / 2;
const CENTER = SIZE / 2;

function polarToCartesian(cx, cy, r, angleDeg) {
  const angleRad = ((angleDeg - 180) * Math.PI) / 180;
  return { x: cx + r * Math.cos(angleRad), y: cy + r * Math.sin(angleRad) };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`;
}

function colorForScore(score) {
  if (score >= 80) return "#E5484D";
  if (score >= 60) return "#F2994A";
  if (score >= 40) return "#F2C94C";
  if (score >= 20) return "#56CCF2";
  return "#3FB950";
}

export default function RiskGauge({ score = 0, grade = "A" }) {
  const clamped = Math.max(0, Math.min(100, score));
  const sweep = (clamped / 100) * 180;
  const color = colorForScore(clamped);

  return (
    <div className="flex flex-col items-center">
      <svg width={SIZE} height={SIZE / 2 + STROKE} viewBox={`0 0 ${SIZE} ${SIZE / 2 + STROKE}`}>
        <path
          d={describeArc(CENTER, CENTER, RADIUS, 0, 180)}
          fill="none"
          stroke="#1A2129"
          strokeWidth={STROKE}
          strokeLinecap="round"
        />
        <path
          d={describeArc(CENTER, CENTER, RADIUS, 0, sweep)}
          fill="none"
          stroke={color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
        <text x={CENTER} y={CENTER - 6} textAnchor="middle" className="font-mono" fontSize="30" fontWeight="600" fill="#E8EDF2">
          {clamped}
        </text>
        <text x={CENTER} y={CENTER + 16} textAnchor="middle" className="font-mono" fontSize="11" fill="#7C8894">
          / 100
        </text>
      </svg>
      <div className="flex items-center gap-2 -mt-1">
        <span className="text-ink-muted text-xs font-mono uppercase tracking-wide">Grade</span>
        <span className="font-display font-bold text-lg" style={{ color }}>{grade}</span>
      </div>
    </div>
  );
}
