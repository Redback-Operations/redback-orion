import { useState, useMemo } from "react";
import { mockPlayers } from "@/lib/mock-data";
import type { QueueItem } from "@/types/dashboard";

// Types for better type safety
export interface Player {
  id: number;
  name: string;
  team: string;
  position: string;
  kicks: number;
  handballs: number;
  marks: number;
  tackles: number;
  goals: number;
  efficiency: number;
  rating?: number;
}

export interface TeamMatch {
  id: number;
  round: string;
  venue: string;
  date: string;
  teams: { home: string; away: string };
  stats: {
    home: TeamStats;
    away: TeamStats;
  };
}

export interface TeamStats {
  goals: number;
  behinds: number;
  disposals: number;
  marks: number;
  tackles: number;
  clearances: number;
  inside50: number;
  efficiency: number;
}

export interface TeamComparison {
  a: TeamStats;
  b: TeamStats;
  aEff: number;
  bEff: number;
}

export function useDashboardState() {
  // Player-related state
  const [selectedPlayer, setSelectedPlayer] = useState<Player>(mockPlayers[0] || {
    id: 0,
    name: "No Player",
    team: "Unknown",
    position: "Unknown",
    kicks: 0,
    handballs: 0,
    marks: 0,
    tackles: 0,
    goals: 0,
    efficiency: 0,
    rating: 0
  });
  const [comparisonPlayer, setComparisonPlayer] = useState<Player>(mockPlayers[1] || mockPlayers[0] || {
    id: 0,
    name: "No Player",
    team: "Unknown",
    position: "Unknown",
    kicks: 0,
    handballs: 0,
    marks: 0,
    tackles: 0,
    goals: 0,
    efficiency: 0,
    rating: 0
  });
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");

  // UI state
  const [isLive, setIsLive] = useState(true);
  const [userEmail, setUserEmail] = useState("demo@aflanalytics.com");

  // Video upload states
  const [selectedVideoFile, setSelectedVideoFile] = useState<File | null>(null);
  const [isVideoUploading, setIsVideoUploading] = useState(false);
  const [videoUploadProgress, setVideoUploadProgress] = useState(0);
  const [isVideoAnalyzing, setIsVideoAnalyzing] = useState(false);
  const [videoAnalysisProgress, setVideoAnalysisProgress] = useState(0);
  const [videoAnalysisComplete, setVideoAnalysisComplete] = useState(false);
  const [videoAnalysisError, setVideoAnalysisError] = useState<string | null>(null);
  const [selectedAnalysisType, setSelectedAnalysisType] = useState("highlights");
  const [selectedFocusAreas, setSelectedFocusAreas] = useState<string[]>([]);

  // Processing Queue state
  const [processingQueue, setProcessingQueue] = useState<QueueItem[]>([]);

  // Team comparison state
  const [teamA, setTeamA] = useState("Western Bulldogs");
  const [teamB, setTeamB] = useState("Richmond");

  // Computed values
  const filteredPlayers = useMemo(() => {
    return mockPlayers.filter(
      (player) =>
        player.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        (selectedTeam === "all" || player.team === selectedTeam)
    );
  }, [searchTerm, selectedTeam]);

  const teamCompare = useMemo((): TeamComparison => {
    const calcTotals = (teamName: string) => {
      const matches = teamMatches.filter(
        (match) => match.teams.home === teamName || match.teams.away === teamName
      );
      let base: TeamStats = { 
        goals: 0, behinds: 0, disposals: 0, marks: 0, tackles: 0, 
        clearances: 0, inside50: 0, efficiency: 0 
      };
      
      for (const match of matches) {
        const isHome = match.teams.home === teamName;
        const stats = isHome ? match.stats.home : match.stats.away;
        base.goals += stats.goals;
        base.behinds += stats.behinds;
        base.disposals += stats.disposals;
        base.marks += stats.marks;
        base.tackles += stats.tackles;
        base.clearances += stats.clearances;
        base.inside50 += stats.inside50;
        base.efficiency += stats.efficiency;
      }
      return base;
    };
    
    const a = calcTotals(teamA);
    const b = calcTotals(teamB);
    const aEff = Math.round(a.efficiency / Math.max(1, teamMatches.filter(m => m.teams.home === teamA || m.teams.away === teamA).length));
    const bEff = Math.round(b.efficiency / Math.max(1, teamMatches.filter(m => m.teams.home === teamB || m.teams.away === teamB).length));
    
    return { a, b, aEff, bEff };
  }, [teamA, teamB]);

  // Available teams for selection
  const availableTeams = useMemo(() => {
    return Array.from(new Set(mockPlayers.map(p => p.team)));
  }, []);

  // Performance trend data for the selected player
  const performanceTrendData = useMemo(() => {
    if (!selectedPlayer) return [];
    
    return [
      { week: "Week 1", kicks: selectedPlayer.kicks - 5, handballs: selectedPlayer.handballs - 3, marks: selectedPlayer.marks - 2, tackles: selectedPlayer.tackles - 1, goals: selectedPlayer.goals - 1, efficiency: selectedPlayer.efficiency - 5 },
      { week: "Week 2", kicks: selectedPlayer.kicks - 2, handballs: selectedPlayer.handballs - 1, marks: selectedPlayer.marks - 1, tackles: selectedPlayer.tackles, goals: selectedPlayer.goals, efficiency: selectedPlayer.efficiency - 2 },
      { week: "Week 3", kicks: selectedPlayer.kicks + 1, handballs: selectedPlayer.handballs + 1, marks: selectedPlayer.marks, tackles: selectedPlayer.tackles + 1, goals: selectedPlayer.goals + 1, efficiency: selectedPlayer.efficiency + 2 },
      { week: "Week 4", kicks: selectedPlayer.kicks, handballs: selectedPlayer.handballs, marks: selectedPlayer.marks, tackles: selectedPlayer.tackles, goals: selectedPlayer.goals, efficiency: selectedPlayer.efficiency },
      { week: "Week 5", kicks: selectedPlayer.kicks + 3, handballs: selectedPlayer.handballs + 2, marks: selectedPlayer.marks + 1, tackles: selectedPlayer.tackles + 2, goals: selectedPlayer.goals + 1, efficiency: selectedPlayer.efficiency + 3 },
    ];
  }, [selectedPlayer]);

  // Player comparison data for the comparison chart
  const playerComparisonData = useMemo(() => {
    if (!selectedPlayer || !comparisonPlayer) return [];
    
    return [
      { stat: "Kicks", [selectedPlayer.name]: selectedPlayer.kicks, [comparisonPlayer.name]: comparisonPlayer.kicks },
      { stat: "Handballs", [selectedPlayer.name]: selectedPlayer.handballs, [comparisonPlayer.name]: comparisonPlayer.handballs },
      { stat: "Marks", [selectedPlayer.name]: selectedPlayer.marks, [comparisonPlayer.name]: comparisonPlayer.marks },
      { stat: "Tackles", [selectedPlayer.name]: selectedPlayer.tackles, [comparisonPlayer.name]: comparisonPlayer.tackles },
      { stat: "Goals", [selectedPlayer.name]: selectedPlayer.goals, [comparisonPlayer.name]: comparisonPlayer.goals },
      { stat: "Efficiency", [selectedPlayer.name]: selectedPlayer.efficiency, [comparisonPlayer.name]: comparisonPlayer.efficiency },
    ];
  }, [selectedPlayer, comparisonPlayer]);

  return {
    // Player state
    selectedPlayer,
    setSelectedPlayer,
    comparisonPlayer,
    setComparisonPlayer,
    searchTerm,
    setSearchTerm,
    selectedTeam,
    setSelectedTeam,
    filteredPlayers,
    availableTeams,

    // UI state
    isLive,
    setIsLive,
    userEmail,
    setUserEmail,

    // Video state
    selectedVideoFile,
    setSelectedVideoFile,
    isVideoUploading,
    setIsVideoUploading,
    videoUploadProgress,
    setVideoUploadProgress,
    isVideoAnalyzing,
    setIsVideoAnalyzing,
    videoAnalysisProgress,
    setVideoAnalysisProgress,
    videoAnalysisComplete,
    setVideoAnalysisComplete,
    videoAnalysisError,
    setVideoAnalysisError,
    selectedAnalysisType,
    setSelectedAnalysisType,
    selectedFocusAreas,
    setSelectedFocusAreas,

    // Queue state
    processingQueue,
    setProcessingQueue,

  // Team state
  teamA,
  setTeamA,
  teamB,
  setTeamB,
  teamCompare,

  // Performance trend data
  performanceTrendData,
  playerComparisonData,
  };
}

// Mock data - this should eventually come from the backend
const teamMatches: TeamMatch[] = [
  {
    id: 1,
    round: "Round 12",
    venue: "MCG",
    date: "2025-07-02",
    teams: { home: "Western Bulldogs", away: "Richmond" },
    stats: {
      home: { goals: 12, behinds: 8, disposals: 368, marks: 86, tackles: 57, clearances: 34, inside50: 55, efficiency: 76 },
      away: { goals: 10, behinds: 11, disposals: 341, marks: 73, tackles: 62, clearances: 31, inside50: 49, efficiency: 72 },
    },
  },
  {
    id: 2,
    round: "Round 12",
    venue: "Marvel Stadium",
    date: "2025-07-03",
    teams: { home: "Geelong", away: "Collingwood" },
    stats: {
      home: { goals: 14, behinds: 7, disposals: 402, marks: 90, tackles: 51, clearances: 39, inside50: 61, efficiency: 79 },
      away: { goals: 9, behinds: 12, disposals: 359, marks: 77, tackles: 66, clearances: 30, inside50: 47, efficiency: 71 },
    },
  },
  {
    id: 3,
    round: "Round 13",
    venue: "Adelaide Oval",
    date: "2025-07-10",
    teams: { home: "Adelaide", away: "Port Adelaide" },
    stats: {
      home: { goals: 11, behinds: 13, disposals: 372, marks: 81, tackles: 64, clearances: 37, inside50: 58, efficiency: 73 },
      away: { goals: 12, behinds: 10, disposals: 365, marks: 75, tackles: 59, clearances: 35, inside50: 54, efficiency: 75 },
    },
  },
];