import { useEffect, useMemo, useRef, useState } from "react";
import FatigueBar from "../components/FatigueBar";
import PlayerHeaderPro from "../components/PlayerHeaderPro";

export default function RealtimeFCarouselPage() {
  // Array of { player: {...}, stream: [...] }
  const [packs, setPacks] = useState([]);
  const [active, setActive] = useState(0); // which player is visible
  const [idx, setIdx] = useState([]); // per-player frame index
  const [playing, setPlaying] = useState(false);
  const [speedMs, setSpeedMs] = useState(400);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);

  // Current selection helpers
  const curPack = packs[active] || null;
  const frames = curPack?.stream || [];
  const curFrame = frames[idx[active] ?? 0] || null;
  const curFatigue = curFrame?.fatigue ?? 0;

  // Upload multi-player JSON
  function handleUpload(ev) {
    const f = ev.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const obj = JSON.parse(String(reader.result));
        if (!Array.isArray(obj.players))
          throw new Error("Invalid JSON: expected a 'players' array.");
        // Basic normalize
        const normalized = obj.players.map((p) => ({
          player: p.player || {},
          stream: Array.isArray(p.stream) ? p.stream : [],
        }));
        setPacks(normalized);
        setIdx(new Array(normalized.length).fill(0));
        setActive(0);
        setError(null);
      } catch (e) {
        setError(e.message || "Failed to parse file.");
      }
    };
    reader.onerror = () => setError("Failed to read file.");
    reader.readAsText(f);
  }

  // Tick all players in the background, so switching views keeps them in sync
  useEffect(() => {
    if (!playing || packs.length === 0) return;
    clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setIdx((old) =>
        old.map((i, k) => {
          const total = packs[k].stream.length;
          return total ? Math.min(i + 1, total - 1) : 0;
        })
      );
    }, speedMs);
    return () => clearInterval(timerRef.current);
  }, [playing, packs, speedMs]);

  function resetAll() {
    setIdx(new Array(packs.length).fill(0));
  }

  function prevPlayer() {
    if (!packs.length) return;
    setActive((a) => (a - 1 + packs.length) % packs.length);
  }

  function nextPlayer() {
    if (!packs.length) return;
    setActive((a) => (a + 1) % packs.length);
  }

  // Progress readout for the active player
  const progress = useMemo(() => {
    const i = idx[active] ?? 0;
    const n = frames.length || 0;
    const pct = n ? Math.round(((i + 1) / n) * 100) : 0;
    return { i: i + 1, n, pct };
  }, [idx, active, frames.length]);

  return (
    <div style={{ display: "grid", gap: 16, maxWidth: 960 }}>
      <h3>Realtime Fatigue — Carousel (Multi-player)</h3>

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
          Upload multi-player JSON
          <input
            type="file"
            accept=".json"
            onChange={handleUpload}
            style={{ display: "none" }}
          />
        </label>

        <button
          onClick={() => setPlaying((p) => !p)}
          disabled={!packs.length}
          style={{
            padding: "6px 10px",
            borderRadius: 8,
            border: "1px solid #ddd",
          }}
        >
          {playing ? "Pause" : "Play"}
        </button>

        <button
          onClick={resetAll}
          disabled={!packs.length}
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
          <span style={{ width: 48, textAlign: "right", fontSize: 12 }}>
            {speedMs}ms
          </span>
        </div>

        {packs.length > 0 && (
          <div style={{ fontSize: 12, color: "#555" }}>
            Frame {progress.i} / {progress.n} • {progress.pct}%
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

      {/* Carousel header */}
      {packs.length > 1 && (
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <button
            onClick={prevPlayer}
            style={{
              padding: "6px 10px",
              borderRadius: 8,
              border: "1px solid #ddd",
            }}
          >
            ‹ Prev
          </button>
          <div style={{ display: "flex", gap: 6 }}>
            {packs.map((_, i) => (
              <span
                key={i}
                title={`Player ${i + 1}`}
                onClick={() => setActive(i)}
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: "50%",
                  background: i === active ? "#111" : "#ccc",
                  cursor: "pointer",
                }}
              />
            ))}
          </div>
          <button
            onClick={nextPlayer}
            style={{
              padding: "6px 10px",
              borderRadius: 8,
              border: "1px solid #ddd",
            }}
          >
            Next ›
          </button>
        </div>
      )}

      {/* Player card */}
      <PlayerHeaderPro player={curPack?.player} />

      {/* Current fatigue only (no quarter bars) */}
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
            {curFrame
              ? `Quarter: Q${curFrame.quarter} • ${new Date(
                  curFrame.ts
                ).toLocaleTimeString()}`
              : "No frame loaded"}
          </div>
        </div>
        <FatigueBar value={curFatigue} />
        <div style={{ fontSize: 12, color: "#555" }}>
          Value: {(curFatigue * 100).toFixed(0)}%
        </div>
      </div>

      {/* Helper state */}
      {!packs.length && (
        <div
          style={{
            padding: 16,
            border: "1px dashed #ddd",
            borderRadius: 12,
            color: "#555",
          }}
        >
          Upload a <code>.json</code> file with a <code>players</code> array.
          Select a player with the carousel dots.
        </div>
      )}
    </div>
  );
}
