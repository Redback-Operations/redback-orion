export default function EmptyPage() {
  return (
    <section>
      <h3>No Data</h3>
      <div
        style={{
          padding: 16,
          border: "1px dashed #ddd",
          borderRadius: 12,
          maxWidth: 480,
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 6 }}>
          No data available
        </div>
        <div style={{ color: "#666" }}>
          Try changing filters, timeframe, or check the live feed.
        </div>
      </div>
    </section>
  );
}
