import {useEffect, useMemo, useRef, useState} from "react";
import {motion} from "framer-motion";
import {Upload, Pause, Play, RotateCcw} from "lucide-react";
import "./fatigue.css";

/**
 * Upload JSON format (first frame should include full player profile fields):
 * {
 *   "frames":[
 *     {
 *       "t":"2025-01-10T08:30:00Z",
 *       "quarter":1,
 *       "players":[
 *         {
 *           "jersey":19, "name":"Rowan Marshall", "team":"St Kilda Football Club",
 *           "pos":"Ruck", "age":29, "height_cm":201, "weight_kg":105, "img":"",
 *           "fatigue":0.18, "speed_mps":7.8, "distance_m":22, "hr":138
 *         },
 *         ...
 *       ]
 *     },
 *     // later frames may omit static profile fields; the component persists them.
 *   ]
 * }
 */

function SparkLine({values = [], width = 120, height = 30}) {
  if (!values.length) return null;
  const max = Math.max(...values, 1);
  const step = width / Math.max(values.length - 1, 1);
  const pts = values
    .map((v, i) => `${i * step},${height - (v / max) * height}`)
    .join(" L ");
  return (
    <svg width={width} height={height} className="spark">
      <polyline points={`0,${height} ${pts} ${width},${height}`} className="spark-fill"/>
      <polyline points={pts} className="spark-line"/>
    </svg>
  );
}

function FatigueBar({value}) {
  const pct = Math.round((value ?? 0) * 100);
  return (
    <div className="fatigue-bar">
      <motion.div
        className={`fatigue-fill ${pct < 50 ? "ok" : pct < 75 ? "warn" : "bad"}`}
        initial={{width: 0}}
        animate={{width: `${pct}%`}}
        transition={{type: "spring", stiffness: 120, damping: 20}}
      />
      <span className="fatigue-label">{pct}%</span>
    </div>
  );
}

function MetricChip({label, value}) {
  return (
    <div className="chip">
      <span className="chip-label">{label}</span>
      <span className="chip-value">{value}</span>
    </div>
  );
}

function PlayerFatigueCard({p, trend = []}) {
  const pct = Math.round((p.fatigue ?? 0) * 100);
  return (
    <div className="player-card fatigue">
      <div className="player-head">
        <img
          src={p.img || "https://i.pravatar.cc/80?img=15"}
          alt={p.name || "Player"}
          className="avatar"
        />
        <div className="id">
          <div className="name">
            {p.name || "Unknown"} <span className="jersey">#{p.jersey ?? "--"}</span>
          </div>
          <div className="meta">
            Age: {p.age ?? "—"} • Height: {p.height_cm ?? "—"} cm • Weight:{" "}
            {p.weight_kg ?? "—"} kg • Position: {p.pos ?? "—"} • Team: {p.team ?? "—"}
          </div>
        </div>
        <div className={`badge ${pct < 50 ? "ok" : pct < 75 ? "warn" : "bad"}`}>
          Fatigue {pct}%
        </div>
      </div>

      <FatigueBar value={p.fatigue ?? 0} />

      <div className="metrics">
        <MetricChip
          label="Speed drop"
          value={`${Math.max(
            0,
            Math.round((1 - (p.speed_mps ?? 0) / (p.baseline_speed_mps || 7.5)) * 100)
          )}%`}
        />
        <MetricChip
          label="Distance (km)"
          value={`${((p.total_distance_m ?? 0) / 1000).toFixed(2)}`}
        />
        <MetricChip label="HR" value={`${p.hr ?? 0} bpm`} />
        <MetricChip label="Quarter" value={p.quarter ?? "-"} />
      </div>

      <div className="trend">
        <SparkLine values={trend} />
      </div>
    </div>
  );
}

export default function FatigueLivePanel() {
  const [frames, setFrames] = useState([]);
  const [idx, setIdx] = useState(0);
  const [paused, setPaused] = useState(false);
  const [speed, setSpeed] = useState(600);
  const timer = useRef(null);

  const currentFrame = frames[idx] || null;

  // Build history + keep static profiles so they’re always visible
  const history = useMemo(() => {
    const map = new Map(); // jersey -> {trend:[], total_distance_m, baseline_speed_mps, profile:{}}
    frames.forEach((f) => {
      (f.players || []).forEach((p) => {
        const entry = map.get(p.jersey) || {
          trend: [],
          total_distance_m: 0,
          baseline_speed_mps: p.speed_mps || 7.5,
          profile: {
            jersey: p.jersey,
            name: p.name,
            team: p.team,
            pos: p.pos,
            age: p.age,
            height_cm: p.height_cm,
            weight_kg: p.weight_kg,
            img: p.img
          }
        };
        // keep first non-empty values
        entry.profile = {
          ...entry.profile,
          ...(p.name ? {name: p.name} : {}),
          ...(p.team ? {team: p.team} : {}),
          ...(p.pos ? {pos: p.pos} : {}),
          ...(p.age ? {age: p.age} : {}),
          ...(p.height_cm ? {height_cm: p.height_cm} : {}),
          ...(p.weight_kg ? {weight_kg: p.weight_kg} : {}),
          ...(p.img ? {img: p.img} : {})
        };
        entry.trend.push((p.fatigue ?? 0) * 100);
        entry.total_distance_m += p.distance_m || 0;
        // baseline from first seen speed if not set
        if (!entry.baseline_speed_mps && p.speed_mps) entry.baseline_speed_mps = p.speed_mps;
        map.set(p.jersey, entry);
      });
    });
    return map;
  }, [frames]);

  // advance frames
  useEffect(() => {
    if (!frames.length || paused) return;
    timer.current = setInterval(() => {
      setIdx((i) => (i + 1 >= frames.length ? i : i + 1));
    }, Math.max(120, speed));
    return () => clearInterval(timer.current);
  }, [frames, paused, speed]);

  const mergeProfilesIntoFrames = (rawFrames) => {
    // collect most complete profile per jersey
    const profile = new Map();
    rawFrames.forEach((f) =>
      (f.players || []).forEach((p) => {
        const prev = profile.get(p.jersey) || {};
        profile.set(p.jersey, {...prev, ...p});
      })
    );
    // enrich each frame’s players with persisted static fields
    return rawFrames.map((f) => ({
      ...f,
      players: (f.players || []).map((p) => {
        const base = profile.get(p.jersey) || {};
        return {
          // static
          jersey: p.jersey ?? base.jersey,
          name: base.name,
          team: base.team,
          pos: base.pos,
          age: base.age,
          height_cm: base.height_cm,
          weight_kg: base.weight_kg,
          img: base.img,
          // dynamic
          fatigue: p.fatigue,
          speed_mps: p.speed_mps,
          distance_m: p.distance_m,
          hr: p.hr,
          quarter: f.quarter ?? p.quarter
        };
      })
    }));
  };

  const onUpload = async (file) => {
    if (!file) return;
    try {
      const text = await file.text();
      const json = JSON.parse(text);
      const sanitized = (json.frames || []).map((f) => ({
        t: f.t,
        quarter: f.quarter ?? 1,
        players: (f.players || []).map((p) => ({
          ...p,
          fatigue: Math.min(1, Math.max(0, p.fatigue ?? 0))
        }))
      }));
      const enriched = mergeProfilesIntoFrames(sanitized);
      setFrames(enriched);
      setIdx(0);
      setPaused(false);
    } catch (e) {
      console.error(`Bad JSON: ${e.message}`, e);
      alert(
        `Invalid JSON: ${e.message}\n\nExpected format:\n{\n  "frames": [\n    {\n      "t": "2025-01-10T08:30:00Z",\n      "quarter": 1,\n      "players": [\n        {\n          "jersey": 19,\n          "name": "Rowan Marshall",\n          "team": "St Kilda Football Club",\n          "pos": "Ruck",\n          "age": 29,\n          "height_cm": 201,\n          "weight_kg": 105,\n          "img": "",\n          "fatigue": 0.18,\n          "speed_mps": 7.8,\n          "distance_m": 22,\n          "hr": 138\n        }\n      ]\n    }\n  ]\n}`
      );
    }
  };

  const fileInputRef = useRef(null);

  return (
    <section className="tracking-section">
      <div className="section-header">
        <h3>Live Player Fatigue</h3>
        <div className="fatigue-controls">
          <button className="btn action-btn" onClick={() => fileInputRef.current?.click()}>
            <Upload size={16}/> Upload JSON
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/json"
            className="hidden-input"
            onChange={(e) => onUpload(e.target.files?.[0])}
          />
          <button className="btn icon-btn" onClick={() => setPaused((p) => !p)} title={paused ? "Play" : "Pause"}>
            {paused ? <Play size={16}/> : <Pause size={16}/>}
          </button>
          <button className="btn icon-btn" onClick={() => setIdx(0)} title="Reset">
            <RotateCcw size={16}/>
          </button>
          <div className="speed">
            <label>Speed</label>
            <input
              className="range"
              type="range"
              min={150}
              max={1200}
              step={50}
              value={speed}
              onChange={(e) => setSpeed(Number(e.target.value))}
            />
            <span>{speed}ms</span>
          </div>
          <div className="progress-info">
            Frame {Math.min(idx + 1, frames.length) || 0} / {frames.length || 0}
          </div>
        </div>
      </div>

      <div className="tracking-content">
        <div className="player-info-cards">
          {!frames.length && (
            <div className="player-card hint">
              <p>Upload a JSON file to start the live fatigue view.</p>    
              <p style={{opacity: .75, marginTop: 6}}>
              Use <code>public/demo/fatigue-sample.json</code>
                </p>
            </div>
          )}

          {currentFrame?.players?.map((p) => {
            const hist = history.get(p.jersey);
            const enriched = {
              ...p,
              total_distance_m: hist?.total_distance_m || 0,
              baseline_speed_mps: hist?.baseline_speed_mps || 7.5,
              quarter: currentFrame.quarter
            };
            return (
              <PlayerFatigueCard
                key={p.jersey}
                p={enriched}
                trend={hist?.trend?.slice(Math.max(0, idx - 20), idx + 1) || []}
              />
            );
          })}
        </div>
      </div>
    </section>
  );
}
