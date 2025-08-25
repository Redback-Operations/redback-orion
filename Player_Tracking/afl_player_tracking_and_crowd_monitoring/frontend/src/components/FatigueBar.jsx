export default function FatigueBar({ value }) {
  const v = Math.max(0, Math.min(1, Number(value) || 0));
  const hue = 120 - v * 120; // 0→1 maps green(120) to red(0)
  const color = `hsl(${hue}, 80%, 45%)`;

  return (
    <div
      style={{
        width: "100%",
        background: "#f1f1f1",
        borderRadius: 999,
        padding: 3,
      }}
    >
      <div
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(v * 100)}
        title={`Fatigue: ${(v * 100).toFixed(0)}%`}
        style={{
          width: `${v * 100}%`,
          height: 12,
          borderRadius: 999,
          background: color,
          transition: "width 250ms ease",
        }}
      />
    </div>
  );
}
