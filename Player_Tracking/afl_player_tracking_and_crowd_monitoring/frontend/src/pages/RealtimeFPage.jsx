import { useEffect, useMemo, useRef, useState } from "react";
import PlayerHeader from "../components/PlayerHeader";
import FatigueBar from "../components/FatigueBar";
import QuarterFatigueBars from "../components/QuarterFatigueBars";

export default function RealtimeFPage() {
  const [player, setPlayer] = useState(null);
  const [stream, setStream] = useState([]); // frames
  const [idx, setIdx] = useState(0); // current frame index
  const [playing, setPlaying] = useState(false);
  const [speedMs, setSpeedMs] = useState(400); // playback speed (ms per frame)
  const timerRef = useRef(null);
  const [error, setError] = useState(null);

  const current = stream[idx] || null;
  const currentFatigue = current?.fatigue ?? 0;

  // running quarter averages up to current index
  const qAgg = useMemo(() => {
    const sums = { 1: 0, 2: 0, 3: 0, 4: 0 },
      counts = { 1: 0, 2: 0, 3: 0, 4: 0 };
    for (let i = 0; i <= idx && i < stream.length; i++) {
      const f = stream[i];
      if (!f || ![1, 2, 3, 4].includes(f.quarter)) continue;
      sums[f.quarter] += Number(f.fatigue) || 0;
      counts[f.quarter] += 1;
    }
    const avg = (q) => (counts[q] ? sums[q] / counts[q] : 0);
    return { q1: avg(1), q2: avg(2), q3: avg(3), q4: avg(4) };
  }, [idx, stream]);

  // playback effect
  useEffect(() => {
    if (!playing || stream.length === 0) return;
    clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setIdx((i) => (i + 1 < stream.length ? i + 1 : i)); // stop at end
    }, speedMs);
    return () => clearInterval(timerRef.current);
  }, [playing, stream.length, speedMs]);

  function handleUpload(ev) {
    const file = ev.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const obj = JSON.parse(String(reader.result));
        if (!obj || !Array.isArray(obj.stream))
          throw new Error("Invalid JSON: missing 'stream' array.");
        setPlayer(obj.player || null);
        setStream(obj.stream);
        setIdx(0);
        setError(null);
      } catch (e) {
        setError(e.message || "Failed to parse file.");
      }
    };
    reader.onerror = () => setError("Failed to read file.");
    reader.readAsText(file);
  }

  function resetPlayback() {
    setIdx(0);
  }

  const progressPct = stream.length
    ? Math.round(((idx + 1) / stream.length) * 100)
    : 0;

  return (
    <div style={{ display: "grid", gap: 16, maxWidth: 960 }}>
      <h3>Realtime Fatigue (Streamed)</h3>

      {/* Controls */}
      <div
        style={{
          display: "flex",
          gap: 12,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <label
          style={{
            border: "1px solid #ddd",
            padding: "6px 10px",
            borderRadius: 8,
            cursor: "pointer",
          }}
        >
          Upload dummy JSON
          <input
            type="file"
            accept=".json"
            onChange={handleUpload}
            style={{ display: "none" }}
          />
        </label>

        <button
          onClick={() => setPlaying((p) => !p)}
          disabled={stream.length === 0 || idx >= stream.length - 1}
          style={{
            padding: "6px 10px",
            borderRadius: 8,
            border: "1px solid #ddd",
          }}
        >
          {playing ? "Pause" : "Play"}
        </button>

        <button
          onClick={resetPlayback}
          disabled={stream.length === 0}
          style={{
            padding: "6px 10px",
            borderRadius: 8,
            border: "1px solid #ddd",
          }}
        >
          Reset
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 12, color: "#555" }}>Speed</span>
          <input
            type="range"
            min="100"
            max="1000"
            step="50"
            value={speedMs}
            onChange={(e) => setSpeedMs(parseInt(e.target.value, 10))}
          />
          <span style={{ width: 40, textAlign: "right", fontSize: 12 }}>
            {speedMs}ms
          </span>
        </div>

        {stream.length > 0 && (
          <div style={{ fontSize: 12, color: "#555" }}>
            Frame {idx + 1} / {stream.length} • {progressPct}%
          </div>
        )}
      </div>

      {error && (
        <div
          style={{
            padding: 12,
            borderRadius: 8,
            background: "#fff5f5",
            border: "1px solid #ffd6d6",
            color: "#b00020",
          }}
        >
          {error}
        </div>
      )}

      {/* Player card */}
      <PlayerHeader player={player} />

      {/* Current frame & fatigue */}
      <div
        style={{
          display: "grid",
          gap: 8,
          padding: 12,
          border: "1px solid #eee",
          borderRadius: 12,
        }}
      >
        <div
          style={{
            display: "flex",
            gap: 12,
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
          }}
        >
          <div style={{ fontWeight: 600 }}>Current Fatigue</div>
          <div style={{ fontSize: 12, color: "#555" }}>
            {current
              ? `Quarter: Q${current.quarter} • ${new Date(
                  current.ts
                ).toLocaleTimeString()}`
              : "No frame loaded"}
          </div>
        </div>
        <FatigueBar value={currentFatigue} />
        <div style={{ fontSize: 12, color: "#555" }}>
          Value: {(currentFatigue * 100).toFixed(0)}%
        </div>
      </div>

      {/* Quarter averages */}
      <div
        style={{
          display: "grid",
          gap: 8,
          padding: 12,
          border: "1px solid #eee",
          borderRadius: 12,
        }}
      >
        <div style={{ fontWeight: 600 }}>Quarter Averages (running)</div>
        <QuarterFatigueBars {...qAgg} />
      </div>

      {/* Helper: Empty state if nothing uploaded */}
      {!player && stream.length === 0 && (
        <div
          style={{
            padding: 16,
            border: "1px dashed #ddd",
            borderRadius: 12,
            color: "#555",
          }}
        >
          Upload a <code>.json</code> file with a <code>player</code> object and
          a <code>stream</code> array to start the realtime demo.
        </div>
      )}
    </div>
  );
}
