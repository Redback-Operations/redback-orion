export default function ErrorPage() {
  return (
    <section>
      <h3>Error</h3>
      <div
        style={{
          padding: 16,
          borderRadius: 12,
          background: "#fff5f5",
          border: "1px solid #ffd6d6",
          maxWidth: 480,
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: 8 }}>
          Something went wrong
        </div>
        <div style={{ color: "#b00020", marginBottom: 12 }}>
          Couldn’t load the stream. Please try again.
        </div>
        <button
          onClick={() => location.reload()}
          style={{ padding: "8px 12px", borderRadius: 8 }}
        >
          Retry
        </button>
      </div>
    </section>
  );
}
