export default function ScreenError({
  title = "Something went wrong",
  message = "Please try again.",
  onRetry
}) {
  return (
    <div style={{
      padding: 16,
      border: "1px solid #fee2e2",
      background: "#fef2f2",
      color: "#991b1b",
      borderRadius: 10
    }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{title}</div>
      <div style={{ fontSize: 14, marginBottom: 8 }}>{message}</div>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            padding: "6px 10px",
            background: "#991b1b",
            color: "#fff",
            border: 0,
            borderRadius: 8,
            cursor: "pointer"
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
}
