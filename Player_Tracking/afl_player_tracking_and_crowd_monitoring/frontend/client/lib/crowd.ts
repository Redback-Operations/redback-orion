export type CrowdZone = {
  zone: string;
  capacity: number;
  current: number;
  density: number;
  trend: "up" | "down" | "stable";
  color: string;
  position: { top?: string; right?: string; bottom?: string; left?: string; width: string; height: string };
};

export function generateTimelineFromStadiumData(crowdZones: CrowdZone[]) {
  const currentAttendance = crowdZones.reduce((sum, zone) => sum + zone.current, 0);
  const currentDensity = Math.round(
    crowdZones.reduce((sum, zone) => sum + zone.density, 0) / crowdZones.length,
  );
  const currentCritical = crowdZones.filter((zone) => zone.density >= 95).length;
  const currentHigh = crowdZones.filter((zone) => zone.density >= 85 && zone.density < 95).length;

  return [
    { time: "12:00", attendance: Math.round(currentAttendance * 0.6), density: Math.round(currentDensity * 0.7), critical: 0, high: Math.max(0, currentHigh - 2) },
    { time: "13:00", attendance: Math.round(currentAttendance * 0.7), density: Math.round(currentDensity * 0.8), critical: Math.max(0, currentCritical - 1), high: Math.max(0, currentHigh - 1) },
    { time: "14:00", attendance: Math.round(currentAttendance * 0.8), density: Math.round(currentDensity * 0.85), critical: Math.max(0, currentCritical - 1), high: currentHigh },
    { time: "15:00", attendance: Math.round(currentAttendance * 0.9), density: Math.round(currentDensity * 0.9), critical: currentCritical, high: currentHigh },
    { time: "16:00", attendance: currentAttendance, density: currentDensity, critical: currentCritical, high: currentHigh },
    { time: "17:00", attendance: Math.round(currentAttendance * 0.95), density: Math.round(currentDensity * 0.95), critical: Math.max(0, currentCritical - 1), high: currentHigh },
    { time: "18:00", attendance: Math.round(currentAttendance * 0.85), density: Math.round(currentDensity * 0.9), critical: Math.max(0, currentCritical - 1), high: Math.max(0, currentHigh - 1) },
  ];
}

export function getStaticAFLCrowdZones(): CrowdZone[] {
  return [
    { zone: "Northern Stand", capacity: 15000, current: 14250, density: 95, trend: "stable", color: "#dc2626", position: { top: "5%", left: "25%", width: "50%", height: "15%" } },
    { zone: "Southern Stand", capacity: 12000, current: 10800, density: 90, trend: "up", color: "#f97316", position: { bottom: "5%", left: "25%", width: "50%", height: "15%" } },
    { zone: "Eastern Wing", capacity: 8000, current: 3200, density: 40, trend: "down", color: "#22c55e", position: { top: "25%", right: "5%", width: "15%", height: "50%" } },
    { zone: "Western Wing", capacity: 8000, current: 7200, density: 90, trend: "stable", color: "#f97316", position: { top: "25%", left: "5%", width: "15%", height: "50%" } },
    { zone: "Northeast Corner", capacity: 5000, current: 2750, density: 55, trend: "up", color: "#eab308", position: { top: "15%", right: "15%", width: "20%", height: "20%" } },
    { zone: "Northwest Corner", capacity: 5000, current: 4750, density: 95, trend: "stable", color: "#dc2626", position: { top: "15%", left: "15%", width: "20%", height: "20%" } },
    { zone: "Southeast Corner", capacity: 5000, current: 3750, density: 75, trend: "down", color: "#f59e0b", position: { bottom: "15%", right: "15%", width: "20%", height: "20%" } },
    { zone: "Southwest Corner", capacity: 5000, current: 1500, density: 30, trend: "stable", color: "#22c55e", position: { bottom: "15%", left: "15%", width: "20%", height: "20%" } },
  ];
}
