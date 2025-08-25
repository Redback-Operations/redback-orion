import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

export default function QuarterFatigueBars({ q1 = 0, q2 = 0, q3 = 0, q4 = 0 }) {
  const data = [
    { q: "Q1", v: q1 },
    { q: "Q2", v: q2 },
    { q: "Q3", v: q3 },
    { q: "Q4", v: q4 },
  ];
  return (
    <div style={{ width: "100%", height: 220 }}>
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="q" />
          <YAxis domain={[0, 1]} ticks={[0, 0.25, 0.5, 0.75, 1]} />
          <Tooltip formatter={(val) => (val * 100).toFixed(0) + "%"} />
          <Bar dataKey="v" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
