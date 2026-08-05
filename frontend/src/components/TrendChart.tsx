import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const data = [
  { sample: "09:00", qber: 2.1, fidelity: 98.4 }, { sample: "10:00", qber: 2.8, fidelity: 97.9 },
  { sample: "11:00", qber: 2.2, fidelity: 98.8 }, { sample: "12:00", qber: 3.4, fidelity: 97.2 },
  { sample: "13:00", qber: 2.5, fidelity: 98.1 }, { sample: "14:00", qber: 1.9, fidelity: 99.0 },
  { sample: "15:00", qber: 2.4, fidelity: 98.6 },
];

export function TrendChart() {
  return <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={data}><defs><linearGradient id="qber" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#22d3ee" stopOpacity={0.28} /><stop offset="100%" stopColor="#22d3ee" stopOpacity={0} /></linearGradient></defs><XAxis dataKey="sample" tickLine={false} axisLine={false} tick={{ fill: "#65758b", fontSize: 11 }} /><YAxis hide domain={[0, 5]} /><Tooltip contentStyle={{ background: "#111d2d", border: "1px solid #233955", borderRadius: 10 }} /><Area type="monotone" dataKey="qber" stroke="#22d3ee" fill="url(#qber)" strokeWidth={2} /></AreaChart></ResponsiveContainer></div>;
}
