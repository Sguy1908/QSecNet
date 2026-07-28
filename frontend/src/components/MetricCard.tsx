interface Props { label: string; value: string; detail?: string; }
export function MetricCard({ label, value, detail }: Props) {
  return <article className="card"><p>{label}</p><strong>{value}</strong>{detail && <small>{detail}</small>}</article>;
}
