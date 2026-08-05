interface MetricCardProps {
  label: string;
  value: string;
  hint: string;
  tone?: "cyan" | "violet" | "amber" | "green";
}

export function MetricCard({ label, value, hint, tone = "cyan" }: MetricCardProps) {
  return (
    <article className={`metric-card metric-${tone}`}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      <div className="metric-hint">{hint}</div>
    </article>
  );
}
