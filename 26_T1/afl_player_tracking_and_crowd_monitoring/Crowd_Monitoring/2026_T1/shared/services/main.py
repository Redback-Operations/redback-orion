"""FastAPI entry point for the shared service layer."""

from pathlib import Path

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .routes import router

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

app = FastAPI(
    title="Crowd Monitoring Services",
    description="Crowd monitoring APIs and demo UI.\n\n[Open Demo Page](/demo)",
    docs_url="/",
    redoc_url="/redoc",
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return actual runtime errors as JSON instead of generic 500 pages."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "path": request.url.path,
        },
    )


app.mount("/artifacts", StaticFiles(directory=PROJECT_ROOT), name="artifacts")


@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    """Simple demo UI for the crowd monitoring pipeline."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Crowd Monitoring Demo</title>
  <style>
    :root {
      --bg: #eef2e2;
      --panel: #fffdf7;
      --ink: #182018;
      --muted: #5f6d5f;
      --accent: #1e6f50;
      --accent-2: #d97a2b;
      --line: #d7dfc7;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top right, rgba(217,122,43,0.18), transparent 22rem),
        radial-gradient(circle at left center, rgba(30,111,80,0.18), transparent 18rem),
        var(--bg);
    }
    .wrap {
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }
    .hero {
      display: grid;
      gap: 12px;
      margin-bottom: 24px;
    }
    h1 {
      margin: 0;
      font-size: clamp(2rem, 4vw, 3.6rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
    }
    .hero p {
      margin: 0;
      max-width: 760px;
      color: var(--muted);
      font-size: 1rem;
    }
    .hero a {
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 18px 40px rgba(24,32,24,0.08);
    }
    .form-panel {
      padding: 18px;
      margin-bottom: 20px;
    }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      align-items: end;
    }
    label {
      display: grid;
      gap: 6px;
      font-size: 0.92rem;
      color: var(--muted);
    }
    input {
      width: 100%;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
    }
    button {
      padding: 12px 18px;
      border: 0;
      border-radius: 999px;
      background: var(--accent);
      color: white;
      font-weight: 700;
      cursor: pointer;
    }
    button:disabled {
      opacity: 0.6;
      cursor: wait;
    }
    .status {
      margin-top: 12px;
      min-height: 24px;
      color: var(--muted);
      font-size: 0.95rem;
    }
    .error {
      color: #a22b2b;
    }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-bottom: 20px;
    }
    .card {
      padding: 16px;
    }
    .eyebrow {
      color: var(--muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }
    .value {
      font-size: 1.8rem;
      font-weight: 700;
    }
    .subvalue {
      margin-top: 6px;
      color: var(--muted);
      font-size: 0.92rem;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }
    .visual {
      padding: 16px;
    }
    .visual img {
      width: 100%;
      height: auto;
      display: block;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: #f6f7f0;
    }
    .visual h2 {
      margin: 0 0 12px;
      font-size: 1.05rem;
    }
    .empty {
      padding: 20px;
      border: 1px dashed var(--line);
      border-radius: 12px;
      color: var(--muted);
      text-align: center;
    }
    .hidden { display: none; }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>Crowd Monitoring Demo</h1>
      <p>Run the full crowd pipeline and preview the key outputs without working through Swagger. Swagger remains available at <a href="/">/</a>.</p>
    </section>

    <section class="panel form-panel">
      <div class="form-grid">
        <label>
          Video ID
          <input id="videoId" value="match_02" />
        </label>
        <label>
          Video Path
          <input id="videoPath" value="data/raw/match_02.mp4" />
        </label>
        <button id="runBtn" type="button">Run Demo</button>
      </div>
      <div id="status" class="status"></div>
    </section>

    <section id="results" class="hidden">
      <div class="cards">
        <div class="panel card">
          <div class="eyebrow">Peak Crowd</div>
          <div id="peakCount" class="value">-</div>
          <div id="peakMeta" class="subvalue"></div>
        </div>
        <div class="panel card">
          <div class="eyebrow">Crowd State</div>
          <div id="crowdState" class="value">-</div>
          <div id="processedFrames" class="subvalue"></div>
        </div>
        <div class="panel card">
          <div class="eyebrow">Highest Density Zone</div>
          <div id="highZone" class="value">-</div>
          <div id="highZoneMeta" class="subvalue"></div>
        </div>
        <div class="panel card">
          <div class="eyebrow">Lowest Density Zone</div>
          <div id="lowZone" class="value">-</div>
          <div id="lowZoneMeta" class="subvalue"></div>
        </div>
      </div>

      <div class="grid">
        <div class="panel visual">
          <h2>Peak Crowd Frame</h2>
          <img id="peakFrame" alt="Peak crowd frame" />
        </div>
        <div class="panel visual">
          <h2>Anomaly / Movement Visual</h2>
          <img id="anomalyFrame" alt="Anomaly visual" />
        </div>
        <div class="panel visual">
          <h2>Heatmap</h2>
          <img id="heatmap" alt="Heatmap" />
        </div>
        <div class="panel visual">
          <h2>Person Count Over Time</h2>
          <img id="chart" alt="Person count chart" />
        </div>
      </div>
    </section>
  </div>

  <script>
    const runBtn = document.getElementById("runBtn");
    const statusEl = document.getElementById("status");
    const resultsEl = document.getElementById("results");

    function artifactUrl(path) {
      return path ? `/artifacts/${path}` : "";
    }

    function setImage(id, path) {
      const image = document.getElementById(id);
      if (path) {
        image.src = artifactUrl(path);
        image.classList.remove("hidden");
      } else {
        image.removeAttribute("src");
        image.classList.add("hidden");
      }
    }

    function zoneText(zone) {
      if (!zone || !zone.zone_id) return ["-", ""];
      return [
        zone.zone_id,
        `Density ${zone.density ?? "-"} | Count ${zone.person_count ?? "-"} | Risk ${zone.risk_level ?? "-"}`
      ];
    }

    async function runDemo() {
      runBtn.disabled = true;
      statusEl.className = "status";
      statusEl.textContent = "Running crowd monitoring pipeline...";
      resultsEl.classList.add("hidden");

      try {
        const response = await fetch("/process-crowd-detection", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            video_id: document.getElementById("videoId").value.trim(),
            video_path: document.getElementById("videoPath").value.trim()
          })
        });

        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.detail || JSON.stringify(payload));
        }

        const summary = payload.summary || {};
        const peakFrame = payload.peak_crowd_frame || {};
        const densityExtremes = payload.density_extremes || {};
        const [highZone, highZoneMeta] = zoneText(densityExtremes.highest_density_zone);
        const [lowZone, lowZoneMeta] = zoneText(densityExtremes.lowest_density_zone);

        document.getElementById("peakCount").textContent = peakFrame.person_count ?? summary.peak_person_count ?? "-";
        document.getElementById("peakMeta").textContent = peakFrame.timestamp != null ? `Frame ${peakFrame.frame_id} at ${peakFrame.timestamp}s` : "";
        document.getElementById("crowdState").textContent = summary.crowd_state || "-";
        document.getElementById("processedFrames").textContent = `${summary.total_frames_processed ?? 0} frames processed`;
        document.getElementById("highZone").textContent = highZone;
        document.getElementById("highZoneMeta").textContent = highZoneMeta;
        document.getElementById("lowZone").textContent = lowZone;
        document.getElementById("lowZoneMeta").textContent = lowZoneMeta;

        setImage("peakFrame", peakFrame.annotated_frame_path);
        setImage("anomalyFrame", (payload.anomaly_visual || {}).image_path);
        setImage("heatmap", (payload.heatmap || {}).image_path);
        setImage("chart", (payload.time_series_chart || {}).image_path);

        resultsEl.classList.remove("hidden");
        statusEl.textContent = "Completed.";
      } catch (error) {
        statusEl.className = "status error";
        statusEl.textContent = error.message;
      } finally {
        runBtn.disabled = false;
      }
    }

    runBtn.addEventListener("click", runDemo);
  </script>
</body>
</html>
"""


app.include_router(router)
