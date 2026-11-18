# Dummy data audit

Most of the analysis pages in the web app still show hardcoded or randomly generated data (`Math.random()`) instead of real backend results. This file lists every place we found, so the team can replace them one at a time.

Audited November 2026. Line numbers were correct at the time and will drift as files change, so search for the function or variable name if a link is off.

**How to use this list:** pick an item, fix it in a feature branch, and tick the box in the same pull request. When you replace dummy data, use the real endpoints listed under [What's already real](#whats-already-real) where you can. If there's no endpoint for something yet, either remove the section or add a visible "Demo data" label so nobody mistakes it for real results.

## Priority 1: downloads that pass off fake data as real results

These are the most serious. A user uploads their own video and gets a report full of made-up stats presented as that video's analysis.

- [ ] **AFLDashboard: report download after analysis.** `fetchBackendAnalysisData` ([client/pages/AFLDashboard.tsx:1233](client/pages/AFLDashboard.tsx)) is commented "Simulate backend JSON response" and returns fixed players (Marcus Bontempelli and others) with random processing times. Replace with the job's results from `GET /status/{job_id}` or `GET /jobs/{job_id}`.
- [ ] **AFLDashboard: download from the processing queue.** `handleDownloadFromQueue` ([AFLDashboard.tsx:651](client/pages/AFLDashboard.tsx)) builds the same fixed report for completed jobs. Use the job ID it already has to fetch the real results.
- [ ] **AFLDashboard: "View analysis" modal.** `generateAnalysisChartData` ([AFLDashboard.tsx:513](client/pages/AFLDashboard.tsx)) and the block marked "Simple mock data" (around line 3405) show fixed players and charts.
- [ ] **AFLDashboard: video clips export.** `handleDownloadVideoClips` ([AFLDashboard.tsx:1495](client/pages/AFLDashboard.tsx)) uses `generateDashboardInsights` (line 1180) and invents clip times, durations, noise levels and processing time.
- [ ] **Analytics: analysis results.** Upload and status polling are real, but the results shown come from `generateAnalysisData()` ([client/pages/Analytics.tsx:67](client/pages/Analytics.tsx)). The polled `results` are never read.
- [ ] **Analytics: report contents.** `generateVideoInsights` ([Analytics.tsx:477](client/pages/Analytics.tsx)) fills reports with random player and crowd stats, after a fake 1.5 second "generating" delay (around line 595).
- [ ] **Reports: "Generate report".** `generateNewReport` ([client/pages/Reports.tsx:287](client/pages/Reports.tsx)) waits 2 seconds, then writes random counts into the file (around line 410).

## Priority 2: crowd pages

- [ ] **CrowdMonitor: zones.** `generateCrowdData` ([client/pages/CrowdMonitor.tsx:39](client/pages/CrowdMonitor.tsx)) is a fixed list of stands with random trend, wait time and flow. This drives the heat map, Zone Details and Analytics tabs.
- [ ] **CrowdMonitor: fake "live" updates.** A timer ([CrowdMonitor.tsx:409](client/pages/CrowdMonitor.tsx)) changes the zone counts randomly every few seconds. Remove it, or replace it with polling of real results.
- [ ] **CrowdMonitor: heat map shapes.** `heatRegions` ([CrowdMonitor.tsx:186](client/pages/CrowdMonitor.tsx)) is fixed positions and levels.
- [ ] **AFLDashboard: Crowd Monitor tab.** `crowdZones` ([AFLDashboard.tsx:194](client/pages/AFLDashboard.tsx)) drives Stadium Zone Density, the stadium map and "Safest Zone". The "89%" figure under Historical Crowd Data (around line 2416) is hardcoded too.

The Peak Crowd card on CrowdMonitor already reads real crowd results (`components/PeakCrowdCard.tsx`), so it's a good model for the items above.

## Priority 3: hardcoded lists and fake status

- [ ] **AFLDashboard: Live Match tab.** The "Carlton vs Adelaide" header, the 324 / 42 / 28 numbers, the possession, Inside 50s and contested marks figures (around lines 2158 to 2240), and the events timeline `matchEvents` ([AFLDashboard.tsx:163](client/pages/AFLDashboard.tsx)) are all hardcoded. There's no live match feed in the backend, so remove the tab or label it as demo data.
- [ ] **AFLDashboard: "Recent Reports" list** (around line 2673) lists reports that don't exist ("Round 15", "MCG").
- [ ] **AFLDashboard: queue item details.** New queue items get a random video duration, completion estimate and priority (around line 1002). Retry also sets a random estimate (around line 399).
- [ ] **AFLDashboard: queue progress simulator.** The `useEffect` at [AFLDashboard.tsx:783](client/pages/AFLDashboard.tsx) fakes progress and random failures. It skips items uploaded through the page, so it's mostly dead code and can be removed.
- [ ] **Analytics: Queue tab.** `processingQueue` ([Analytics.tsx:176](client/pages/Analytics.tsx)) is a fixed list of files like `Round_15_Carlton_vs_Adelaide.mp4`. Replace with `GET /jobs`.
- [ ] **Analytics: reports list.** `availableReports` ([Analytics.tsx:246](client/pages/Analytics.tsx)) is fixed.
- [ ] **Reports: reports list.** `availableReports` ([Reports.tsx:45](client/pages/Reports.tsx)) is fixed, dated 2024, and shown below the one real row from `/api/analytics/latest`.
- [ ] **ApiDiagnostics page.** `generateApiStatus` ([client/pages/ApiDiagnostics.tsx:57](client/pages/ApiDiagnostics.tsx)) lists `/api/v1/...` endpoints the backend doesn't have, with random response times and uptime. "Test API" (around line 245) never sends a request and returns a 500 about 20% of the time. Either point it at the real backend (`/health`, `/docs`) or remove the page.

## Priority 4: missing player stats

- [ ] **PlayerPerformance: zero-filled stats.** `normalizePlayer` ([client/pages/PlayerPerformance.tsx:262](client/pages/PlayerPerformance.tsx)) sets speed, distance, contested, clangers, rebounds and others to `0` because the backend doesn't store them. The Form and Heat Map tabs are always empty. Either add these fields to the backend or hide what we don't have.
- [ ] **PlayerPerformance: made-up "Assists".** `playerMetrics` ([PlayerPerformance.tsx:743](client/pages/PlayerPerformance.tsx)) shows `inside50s / 2` as assists.
- [ ] **PlayerPerformance: hardcoded chart targets.** `performanceMetrics` ([PlayerPerformance.tsx:710](client/pages/PlayerPerformance.tsx)) uses fixed targets (goals 3, disposals 35 and so on). Fine to keep, but say where they come from.

## Cleanup: dead code and leftovers

- [ ] **Delete `generatePlayerData`** ([PlayerPerformance.tsx:74](client/pages/PlayerPerformance.tsx)). It's never called and is about 180 lines.
- [ ] **Delete `validCredentials` and `demoLogin`** ([client/pages/Login.tsx:81](client/pages/Login.tsx) and line 179). Neither is used, but the demo passwords still end up in the built JavaScript.
- [ ] **Remove the `/stitch` route and `client/pages/Index.tsx`.** It's a page left over from the starter template, for a UI generator called "Stitch", and has nothing to do with Orion.
- [ ] **Use `BACKEND_URL` in Admin and ResetPassword.** Both hardcode `http://localhost:8000` ([client/pages/Admin.tsx:17](client/pages/Admin.tsx), [client/pages/ResetPassword.tsx:53](client/pages/ResetPassword.tsx)), so they break if the backend runs anywhere else.
- [ ] **Decide on Profile and Settings storage.** Name, date of birth and role are saved in the browser only (`localStorage`), so edits never reach the backend and don't carry across devices.

`/error-demo` (`ErrorDemo.tsx`) fakes loading and errors on purpose to show the error screens, so it isn't on this list. Consider hiding it in production builds.

## What's already real

These parts already use the backend and can be used as examples:

| Page or part | Endpoint |
|---|---|
| Player list, search, stats card and comparison (AFLDashboard, PlayerPerformance) | `GET /api/players` |
| Video upload and status polling (AFLDashboard, Analytics, PlayerPerformance) | `POST /upload`, `GET /status/{job_id}` |
| Jobs list, delete player, Excel import (PlayerPerformance) | `GET /jobs`, `DELETE /api/player/{id}`, `POST /api/players/upload-excel` |
| Peak Crowd card (CrowdMonitor) | `GET /jobs`, `GET /jobs/{job_id}`, `GET /api/crowd/latest` |
| The "live" row at the top of Reports | `GET /api/analytics/latest` |
| Admin, AddPlayer, Login, ResetPassword | Backend auth and player endpoints |

See [backend/API_CONTRACT.md](../backend/API_CONTRACT.md) for the response formats.
