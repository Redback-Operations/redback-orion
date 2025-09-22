import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

export interface UploadMeta {
  id: string;
  original_filename: string;
  created_at: string;
}

function getAuthToken() {
  return (
    localStorage.getItem("token") ||
    localStorage.getItem("authToken") ||
    localStorage.getItem("access_token") ||
    ""
  );
}

async function fetchImageBytes(url: string): Promise<Uint8Array | null> {
  try {
    const headers: Record<string, string> = {};
    const token = getAuthToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(url, { headers });
    if (!res.ok) return null;
    const buf = await res.arrayBuffer();
    return new Uint8Array(buf);
  } catch {
    return null;
  }
}

function wrapText(text: string, maxWidth: number, font: any, size: number) {
  const words = String(text).split(/\s+/);
  const lines: string[] = [];
  let line = "";
  for (const w of words) {
    const test = line ? line + " " + w : w;
    const width = font.widthOfTextAtSize(test, size);
    if (width > maxWidth && line) {
      lines.push(line);
      line = w;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
}

export async function buildAnalysisPdf(params: {
  title: string;
  upload: UploadMeta;
  section: string;
  data: any;
}): Promise<Blob> {
  const { title, upload, section, data } = params;
  const pdf = await PDFDocument.create();
  pdf.setTitle(title);
  pdf.setSubject(section);
  pdf.setAuthor("AFL Analytics");

  const font = await pdf.embedFont(StandardFonts.Helvetica);
  const fontBold = await pdf.embedFont(StandardFonts.HelveticaBold);

  let page = pdf.addPage();
  let { width, height } = page.getSize();
  const margin = 40;
  const contentWidth = width - margin * 2;
  let y = height - margin;

  const addPageIfNeeded = (needed: number) => {
    if (y - needed < margin) {
      page = pdf.addPage();
      ({ width, height } = page.getSize());
      y = height - margin;
    }
  };

  const drawLine = (t: string, f: any, size: number, color = rgb(0, 0, 0)) => {
    const lines = wrapText(t, contentWidth, f, size);
    for (const ln of lines) {
      addPageIfNeeded(size + 6);
      page.drawText(ln, { x: margin, y, size, font: f, color });
      y -= size + 4;
    }
  };

  const drawRule = () => {
    addPageIfNeeded(12);
    page.drawLine({ start: { x: margin, y }, end: { x: width - margin, y }, thickness: 1, color: rgb(0.88, 0.88, 0.9) });
    y -= 12;
  };

  const drawImageUrl = async (url?: string | null, maxW = contentWidth) => {
    if (!url) return;
    const bytes = await fetchImageBytes(url);
    if (!bytes) return;
    let img: any = null;
    try { img = await pdf.embedPng(bytes); } catch {}
    if (!img) {
      try { img = await pdf.embedJpg(bytes); } catch {}
    }
    if (!img) return;
    const imgW = img.width;
    const imgH = img.height;
    const scale = Math.min(maxW / imgW, 260 / imgH, 1);
    const wScaled = imgW * scale;
    const hScaled = imgH * scale;
    addPageIfNeeded(hScaled + 6);
    page.drawImage(img, { x: margin, y: y - hScaled, width: wScaled, height: hScaled });
    y -= hScaled + 6;
  };

  const drawTable = (headers: string[], rows: (string | number)[][]) => {
    const colCount = headers.length;
    const colW = contentWidth / colCount;
    const rowH = 18;

    const drawRow = (cells: (string | number)[], bold = false, bg?: boolean) => {
      addPageIfNeeded(rowH + 4);
      if (bg) {
        page.drawRectangle({ x: margin, y: y - rowH + 4, width: contentWidth, height: rowH, color: rgb(0.97, 0.97, 0.99) });
      }
      for (let i = 0; i < colCount; i++) {
        const text = String(cells[i] ?? "");
        const f = bold ? fontBold : font;
        page.drawText(text, { x: margin + i * colW + 4, y: y, size: 10, font: f, color: rgb(0.1, 0.1, 0.12) });
      }
      y -= rowH;
    };

    drawRow(headers, true, true);
    rows.forEach((r, idx) => drawRow(r, false, idx % 2 === 0));
    y -= 6;
  };

  // Header
  drawLine(title, fontBold, 20);
  const createdAt = upload.created_at ? new Date(upload.created_at).toLocaleString() : "";
  drawLine(`Upload: ${upload.original_filename} • Created: ${createdAt}`, font, 10, rgb(0.35, 0.35, 0.35));
  drawRule();
  drawLine(section, fontBold, 14);

  // Player dashboard report
  if (data && Array.isArray(data.players)) {
    // Team heatmaps
    if (data.team) {
      drawLine("Team Heatmap", fontBold, 12);
      await drawImageUrl(data.team.team_heatmap_url);
      drawLine("Zone Heatmaps", fontBold, 12);
      await drawImageUrl(data.team.zones?.back_50);
      await drawImageUrl(data.team.zones?.midfield);
      await drawImageUrl(data.team.zones?.forward_50);
      drawRule();
    }

    // Player stats table
    drawLine("Player Statistics", fontBold, 12);
    const rows = data.players.map((p: any) => [
      p.player_id,
      typeof p.distance_m === "number" ? p.distance_m.toFixed(1) : String(p.distance_m ?? ""),
      typeof p.avg_speed_kmh === "number" ? p.avg_speed_kmh.toFixed(2) : String(p.avg_speed_kmh ?? ""),
      typeof p.max_speed_kmh === "number" ? p.max_speed_kmh.toFixed(2) : String(p.max_speed_kmh ?? ""),
    ]);
    drawTable(["Player", "Distance (m)", "Avg Speed (km/h)", "Max Speed (km/h)"], rows);

    // Player heatmap thumbnails (first 6)
    const thumbs = (data.players || []).slice(0, 6).map((p: any) => p.heatmap_url).filter(Boolean);
    if (thumbs.length) {
      drawLine("Player Heatmaps", fontBold, 12);
      const cols = 2;
      const gap = 12;
      const cellW = (contentWidth - gap) / cols;
      for (let i = 0; i < thumbs.length; i++) {
        const url = thumbs[i];
        const bytes = await fetchImageBytes(url);
        if (!bytes) continue;
        let img: any = null;
        try { img = await pdf.embedPng(bytes); } catch {}
        if (!img) { try { img = await pdf.embedJpg(bytes); } catch {} }
        if (!img) continue;
        const imgW = img.width;
        const imgH = img.height;
        const scale = Math.min(cellW / imgW, 220 / imgH, 1);
        const wScaled = imgW * scale;
        const hScaled = imgH * scale;
        if (i % cols === 0) addPageIfNeeded(hScaled + 10);
        const col = i % cols;
        const x = margin + col * (cellW + gap);
        const yTop = y - (i % cols === 0 ? 0 : 0);
        page.drawImage(img, { x, y: yTop - hScaled, width: wScaled, height: hScaled });
        if (col === cols - 1 || i === thumbs.length - 1) {
          y -= hScaled + 10;
        }
      }
    }
  } else if (data && (Array.isArray(data.results) || data.status)) {
    // Crowd report
    drawLine("Summary", fontBold, 12);
    if (typeof data.frames_detected !== "undefined") drawLine(`Frames detected: ${data.frames_detected}`, font, 10);
    if (typeof data.avg_count !== "undefined") drawLine(`Average count: ${data.avg_count}`, font, 10);
    if (typeof data.peak_count !== "undefined") drawLine(`Peak count: ${data.peak_count}`, font, 10);
    if (typeof data.min_count !== "undefined") drawLine(`Min count: ${data.min_count}`, font, 10);
    drawRule();

    const images: string[] = (data.results || []).map((r: any) => r.heatmap_url).filter(Boolean).slice(0, 8);
    if (images.length) {
      drawLine("Heatmaps", fontBold, 12);
      const cols = 2;
      const gap = 12;
      const cellW = (contentWidth - gap) / cols;
      for (let i = 0; i < images.length; i++) {
        const url = images[i];
        const bytes = await fetchImageBytes(url);
        if (!bytes) continue;
        let img: any = null;
        try { img = await pdf.embedPng(bytes); } catch {}
        if (!img) { try { img = await pdf.embedJpg(bytes); } catch {} }
        if (!img) continue;
        const imgW = img.width;
        const imgH = img.height;
        const scale = Math.min(cellW / imgW, 230 / imgH, 1);
        const wScaled = imgW * scale;
        const hScaled = imgH * scale;
        if (i % cols === 0) addPageIfNeeded(hScaled + 10);
        const col = i % cols;
        const x = margin + col * (cellW + gap);
        page.drawImage(img, { x, y: y - hScaled, width: wScaled, height: hScaled });
        if (col === cols - 1 || i === images.length - 1) {
          y -= hScaled + 10;
        }
      }
    }
  } else {
    // Fallback: pretty print JSON
    const body = data ? JSON.stringify(data, null, 2) : "Not available";
    const paragraphs = body.split("\n");
    for (const p of paragraphs) drawLine(p, font, 10);
  }

  const bytes = await pdf.save();
  return new Blob([bytes], { type: "application/pdf" });
}
