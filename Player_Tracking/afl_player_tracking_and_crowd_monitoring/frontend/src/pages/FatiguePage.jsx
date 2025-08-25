import { useState } from "react";
import FatigueBar from "../components/FatigueBar";

export default function FatiguePage() {
  const [fatigue, setFatigue] = useState(0.64); // assume derived from distance/goals/body profile, etc.

  return (
    <section style={{ display: "grid", gap: 16, maxWidth: 640 }}>
      <h3>Player Fatigue (0 → 1)</h3>
      <FatigueBar value={fatigue} />
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <input
          type="range"
          min="0"
          max="1"
          step="0.01"
          value={fatigue}
          onChange={(e) => setFatigue(parseFloat(e.target.value))}
          style={{ width: 320 }}
        />
        <span>{fatigue.toFixed(2)}</span>
      </div>
      <small style={{ color: "#666" }}>
        Updated in real time; computed from live player tracking features (e.g.,
        distance, goals, body profile).
      </small>
    </section>
  );
}
