// Pure helpers shared by the Video Analysis tab and the analysis dialog.

export const formatTimeAgo = (timestamp: string) => {
  const now = new Date();
  const time = new Date(timestamp);
  const diffMs = now.getTime() - time.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins} min ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
  return time.toLocaleDateString();
};

export const formatETA = (timestamp: string | null) => {
  if (!timestamp) return "Unknown";
  const now = new Date();
  const eta = new Date(timestamp);
  const diffMs = eta.getTime() - now.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 0) return "Overdue";
  if (diffMins < 60) return `${diffMins} min remaining`;
  const diffHours = Math.floor(diffMins / 60);
  return `${diffHours}h ${diffMins % 60}m remaining`;
};

// PDF generation for dashboard reports
export const generateDashboardPDF = (content: string, fileName: string) => {
  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    alert("Please allow popups to generate PDF reports");
    return;
  }

  const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <title>AFL Analytics Dashboard Report</title>
          <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 40px; line-height: 1.6; color: #333; }
            .header { text-align: center; border-bottom: 3px solid #059669; padding-bottom: 20px; margin-bottom: 30px; }
            .logo { color: #059669; font-size: 28px; font-weight: bold; margin-bottom: 5px; }
            .subtitle { color: #666; font-size: 14px; }
            h1 { color: #059669; font-size: 24px; margin: 30px 0 15px 0; }
            h2 { color: #2563eb; font-size: 18px; margin: 25px 0 10px 0; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; }
            .metric { background: #f0fdf4; padding: 10px; margin: 8px 0; border-left: 4px solid #059669; }
            .section { margin-bottom: 25px; }
            .player-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0; }
            .player-card { background: #f9fafb; padding: 12px; border-radius: 6px; border: 1px solid #e5e7eb; }
            .crowd-item { background: #ecfdf5; padding: 8px; margin: 4px 0; border-radius: 4px; }
            @media print { body { margin: 20px; } .no-print { display: none; } }
          </style>
        </head>
        <body>
          <div class="header">
            <div class="logo">AFL Analytics Dashboard</div>
            <div class="subtitle">Professional Sports Analytics Platform</div>
          </div>
          <div class="no-print" style="text-align: center; margin-bottom: 20px;">
            <button onclick="window.print()" style="background: #059669; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Generate PDF</button>
            <button onclick="window.close()" style="background: #6b7280; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-left: 10px;">Close</button>
          </div>
          ${content}
        </body>
      </html>
    `;

  printWindow.document.write(htmlContent);
  printWindow.document.close();
  setTimeout(() => printWindow.print(), 500);
};

// Generate detailed AFL video analysis insights
export const generateDashboardInsights = () => {
  const players = [
    "Marcus Bontempelli",
    "Patrick Cripps",
    "Clayton Oliver",
    "Lachie Neale",
    "Dustin Martin",
    "Jeremy Cameron",
    "Tom Hawkins",
    "Charlie Curnow",
    "Jack Steele",
    "Andrew Brayshaw",
    "Christian Petracca",
    "Max Gawn",
  ];

  const stadiumSections = [
    "MCC Members",
    "AFL Members",
    "Southern Stand",
    "Olympic Stand",
    "Ponsford Stand",
    "Great Southern Stand",
    "Premium Seating",
    "General Admission",
  ];

  const playerStats = players.slice(0, 6).map((player, index) => ({
    name: player,
    speed: (25 + Math.random() * 10).toFixed(1),
    goals: Math.floor(Math.random() * 4),
    tackles: Math.floor(Math.random() * 12 + 3),
    assists: Math.floor(Math.random() * 6),
    disposals: Math.floor(Math.random() * 25 + 12),
    marks: Math.floor(Math.random() * 10 + 2),
    efficiency: (65 + Math.random() * 30).toFixed(1),
    timeOnGround: Math.floor(Math.random() * 25 + 70),
  }));

  const crowdDensity = stadiumSections.slice(0, 6).map((section) => ({
    section,
    capacity: Math.floor(Math.random() * 6000 + 2000),
    attendance: Math.floor(Math.random() * 5500 + 1800),
    density: (75 + Math.random() * 20).toFixed(1),
    avgMovement: (6 + Math.random() * 12).toFixed(1),
    noiseLevel: (65 + Math.random() * 25).toFixed(1),
    peakMoments: Math.floor(Math.random() * 6 + 2),
  }));

  return { playerStats, crowdDensity };
};

// Convert backend JSON to formatted text
export const convertBackendDataToText = (data: any) => {
  return `AFL VIDEO ANALYSIS REPORT
Generated: ${new Date(data.timestamp).toLocaleString()}
Analysis ID: ${data.analysisId}

VIDEO INFORMATION
================
File: ${data.videoFile.name}
Duration: ${data.videoFile.duration}
Size: ${data.videoFile.size}
Resolution: ${data.videoFile.resolution}
Processing Time: ${data.processingTime} seconds

PLAYER PERFORMANCE
==================
${data.results.playerPerformance
  .map(
    (player: any) => `
${player.name} (${player.team} - ${player.position})
- Max Speed: ${player.statistics.speed.max} ${player.statistics.speed.unit}
- Average Speed: ${player.statistics.speed.average} ${player.statistics.speed.unit}
- Total Distance: ${player.statistics.distance.total} ${player.statistics.distance.unit}
- Goals: ${player.statistics.goals} | Assists: ${player.statistics.assists}
- Tackles: ${player.statistics.tackles} | Marks: ${player.statistics.marks}
- Disposals: ${player.statistics.disposals} | Efficiency: ${player.statistics.touches.efficiency}%
- Time on Ground: ${player.statistics.timeOnGround}%
`,
  )
  .join("\n")}

CROWD ANALYSIS
==============
Total Attendance: ${data.results.crowdAnalysis.totalAttendance.toLocaleString()}
Stadium Utilization: ${data.results.crowdAnalysis.utilizationRate}%

${data.results.crowdAnalysis.sections
  .map(
    (section: any) => `
${section.name}: ${section.attendance.toLocaleString()} / ${section.capacity.toLocaleString()} (${section.density}%)
Peak Noise: ${section.noiseLevel.peak} ${section.noiseLevel.unit}
`,
  )
  .join("")}

HIGHLIGHTS
==========
${data.results.highlights
  .map(
    (highlight: any) =>
      `${highlight.timestamp} - ${highlight.type.toUpperCase()}: ${highlight.description} (${Math.round(highlight.confidence * 100)}% confidence)`,
  )
  .join("\n")}

TECHNICAL METADATA
==================
Overall Confidence: ${Math.round(data.results.metadata.confidence * 100)}%
Quality Score: ${data.results.metadata.qualityScore}/10
Processing Version: ${data.results.metadata.processingVersion}

Report generated by AFL Analytics Platform
`;
};

// Convert backend JSON to HTML for PDF
export const convertBackendDataToHTML = (data: any) => {
  return `
      <div class="section">
        <h1>AFL Video Analysis Report</h1>
        <div class="metric">
          <strong>Generated:</strong> ${new Date(data.timestamp).toLocaleString()}<br>
          <strong>Analysis ID:</strong> ${data.analysisId}<br>
          <strong>Video File:</strong> ${data.videoFile.name}<br>
          <strong>Duration:</strong> ${data.videoFile.duration}<br>
          <strong>Processing Time:</strong> ${data.processingTime} seconds
        </div>
      </div>

      <div class="section">
        <h2>Player Performance Analysis</h2>
        <div class="player-grid">
          ${data.results.playerPerformance
            .map(
              (player: any) => `
            <div class="player-card">
              <h3 style="margin: 0 0 8px 0; color: #059669;">${player.name}</h3>
              <div class="player-team">${player.team} - ${player.position}</div>
              <div><strong>Max Speed:</strong> ${player.statistics.speed.max} ${player.statistics.speed.unit}</div>
              <div><strong>Distance:</strong> ${player.statistics.distance.total} ${player.statistics.distance.unit}</div>
              <div><strong>Goals:</strong> ${player.statistics.goals} | <strong>Assists:</strong> ${player.statistics.assists}</div>
              <div><strong>Efficiency:</strong> ${player.statistics.touches.efficiency}%</div>
            </div>
          `,
            )
            .join("")}
        </div>
      </div>

      <div class="section">
        <h2>Crowd Analysis</h2>
        <div class="metric">
          <strong>Total Attendance:</strong> ${data.results.crowdAnalysis.totalAttendance.toLocaleString()}<br>
          <strong>Utilization Rate:</strong> ${data.results.crowdAnalysis.utilizationRate}%
        </div>
        ${data.results.crowdAnalysis.sections
          .map(
            (section: any) => `
          <div class="crowd-item">
            <strong>${section.name}:</strong> ${section.attendance.toLocaleString()} / ${section.capacity.toLocaleString()} (${section.density}%)<br>
            Peak Noise: ${section.noiseLevel.peak} ${section.noiseLevel.unit}
          </div>
        `,
          )
          .join("")}
      </div>

      <div class="section">
        <h2>Technical Information</h2>
        <div class="metric">
          <strong>Analysis Confidence:</strong> ${Math.round(data.results.metadata.confidence * 100)}%<br>
          <strong>Quality Score:</strong> ${data.results.metadata.qualityScore}/10<br>
          <strong>Processing Version:</strong> ${data.results.metadata.processingVersion}
        </div>
      </div>
    `;
};
