export default function PlayerHeader({ player }) {
  if (!player) return null;
  const { photoUrl, jerseyNumber, name, age, position, team } = player;

  return (
    <div
      style={{
        display: "flex",
        gap: 16,
        alignItems: "center",
        padding: 12,
        border: "1px solid #eee",
        borderRadius: 12,
      }}
    >
      {photoUrl ? (
        <img
          src={photoUrl}
          alt={`${name} headshot`}
          width={80}
          height={80}
          style={{ borderRadius: "50%", objectFit: "cover" }}
        />
      ) : (
        <div
          style={{
            width: 80,
            height: 80,
            borderRadius: "50%",
            display: "grid",
            placeItems: "center",
            background: "#f0f0f0",
            fontWeight: 700,
          }}
        >
          #{jerseyNumber ?? "?"}
        </div>
      )}

      <div style={{ display: "grid", gap: 4 }}>
        <div style={{ fontWeight: 700, fontSize: 18 }}>
          {name ?? "Unknown"}{" "}
          {typeof jerseyNumber !== "undefined" && (
            <span style={{ color: "#666" }}>(#{jerseyNumber})</span>
          )}
        </div>
        <div style={{ fontSize: 13, color: "#555" }}>
          {age ? `Age: ${age} • ` : ""}
          {position ? `Position: ${position} • ` : ""}
          {team ? `Team: ${team}` : ""}
        </div>
      </div>
    </div>
  );
}
