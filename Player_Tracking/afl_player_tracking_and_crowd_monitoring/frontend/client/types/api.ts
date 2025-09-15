// API Types for Backend Integration
// This file defines the expected data structures for API communication

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

// Player API Types
export interface PlayerApiData {
  id: number;
  name: string;
  team: string;
  position: string;
  jerseyNumber: number;
  stats: PlayerStats;
  rating: number;
  photo?: string;
}

export interface PlayerStats {
  kicks: number;
  handballs: number;
  marks: number;
  tackles: number;
  goals: number;
  behinds: number;
  disposals: number;
  efficiency: number;
  clearances: number;
  inside50s: number;
  contestedPossessions: number;
  uncontestedPossessions: number;
}

// Team API Types
export interface TeamApiData {
  id: number;
  name: string;
  logo?: string;
  colors: {
    primary: string;
    secondary: string;
  };
  players: PlayerApiData[];
  stats: TeamStats;
}

export interface TeamStats {
  goals: number;
  behinds: number;
  disposals: number;
  marks: number;
  tackles: number;
  clearances: number;
  inside50s: number;
  efficiency: number;
  contestedPossessions: number;
  uncontestedPossessions: number;
}

// Match API Types
export interface MatchApiData {
  id: number;
  round: string;
  venue: string;
  date: string;
  teams: {
    home: TeamApiData;
    away: TeamApiData;
  };
  stats: {
    home: TeamStats;
    away: TeamStats;
  };
  events: MatchEvent[];
  status: 'scheduled' | 'live' | 'completed';
}

export interface MatchEvent {
  id: number;
  timestamp: string;
  type: 'goal' | 'behind' | 'mark' | 'tackle' | 'clearance' | 'inside50';
  player: PlayerApiData;
  team: string;
  description: string;
}

// Video Analysis API Types
export interface VideoAnalysisRequest {
  file: File;
  analysisType: 'highlights' | 'player_tracking' | 'crowd_analysis' | 'tactical_analysis';
  focusAreas: string[];
  teamId?: number;
  playerId?: number;
}

export interface VideoAnalysisResponse {
  id: string;
  status: 'processing' | 'completed' | 'failed';
  progress: number;
  results?: VideoAnalysisResults;
  error?: string;
}

export interface VideoAnalysisResults {
  highlights: VideoClip[];
  playerTracking: PlayerTrackingData[];
  crowdAnalysis: CrowdAnalysisData;
  tacticalInsights: TacticalInsight[];
}

export interface VideoClip {
  id: string;
  startTime: number;
  endTime: number;
  description: string;
  type: 'goal' | 'tackle' | 'mark' | 'clearance' | 'highlight';
  player?: PlayerApiData;
  downloadUrl: string;
}

export interface PlayerTrackingData {
  playerId: number;
  playerName: string;
  positions: Position[];
  speed: number[];
  distance: number;
  heatmap: HeatmapData;
}

export interface Position {
  x: number;
  y: number;
  timestamp: number;
}

export interface HeatmapData {
  x: number[];
  y: number[];
  intensity: number[];
}

export interface CrowdAnalysisData {
  totalAttendance: number;
  densityByZone: ZoneDensity[];
  safetyAlerts: SafetyAlert[];
  crowdFlow: CrowdFlowData[];
}

export interface ZoneDensity {
  zoneId: string;
  zoneName: string;
  density: number; // 0-100
  capacity: number;
  occupancy: number;
  status: 'safe' | 'warning' | 'critical';
}

export interface SafetyAlert {
  id: string;
  type: 'density' | 'flow' | 'emergency';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  zoneId: string;
  timestamp: string;
}

export interface CrowdFlowData {
  timestamp: string;
  zoneId: string;
  flowDirection: 'in' | 'out' | 'static';
  flowRate: number;
}

export interface TacticalInsight {
  id: string;
  type: 'formation' | 'movement' | 'strategy';
  description: string;
  confidence: number; // 0-100
  timestamp: number;
  players: number[];
}

// Reports API Types
export interface ReportRequest {
  type: 'player_performance' | 'team_analysis' | 'match_summary' | 'video_analysis';
  format: 'pdf' | 'excel' | 'csv';
  filters: ReportFilters;
  dateRange: {
    start: string;
    end: string;
  };
}

export interface ReportFilters {
  teamIds?: number[];
  playerIds?: number[];
  matchIds?: number[];
  analysisTypes?: string[];
}

export interface ReportResponse {
  id: string;
  status: 'generating' | 'completed' | 'failed';
  downloadUrl?: string;
  error?: string;
}

// Queue API Types
export interface QueueItem {
  id: string;
  type: 'video_analysis' | 'report_generation' | 'data_processing';
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  createdAt: string;
  estimatedCompletion?: string;
  error?: string;
  result?: any;
}

// API Endpoints
export const API_ENDPOINTS = {
  // Players
  PLAYERS: '/api/players',
  PLAYER_STATS: '/api/players/:id/stats',
  
  // Teams
  TEAMS: '/api/teams',
  TEAM_STATS: '/api/teams/:id/stats',
  
  // Matches
  MATCHES: '/api/matches',
  MATCH_DETAILS: '/api/matches/:id',
  
  // Video Analysis
  VIDEO_UPLOAD: '/api/video/upload',
  VIDEO_ANALYSIS: '/api/video/analysis/:id',
  VIDEO_RESULTS: '/api/video/results/:id',
  
  // Reports
  REPORTS: '/api/reports',
  REPORT_GENERATE: '/api/reports/generate',
  REPORT_DOWNLOAD: '/api/reports/:id/download',
  
  // Queue
  QUEUE: '/api/queue',
  QUEUE_ITEM: '/api/queue/:id',
  
  // Crowd Monitoring
  CROWD_DATA: '/api/crowd/data',
  CROWD_ALERTS: '/api/crowd/alerts',
} as const;
