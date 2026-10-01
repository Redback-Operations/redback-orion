export default function ScreenLoader({ label = "Loading…" }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "12px 16px",
        border: "1px solid #eee",
        borderRadius: 10,
        background: "#fff",
        boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
      }}
    >
      <span
        style={{
          width: 16,
          height: 16,
          borderRadius: "50%",
          border: "2px solid #ddd",
          borderTopColor: "#3b82f6",
          animation: "spin 0.8s linear infinite",
        }}
      />
      <span style={{ fontSize: 14, color: "#374151" }}>{label}</span>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </div>
  );
}
