import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { downloadText, downloadFile } from "@/lib/download";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import {
  Activity,
  Users,
  BarChart3,
  Download,
  Upload,
  Search,
  Filter,
  Play,
  Pause,
  TrendingUp,
  TrendingDown,
  Clock,
  MapPin,
  Video,
  Eye,
  Target,
  Zap,
  Calendar,
  FileText,
  Settings,
  LogOut,
  ChevronDown,
  Flag,
} from "lucide-react";

// Mock data for the dashboard
const mockPlayers = [
  {
    id: 1,
    name: "Marcus Bontempelli",
    team: "Western Bulldogs",
    position: "Midfielder",
    kicks: 28,
    handballs: 12,
    marks: 8,
    tackles: 6,
    goals: 2,
    efficiency: 87,
  },
  {
    id: 2,
    name: "Dustin Martin",
    team: "Richmond",
    position: "Forward",
    kicks: 22,
    handballs: 8,
    marks: 6,
    tackles: 4,
    goals: 3,
    efficiency: 82,
  },
  {
    id: 3,
    name: "Patrick Dangerfield",
    team: "Geelong",
    position: "Midfielder",
    kicks: 25,
    handballs: 15,
    marks: 7,
    tackles: 8,
    goals: 1,
    efficiency: 84,
  },
  {
    id: 4,
    name: "Max Gawn",
    team: "Melbourne",
    position: "Ruckman",
    kicks: 18,
    handballs: 6,
    marks: 10,
    tackles: 3,
    goals: 1,
    efficiency: 78,
  },
];

const matchEvents = [
  {
    time: "1:32",
    event: "GOAL",
    player: "Charlie Curnow",
    team: "Carlton",
    description: "Beautiful mark and goal from 30m out",
  },
  {
    time: "3:45",
    event: "BEHIND",
    player: "Taylor Walker",
    team: "Adelaide",
    description: "Shot from the boundary line",
  },
  {
    time: "5:12",
    event: "MARK",
    player: "Jeremy McGovern",
    team: "West Coast",
    description: "Spectacular defensive mark",
  },
  {
    time: "7:22",
    event: "TACKLE",
    player: "Clayton Oliver",
    team: "Melbourne",
    description: "Crucial tackle in defensive 50",
  },
];

// Generate timeline data based on current stadium zones
const generateTimelineFromStadiumData = (crowdZones) => {
  const currentAttendance = crowdZones.reduce(
    (sum, zone) => sum + zone.current,
    0,
  );
  const currentDensity = Math.round(
    crowdZones.reduce((sum, zone) => sum + zone.density, 0) / crowdZones.length,
  );
  const currentCritical = crowdZones.filter(
    (zone) => zone.density >= 95,
  ).length;
  const currentHigh = crowdZones.filter(
    (zone) => zone.density >= 85 && zone.density < 95,
  ).length;

  // Generate historical timeline showing progression to current state
  return [
    {
      time: "12:00",
      attendance: Math.round(currentAttendance * 0.6),
      density: Math.round(currentDensity * 0.7),
      critical: 0,
      high: Math.max(0, currentHigh - 2),
    },
    {
      time: "13:00",
      attendance: Math.round(currentAttendance * 0.7),
      density: Math.round(currentDensity * 0.8),
      critical: Math.max(0, currentCritical - 1),
      high: Math.max(0, currentHigh - 1),
    },
    {
      time: "14:00",
      attendance: Math.round(currentAttendance * 0.8),
      density: Math.round(currentDensity * 0.85),
      critical: Math.max(0, currentCritical - 1),
      high: currentHigh,
    },
    {
      time: "15:00",
      attendance: Math.round(currentAttendance * 0.9),
      density: Math.round(currentDensity * 0.9),
      critical: currentCritical,
      high: currentHigh,
    },
    {
      time: "16:00",
      attendance: currentAttendance,
      density: currentDensity,
      critical: currentCritical,
      high: currentHigh,
    },
    {
      time: "17:00",
      attendance: Math.round(currentAttendance * 0.95),
      density: Math.round(currentDensity * 0.95),
      critical: Math.max(0, currentCritical - 1),
      high: currentHigh,
    },
    {
      time: "18:00",
      attendance: Math.round(currentAttendance * 0.85),
      density: Math.round(currentDensity * 0.9),
      critical: Math.max(0, currentCritical - 1),
      high: Math.max(0, currentHigh - 1),
    },
  ];
};

// Static crowd zones for AFL ground with realistic varying density
const getStaticAFLCrowdZones = () => {
  return [
    {
      zone: "Northern Stand",
      capacity: 15000,
      current: 14250,
      density: 95,
      trend: "stable",
      color: "#dc2626", // red - critical
      position: { top: "5%", left: "25%", width: "50%", height: "15%" },
    },
    {
      zone: "Southern Stand",
      capacity: 12000,
      current: 10800,
      density: 90,
      trend: "up",
      color: "#f97316", // orange - high
      position: { bottom: "5%", left: "25%", width: "50%", height: "15%" },
    },
    {
      zone: "Eastern Wing",
      capacity: 8000,
      current: 3200,
      density: 40,
      trend: "down",
      color: "#22c55e", // green - low
      position: { top: "25%", right: "5%", width: "15%", height: "50%" },
    },
    {
      zone: "Western Wing",
      capacity: 8000,
      current: 7200,
      density: 90,
      trend: "stable",
      color: "#f97316", // orange - high
      position: { top: "25%", left: "5%", width: "15%", height: "50%" },
    },
    {
      zone: "Northeast Corner",
      capacity: 5000,
      current: 2750,
      density: 55,
      trend: "up",
      color: "#eab308", // yellow - low-medium
      position: { top: "15%", right: "15%", width: "20%", height: "20%" },
    },
    {
      zone: "Northwest Corner",
      capacity: 5000,
      current: 4750,
      density: 95,
      trend: "stable",
      color: "#dc2626", // red - critical
      position: { top: "15%", left: "15%", width: "20%", height: "20%" },
    },
    {
      zone: "Southeast Corner",
      capacity: 5000,
      current: 3750,
      density: 75,
      trend: "down",
      color: "#f59e0b", // amber - medium
      position: { bottom: "15%", right: "15%", width: "20%", height: "20%" },
    },
    {
      zone: "Southwest Corner",
      capacity: 5000,
      current: 1500,
      density: 30,
      trend: "stable",
      color: "#22c55e", // green - low
      position: { bottom: "15%", left: "15%", width: "20%", height: "20%" },
    },
  ];
};

type QueueItem = {
  id: string;
  name: string;
  analysisType: string;
  status:
    | "uploading"
    | "queued"
    | "processing"
    | "analyzing"
    | "completed"
    | "failed";
  progress: number;
  duration: string;
  size: string;
  uploadTime: string;
  completedTime: string | null;
  estimatedCompletion: string | null;
  priority: "low" | "medium" | "high";
  userId: string;
  processingStage: string;
  errorCount: number;
  retryCount: number;
  isUIControlled?: boolean;
};

export default function AFLDashboard() {
  const navigate = useNavigate();
  const [selectedPlayer, setSelectedPlayer] = useState(mockPlayers[0]);
  const [comparisonPlayer, setComparisonPlayer] = useState(mockPlayers[1]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");
  const [isLive, setIsLive] = useState(true);
  const [userEmail, setUserEmail] = useState("");

  // Static crowd zones data
  const crowdZones = getStaticAFLCrowdZones();

  // Team Match Performance data for Team tab
  const teamMatches = [
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

  const [teamSearch, setTeamSearch] = useState("");
  const [teamFilter, setTeamFilter] = useState("all");
  const [teamRound, setTeamRound] = useState("all");
  const teamRounds = useMemo(() => ["all", ...Array.from(new Set(teamMatches.map((m) => m.round)))], []);
  const teamTeams = useMemo(() => {
    const s = new Set<string>();
    teamMatches.forEach((m) => { s.add(m.teams.home); s.add(m.teams.away); });
    return ["all", ...Array.from(s).sort()];
  }, []);
  const teamFiltered = useMemo(() => {
    const q = teamSearch.trim().toLowerCase();
    return teamMatches.filter((m) => {
      const matchesRound = teamRound === "all" || m.round === teamRound;
      const matchesTeam = teamFilter === "all" || m.teams.home === teamFilter || m.teams.away === teamFilter;
      const hay = `${m.teams.home} ${m.teams.away} ${m.venue}`.toLowerCase();
      return matchesRound && matchesTeam && (q === "" || hay.includes(q));
    });
  }, [teamMatches, teamRound, teamFilter, teamSearch]);
  const teamSummary = useMemo(() => {
    return teamFiltered.reduce(
      (acc, m) => {
        acc.games += 1;
        acc.goals += m.stats.home.goals + m.stats.away.goals;
        acc.disposals += m.stats.home.disposals + m.stats.away.disposals;
        acc.inside50 += m.stats.home.inside50 + m.stats.away.inside50;
        return acc;
      },
      { games: 0, goals: 0, disposals: 0, inside50: 0 },
    );
  }, [teamFiltered]);

  // Compare Teams helpers
  const [teamA, setTeamA] = useState<string>("all");
  const [teamB, setTeamB] = useState<string>("all");
  const calcTotals = (name: string) => {
    const base = { goals: 0, disposals: 0, marks: 0, tackles: 0, clearances: 0, inside50: 0, effSum: 0, effCount: 0 };
    if (!name || name === "all") return base;
    for (const m of teamMatches) {
      if (m.teams.home === name) {
        base.goals += m.stats.home.goals; base.disposals += m.stats.home.disposals; base.marks += m.stats.home.marks; base.tackles += m.stats.home.tackles; base.clearances += m.stats.home.clearances; base.inside50 += m.stats.home.inside50; base.effSum += m.stats.home.efficiency; base.effCount += 1;
      }
      if (m.teams.away === name) {
        base.goals += m.stats.away.goals; base.disposals += m.stats.away.disposals; base.marks += m.stats.away.marks; base.tackles += m.stats.away.tackles; base.clearances += m.stats.away.clearances; base.inside50 += m.stats.away.inside50; base.effSum += m.stats.away.efficiency; base.effCount += 1;
      }
    }
    return base;
  };
  const teamCompare = useMemo(() => {
    const a = calcTotals(teamA); const b = calcTotals(teamB);
    const aEff = a.effCount ? Math.round(a.effSum / a.effCount) : 0;
    const bEff = b.effCount ? Math.round(b.effSum / b.effCount) : 0;
    return { a, b, aEff, bEff };
  }, [teamA, teamB]);

  const TeamCompareBar = ({ label, aLabel, aValue, bLabel, bValue }: { label: string; aLabel: string; aValue: number; bLabel: string; bValue: number }) => {
    const max = Math.max(aValue, bValue) || 1;
    const aPct = Math.round((aValue / max) * 100);
    const bPct = Math.round((bValue / max) * 100);
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium">{label}</span>
          <span className="text-gray-600">{aValue} vs {bValue}</span>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="w-28 text-xs text-blue-700 truncate">{aLabel}</span>
            <div className="flex-1 bg-gray-200 rounded-full h-3">
              <div className="bg-blue-500 h-3 rounded-full" style={{ width: `${aPct}%` }} />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-28 text-xs text-green-700 truncate">{bLabel}</span>
            <div className="flex-1 bg-gray-200 rounded-full h-3">
              <div className="bg-green-600 h-3 rounded-full" style={{ width: `${bPct}%` }} />
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Player card display state
  const [showAllCards, setShowAllCards] = useState(false);
  const [selectedCardIndex, setSelectedCardIndex] = useState(0);
  const [selectedCard, setSelectedCard] = useState(null);

  // Expanded card state
  const [expandedCardId, setExpandedCardId] = useState(null);

  // Video upload states
  const [selectedVideoFile, setSelectedVideoFile] = useState<File | null>(null);
  const [isVideoUploading, setIsVideoUploading] = useState(false);
  const [videoUploadProgress, setVideoUploadProgress] = useState(0);
  const [isVideoAnalyzing, setIsVideoAnalyzing] = useState(false);
  const [videoAnalysisProgress, setVideoAnalysisProgress] = useState(0);
  const [videoAnalysisComplete, setVideoAnalysisComplete] = useState(false);
  const [videoAnalysisError, setVideoAnalysisError] = useState<string | null>(
    null,
  );
  const [selectedAnalysisType, setSelectedAnalysisType] =
    useState("highlights");
  const [selectedFocusAreas, setSelectedFocusAreas] = useState<string[]>([]);

  // Analysis view modal state
  const [viewModalOpen, setViewModalOpen] = useState(false);
  const [selectedAnalysisItem, setSelectedAnalysisItem] = useState<any>(null);

  // Processing Queue state - starts empty, only shows actual uploads
  const [processingQueue, setProcessingQueue] = useState<QueueItem[]>([]);

  // Processing queue management functions
  const StatusIcon = ({ status }: { status: string }) => {
    switch (status) {
      case "completed":
        return <div className="w-3 h-3 rounded-full bg-green-500" />;
      case "analyzing":
      case "processing":
        return (
          <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse" />
        );
      case "uploading":
        return (
          <div className="w-3 h-3 rounded-full bg-yellow-500 animate-pulse" />
        );
      case "queued":
        return <div className="w-3 h-3 rounded-full bg-gray-400" />;
      case "failed":
        return <div className="w-3 h-3 rounded-full bg-red-500" />;
      default:
        return <div className="w-3 h-3 rounded-full bg-gray-300" />;
    }
  };

  const retryProcessing = (itemId: string) => {
    setProcessingQueue((prev) =>
      prev.map((item) =>
        item.id === itemId
          ? {
              ...item,
              status: "queued",
              progress: 0,
              processingStage: "queue_waiting",
              retryCount: item.retryCount + 1,
              estimatedCompletion: new Date(
                Date.now() + Math.random() * 3600000 + 1800000,
              ).toISOString(),
              // If this was a UI-controlled item, it should remain so after retry
              isUIControlled: item.isUIControlled || false,
            }
          : item,
      ),
    );
  };

  const removeFromQueue = (itemId: string) => {
    setProcessingQueue((prev) => prev.filter((item) => item.id !== itemId));
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24)
      return `${diffHours} hour${diffHours > 1 ? "s" : ""} ago`;
    return time.toLocaleDateString();
  };

  const formatETA = (timestamp: string | null) => {
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

  // Generate dynamic chart data for analysis results
  const generateAnalysisChartData = (item: any) => {
    // Player performance data for charts
    const playerStatsData = [
      {
        name: "Marcus Bontempelli",
        goals: 2,
        assists: 3,
        tackles: 6,
        marks: 8,
        efficiency: 85.7,
        maxSpeed: 32.4,
        distance: 12.8,
        disposals: 31,
      },
      {
        name: "Patrick Cripps",
        goals: 1,
        assists: 5,
        tackles: 9,
        marks: 6,
        efficiency: 88.6,
        maxSpeed: 29.8,
        distance: 13.2,
        disposals: 34,
      },
      {
        name: "Clayton Oliver",
        goals: 0,
        assists: 4,
        tackles: 7,
        marks: 5,
        efficiency: 82.3,
        maxSpeed: 28.1,
        distance: 11.5,
        disposals: 28,
      },
      {
        name: "Christian Petracca",
        goals: 3,
        assists: 2,
        tackles: 4,
        marks: 7,
        efficiency: 89.2,
        maxSpeed: 31.8,
        distance: 10.9,
        disposals: 26,
      },
    ];

    // Crowd density data for charts
    const crowdDensityData = [
      {
        section: "Northern Stand",
        density: 95.0,
        attendance: 14250,
        capacity: 15000,
        noiseLevel: 95.2,
      },
      {
        section: "Southern Stand",
        density: 97.3,
        attendance: 11680,
        capacity: 12000,
        noiseLevel: 92.8,
      },
      {
        section: "Eastern Wing",
        density: 88.5,
        attendance: 7080,
        capacity: 8000,
        noiseLevel: 87.4,
      },
      {
        section: "Western Wing",
        density: 91.2,
        attendance: 7296,
        capacity: 8000,
        noiseLevel: 89.6,
      },
      {
        section: "Premium Seats",
        density: 94.8,
        attendance: 2844,
        capacity: 3000,
        noiseLevel: 78.2,
      },
      {
        section: "MCC Members",
        density: 89.1,
        attributes: 4455,
        capacity: 5000,
        noiseLevel: 82.1,
      },
    ];

    // Performance timeline data
    const performanceTimelineData = [
      { time: "Q1", goals: 3, tackles: 15, marks: 12, efficiency: 84 },
      { time: "Q2", goals: 4, tackles: 18, marks: 14, efficiency: 87 },
      { time: "Q3", goals: 2, tackles: 12, marks: 10, efficiency: 82 },
      { time: "Q4", goals: 5, tackles: 20, marks: 16, efficiency: 89 },
    ];

    // Speed comparison data
    const speedComparisonData = [
      { player: "M. Bontempelli", maxSpeed: 32.4, avgSpeed: 24.8 },
      { player: "P. Cripps", maxSpeed: 29.8, avgSpeed: 22.1 },
      { player: "C. Oliver", maxSpeed: 28.1, avgSpeed: 21.5 },
      { player: "C. Petracca", maxSpeed: 31.8, avgSpeed: 25.2 },
    ];

    return {
      playerStats: playerStatsData,
      crowdDensity: crowdDensityData,
      performanceTimeline: performanceTimelineData,
      speedComparison: speedComparisonData,
    };
  };

  // Chart color schemes
  const chartColors = {
    primary: "#059669",
    secondary: "#2563eb",
    accent: "#dc2626",
    warning: "#d97706",
    success: "#16a34a",
    purple: "#7c3aed",
    pink: "#ec4899",
    teal: "#0d9488",
  };

  // View analysis results for a queue item
  const handleViewAnalysis = (item: any) => {
    setSelectedAnalysisItem(item);
    setViewModalOpen(true);
  };

  // Download analysis report for a queue item
  const handleDownloadFromQueue = async (
    item: any,
    format: "pdf" | "json" | "txt" = "pdf",
  ) => {
    try {
      // Generate analysis data for this specific item
      const analysisId = item.id;
      const backendData = {
        analysisId,
        timestamp: item.completedTime || item.uploadTime,
        videoFile: {
          name: item.name,
          duration: item.duration,
          size: item.size,
          resolution: "1920x1080",
          framerate: "30fps",
        },
        analysisType: item.analysisType,
        focusAreas: [], // Queue items don't have focus areas stored
        processingTime: Math.floor(Math.random() * 300 + 120),
        results: {
          playerPerformance: [
            {
              playerId: "p001",
              name: "Marcus Bontempelli",
              team: "Western Bulldogs",
              position: "Midfielder",
              statistics: {
                speed: { max: 32.4, average: 24.8, unit: "km/h" },
                distance: { total: 12.8, sprints: 2.3, unit: "km" },
                touches: { total: 28, effective: 24, efficiency: 85.7 },
                goals: 2,
                assists: 3,
                tackles: 6,
                marks: 8,
                disposals: 31,
                timeOnGround: 87.5,
              },
            },
            {
              playerId: "p002",
              name: "Patrick Cripps",
              team: "Carlton",
              position: "Midfielder",
              statistics: {
                speed: { max: 29.8, average: 22.1, unit: "km/h" },
                distance: { total: 13.2, sprints: 1.8, unit: "km" },
                touches: { total: 35, effective: 31, efficiency: 88.6 },
                goals: 1,
                assists: 5,
                tackles: 9,
                marks: 6,
                disposals: 34,
                timeOnGround: 92.3,
              },
            },
          ],
          crowdAnalysis: {
            totalAttendance: 47832,
            capacity: 50000,
            utilizationRate: 95.7,
            sections: [
              {
                sectionId: "north_stand",
                name: "Northern Stand",
                attendance: 14250,
                capacity: 15000,
                density: 95.0,
                noiseLevel: { peak: 95.2, average: 78.4, unit: "dB" },
              },
              {
                sectionId: "south_stand",
                name: "Southern Stand",
                attendance: 11680,
                capacity: 12000,
                density: 97.3,
                noiseLevel: { peak: 92.8, average: 76.9, unit: "dB" },
              },
            ],
          },
          highlights: [
            {
              timestamp: "00:03:45",
              duration: 15,
              type: "goal",
              description: "Opening goal with crowd eruption",
              players: ["Marcus Bontempelli"],
              confidence: 0.94,
            },
          ],
          metadata: {
            confidence: 0.923,
            processingVersion: "2.1.3",
            qualityScore: 8.7,
          },
        },
      };

      if (format === "json") {
        // Download raw JSON data
        const jsonContent = JSON.stringify(backendData, null, 2);
        const blob = new Blob([jsonContent], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${item.name.replace(/\.[^/.]+$/, "")}_Analysis.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else if (format === "pdf") {
        // Generate PDF from backend data
        const htmlContent = convertBackendDataToHTML(backendData);
        generateDashboardPDF(
          htmlContent,
          `${item.name.replace(/\.[^/.]+$/, "")}_Analysis`,
        );
      } else {
        // Generate TXT from backend data
        const textContent = convertBackendDataToText(backendData);
        downloadText(
          textContent,
          `${item.name.replace(/\.[^/.]+$/, "")}_Analysis`,
        );
      }
    } catch (error) {
      console.error("Error downloading analysis:", error);
      alert("Failed to download analysis. Please try again.");
    }
  };

  // Simulate realistic processing queue progress
  useEffect(() => {
    const interval = setInterval(() => {
      setProcessingQueue((prev) =>
        prev.map((item) => {
          // Only update items that are actively processing AND not controlled by UI
          if (
            (item.status === "analyzing" ||
              item.status === "processing" ||
              item.status === "uploading" ||
              item.status === "queued") &&
            !item.isUIControlled
          ) {
            // Variable progress based on file size and complexity
            const sizeMultiplier = parseFloat(item.size) > 1000 ? 0.5 : 1; // Slower for large files
            const complexityMultiplier =
              item.analysisType === "Full Match Analysis"
                ? 0.3
                : item.analysisType === "Tactical Analysis"
                  ? 0.6
                  : 1;
            const progressIncrement =
              Math.random() * 3 * sizeMultiplier * complexityMultiplier + 0.5;
            const newProgress = Math.min(
              100,
              item.progress + progressIncrement,
            );

            // Simulate stage transitions
            let newStage = item.processingStage;
            let newStatus: QueueItem["status"] = item.status;

            if (item.status === "uploading" && newProgress >= 100) {
              newStatus = "queued";
              newStage = "queue_waiting";
              return {
                ...item,
                status: newStatus,
                progress: 0,
                processingStage: newStage,
              };
            }

            if (item.status === "queued" && Math.random() > 0.7) {
              newStatus = "processing";
              newStage = "preprocessing";
              return {
                ...item,
                status: newStatus,
                progress: 5,
                processingStage: newStage,
              };
            }

            if (
              item.status === "processing" &&
              item.progress > 30 &&
              Math.random() > 0.8
            ) {
              newStatus = "analyzing";
              newStage = "video_analysis";
            }

            if (newProgress >= 100) {
              newStatus = "completed";
              newStage = "analysis_complete";
              return {
                ...item,
                status: newStatus,
                progress: 100,
                processingStage: newStage,
                completedTime: new Date().toISOString(),
                estimatedCompletion: null,
              };
            }

            // Realistic failure scenarios based on file characteristics
            const failureChance =
              parseFloat(item.size) > 2000
                ? 0.005 // Higher chance for very large files
                : item.analysisType === "Tactical Analysis"
                  ? 0.003 // Complex analysis more prone to failure
                  : item.retryCount > 0
                    ? 0.001 // Lower chance if already retried
                    : 0.002; // Base failure chance

            if (
              Math.random() < failureChance &&
              item.errorCount < 2 &&
              item.progress > 10
            ) {
              const errorReasons = [
                "insufficient_memory",
                "corrupted_segment",
                "processing_timeout",
                "unsupported_codec",
                "server_overload",
              ];
              return {
                ...item,
                status: "failed",
                processingStage:
                  errorReasons[Math.floor(Math.random() * errorReasons.length)],
                errorCount: item.errorCount + 1,
              };
            }

            return {
              ...item,
              progress: newProgress,
              status: newStatus,
              processingStage: newStage,
            };
          }
          return item;
        }),
      );
    }, 2000); // Update every 2 seconds

    return () => clearInterval(interval);
  }, []);

  // Check authentication on component mount
  useEffect(() => {
    const isAuthenticated = localStorage.getItem("isAuthenticated");
    const email = localStorage.getItem("userEmail");

    if (!isAuthenticated || isAuthenticated !== "true") {
      // Redirect to login if not authenticated
      navigate("/");
      return;
    }

    if (email) {
      setUserEmail(email);
    }
  }, [navigate]);

  // Logout function
  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
    navigate("/");
  };

  // Video upload handlers
  const handleVideoFileSelect = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = [
        "video/mp4",
        "video/mov",
        "video/avi",
        "video/quicktime",
      ];
      if (!validTypes.includes(file.type)) {
        setVideoAnalysisError(
          "Please select a valid video file (MP4, MOV, or AVI)",
        );
        return;
      }

      // Validate file size (max 500MB)
      const maxSize = 500 * 1024 * 1024; // 500MB in bytes
      if (file.size > maxSize) {
        setVideoAnalysisError("File size must be less than 500MB");
        return;
      }

      setSelectedVideoFile(file);
      setVideoAnalysisError(null);
      setVideoAnalysisComplete(false);
    }
  };

  const handleFocusAreaChange = (area: string, checked: boolean) => {
    if (checked) {
      setSelectedFocusAreas([...selectedFocusAreas, area]);
    } else {
      setSelectedFocusAreas(selectedFocusAreas.filter((a) => a !== area));
    }
  };

  const uploadAndAnalyzeVideo = async () => {
    if (!selectedVideoFile) {
      setVideoAnalysisError("Please select a video file first");
      return;
    }

    try {
      setVideoAnalysisError(null);
      setIsVideoUploading(true);
      setVideoUploadProgress(0);

      // Create queue item immediately when upload starts
      const newQueueItem: QueueItem = {
        id: `pq_${Date.now()}`,
        name: selectedVideoFile.name,
        analysisType:
          selectedAnalysisType === "highlights"
            ? "Highlight Generation"
            : selectedAnalysisType === "player"
              ? "Player Tracking"
              : selectedAnalysisType === "tactics"
                ? "Tactical Analysis"
                : selectedAnalysisType === "performance"
                  ? "Performance Analysis"
                  : "Crowd Analysis",
        status: "uploading",
        progress: 0,
        duration: `${Math.floor(Math.random() * 60 + 30)}:${Math.floor(
          Math.random() * 60,
        )
          .toString()
          .padStart(2, "0")}`,
        size: `${(selectedVideoFile.size / (1024 * 1024)).toFixed(1)} MB`,
        uploadTime: new Date().toISOString(),
        completedTime: null,
        estimatedCompletion: new Date(
          Date.now() + Math.random() * 600000 + 300000,
        ).toISOString(), // 5-15 minutes
        priority:
          selectedFocusAreas.length > 2
            ? "high"
            : Math.random() > 0.5
              ? "medium"
              : "low",
        userId: "current_user",
        processingStage: "file_upload",
        errorCount: 0,
        retryCount: 0,
        isUIControlled: true,
      };

      // Add to processing queue immediately
      setProcessingQueue((prev) => [newQueueItem, ...prev]);

      // Simulate file upload with real progress
      for (let i = 0; i <= 100; i += 5) {
        await new Promise((resolve) => setTimeout(resolve, 100));
        setVideoUploadProgress(i);

        // Update the queue item progress during upload
        setProcessingQueue((prev) =>
          prev.map((item) =>
            item.id === newQueueItem.id ? { ...item, progress: i } : item,
          ),
        );
      }

      setIsVideoUploading(false);
      setIsVideoAnalyzing(true);
      setVideoAnalysisProgress(0);

      // Move to queued status after upload completes
      setProcessingQueue((prev) =>
        prev.map((item) =>
          item.id === newQueueItem.id
            ? {
                ...item,
                status: "analyzing", // Start analyzing immediately since this is UI-controlled
                progress: 5,
                processingStage: "video_analysis",
              }
            : item,
        ),
      );

      // Complete the UI state and sync queue progress
      for (let i = 0; i <= 100; i += 2) {
        await new Promise((resolve) => setTimeout(resolve, 50));
        setVideoAnalysisProgress(i);

        // Update queue item progress to match UI progress
        setProcessingQueue((prev) =>
          prev.map((item) =>
            item.id === newQueueItem.id
              ? { ...item, progress: Math.max(5, i) } // Keep minimum 5% from earlier
              : item,
          ),
        );
      }

      setIsVideoAnalyzing(false);
      setVideoAnalysisComplete(true);

      // Mark the corresponding queue item as completed when UI analysis finishes
      setProcessingQueue((prev) =>
        prev.map((item) =>
          item.id === newQueueItem.id
            ? {
                ...item,
                status: "completed",
                progress: 100,
                processingStage: "analysis_complete",
                completedTime: new Date().toISOString(),
                estimatedCompletion: null,
              }
            : item,
        ),
      );

      // Store analysis results
      const analysisResults = {
        fileName: selectedVideoFile.name,
        analysisType: selectedAnalysisType,
        focusAreas: selectedFocusAreas,
        timestamp: new Date().toISOString(),
        fileSize: selectedVideoFile.size,
      };

      const existingAnalyses = JSON.parse(
        localStorage.getItem("videoAnalyses") || "[]",
      );
      localStorage.setItem(
        "videoAnalyses",
        JSON.stringify([...existingAnalyses, analysisResults]),
      );
    } catch (error) {
      setIsVideoUploading(false);
      setIsVideoAnalyzing(false);
      setVideoAnalysisError(
        error instanceof Error ? error.message : "Upload failed",
      );

      // Mark the queue item as failed if there was an error
      setProcessingQueue((prev) =>
        prev.map((item) =>
          item.name === selectedVideoFile?.name && item.status === "uploading"
            ? {
                ...item,
                status: "failed",
                processingStage: "upload_error",
                errorCount: 1,
              }
            : item,
        ),
      );
    }
  };

  // Generate dynamic summaries for dashboard reports
  const generateDynamicDashboardSummary = (
    insights: any,
    analysisType: string,
    focusAreas: string[],
  ) => {
    const totalAttendance = insights.crowdDensity.reduce(
      (sum: number, section: any) => sum + section.attendance,
      0,
    );
    const topPlayer = insights.playerStats.reduce((best: any, current: any) =>
      parseFloat(current.efficiency) > parseFloat(best.efficiency)
        ? current
        : best,
    );
    const avgCrowdDensity = (
      insights.crowdDensity.reduce(
        (sum: number, section: any) => sum + parseFloat(section.density),
        0,
      ) / insights.crowdDensity.length
    ).toFixed(1);

    return {
      overview: `Comprehensive analysis of ${totalAttendance.toLocaleString()} attendees across ${insights.crowdDensity.length} stadium sections with ${focusAreas.length || "general"} focus areas.`,
      performance: `Top performer: ${topPlayer.name} achieved ${topPlayer.efficiency}% efficiency with ${topPlayer.goals} goals and ${topPlayer.tackles} tackles.`,
      crowd: `Stadium operated at ${avgCrowdDensity}% average density with peak engagement in ${
        insights.crowdDensity.reduce((max: any, section: any) =>
          parseFloat(section.density) > parseFloat(max.density) ? section : max,
        ).section
      }.`,
      analysis:
        analysisType === "highlights"
          ? `Key highlight moments identified with real-time crowd correlation analysis.`
          : analysisType === "player"
            ? `Individual player tracking completed for ${insights.playerStats.length} athletes with speed and positioning data.`
            : analysisType === "tactics"
              ? `Tactical formations and strategic patterns analyzed throughout the match.`
              : analysisType === "performance"
                ? `Comprehensive performance metrics calculated for all tracked players.`
                : `Crowd engagement patterns analyzed across all stadium sections.`,
    };
  };

  // PDF generation for dashboard reports
  const generateDashboardPDF = (content: string, fileName: string) => {
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
  const generateDashboardInsights = () => {
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

  // Simulate getting JSON data from backend
  const fetchBackendAnalysisData = async (analysisId: string) => {
    // Simulate backend JSON response
    return {
      analysisId,
      timestamp: new Date().toISOString(),
      videoFile: {
        name: selectedVideoFile?.name || "sample_video.mp4",
        duration: "02:15:30",
        size: "1.8 GB",
        resolution: "1920x1080",
        framerate: "30fps",
      },
      analysisType: selectedAnalysisType,
      focusAreas: selectedFocusAreas,
      processingTime: Math.floor(Math.random() * 300 + 120),
      results: {
        playerPerformance: [
          {
            playerId: "p001",
            name: "Marcus Bontempelli",
            team: "Western Bulldogs",
            position: "Midfielder",
            statistics: {
              speed: { max: 32.4, average: 24.8, unit: "km/h" },
              distance: { total: 12.8, sprints: 2.3, unit: "km" },
              touches: { total: 28, effective: 24, efficiency: 85.7 },
              goals: 2,
              assists: 3,
              tackles: 6,
              marks: 8,
              disposals: 31,
              timeOnGround: 87.5,
            },
          },
          {
            playerId: "p002",
            name: "Patrick Cripps",
            team: "Carlton",
            position: "Midfielder",
            statistics: {
              speed: { max: 29.8, average: 22.1, unit: "km/h" },
              distance: { total: 13.2, sprints: 1.8, unit: "km" },
              touches: { total: 35, effective: 31, efficiency: 88.6 },
              goals: 1,
              assists: 5,
              tackles: 9,
              marks: 6,
              disposals: 34,
              timeOnGround: 92.3,
            },
          },
        ],
        crowdAnalysis: {
          totalAttendance: 47832,
          capacity: 50000,
          utilizationRate: 95.7,
          sections: [
            {
              sectionId: "north_stand",
              name: "Northern Stand",
              attendance: 14250,
              capacity: 15000,
              density: 95.0,
              noiseLevel: { peak: 95.2, average: 78.4, unit: "dB" },
            },
            {
              sectionId: "south_stand",
              name: "Southern Stand",
              attendance: 11680,
              capacity: 12000,
              density: 97.3,
              noiseLevel: { peak: 92.8, average: 76.9, unit: "dB" },
            },
          ],
        },
        highlights: [
          {
            timestamp: "00:03:45",
            duration: 15,
            type: "goal",
            description: "Opening goal with crowd eruption",
            players: ["Marcus Bontempelli"],
            confidence: 0.94,
          },
        ],
        metadata: {
          confidence: 0.923,
          processingVersion: "2.1.3",
          qualityScore: 8.7,
        },
      },
    };
  };

  // Convert backend JSON to formatted text
  const convertBackendDataToText = (data: any) => {
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
  const convertBackendDataToHTML = (data: any) => {
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

  // Download handlers for reports with backend JSON processing
  const handleDownloadReport = async (
    format: "pdf" | "json" | "txt" = "txt",
  ) => {
    if (!videoAnalysisComplete || !selectedVideoFile) {
      alert("Please complete video analysis first");
      return;
    }

    try {
      // Fetch JSON data from backend
      const analysisId = `analysis_${Date.now()}`;
      const backendData = await fetchBackendAnalysisData(analysisId);

      if (format === "json") {
        // Download raw JSON data
        const jsonContent = JSON.stringify(backendData, null, 2);
        const blob = new Blob([jsonContent], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `AFL_Analysis_${analysisId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else if (format === "pdf") {
        // Generate PDF from backend data
        const htmlContent = convertBackendDataToHTML(backendData);
        generateDashboardPDF(htmlContent, `AFL_Analysis_${analysisId}`);
      } else {
        // Generate TXT from backend data
        const textContent = convertBackendDataToText(backendData);
        downloadText(textContent, `AFL_Analysis_${analysisId}`);
      }
    } catch (error) {
      console.error("Error generating report:", error);
      alert("Failed to generate report. Please try again.");
    }
  };

  const handleDownloadVideoClips = () => {
    if (!videoAnalysisComplete) {
      alert("Please complete video analysis first");
      return;
    }

    const insights = generateDashboardInsights();
    const clipEvents = [
      {
        time: "00:03:45",
        event: "Opening Goal",
        player: insights.playerStats[0].name,
        speed: insights.playerStats[0].speed,
        crowd: "Explosive reaction",
      },
      {
        time: "00:18:23",
        event: "Spectacular Mark",
        player: insights.playerStats[1].name,
        speed: insights.playerStats[1].speed,
        crowd: "Standing ovation",
      },
      {
        time: "00:34:56",
        event: "Crucial Tackle",
        player: insights.playerStats[2].name,
        speed: insights.playerStats[2].speed,
        crowd: "Defensive roar",
      },
      {
        time: "00:52:12",
        event: "Assist Play",
        player: insights.playerStats[3].name,
        speed: insights.playerStats[3].speed,
        crowd: "Building excitement",
      },
      {
        time: "01:08:34",
        event: "Match Winner",
        player: insights.playerStats[4].name,
        speed: insights.playerStats[4].speed,
        crowd: "Stadium eruption",
      },
      {
        time: "01:15:45",
        event: "Final Siren",
        player: "Multiple Players",
        speed: "N/A",
        crowd: "Celebration frenzy",
      },
    ];

    const clipsData = `AFL ANALYTICS VIDEO CLIPS EXPORT

Generated: ${new Date().toLocaleString()}
Source Video: ${selectedVideoFile?.name}
Analysis Type: ${
      selectedAnalysisType === "highlights"
        ? "Match Highlights"
        : selectedAnalysisType === "player"
          ? "Player Tracking"
          : selectedAnalysisType === "tactics"
            ? "Tactical Analysis"
            : selectedAnalysisType === "performance"
              ? "Performance Metrics"
              : "Crowd Reactions"
    }

════════════════════���══════════════════════════════����══════

EXTRACTED VIDEO CLIPS WITH INSIGHTS
===================================
${clipEvents
  .map(
    (clip, index) => `
Clip ${index + 1}: ${clip.event}
  • Timestamp: ${clip.time}
  • Featured Player: ${clip.player}
  • Player Speed: ${clip.speed} km/h
  • Duration: ${Math.floor(Math.random() * 25 + 10)}s
  • Crowd Reaction: ${clip.crowd}
  • Stands Most Active: ${insights.crowdDensity[Math.floor(Math.random() * insights.crowdDensity.length)].section}
  • Noise Level: ${(85 + Math.random() * 15).toFixed(1)} dB
`,
  )
  .join("")}

CLIP ANALYSIS SUMMARY
====================
• Total clips identified: ${clipEvents.length}
• Total duration: ${clipEvents.reduce((sum, _, index) => sum + Math.floor(Math.random() * 25 + 10), 0)} seconds
• Average crowd noise: ${(80 + Math.random() * 20).toFixed(1)} dB
• Most active stand: ${
      insights.crowdDensity.reduce((max, section) =>
        parseFloat(section.density) > parseFloat(max.density) ? section : max,
      ).section
    }
• Player tracking accuracy: 97.2%

CROWD RESPONSE CORRELATION
==========================
${clipEvents
  .map(
    (clip, index) => `
${clip.event} (${clip.time}):
  Crowd Response Intensity: ${(7 + Math.random() * 3).toFixed(1)}/10
  Stands Reacting: ${Math.floor(Math.random() * 3 + 3)} of ${insights.crowdDensity.length}
  Duration of Reaction: ${Math.floor(Math.random() * 15 + 5)}s
`,
  )
  .join("")}

EXPORT DETAILS
==============
• Export Format: Metadata Analysis (TXT)
• Processing Time: ${Math.floor(Math.random() * 3 + 1)} minutes
• Clips Ready for Download: ${clipEvents.length}
• Analysis Confidence: 94.8%

NOTE: In a production environment, this would package actual video clip files.
Currently providing comprehensive metadata and analysis for demonstration.

Generated by AFL Analytics Platform - Advanced Video Intelligence
Export ID: ${Date.now()}-${Math.random().toString(36).substr(2, 9)}
`;

    downloadText(clipsData, `AFL_Video_Clips_${Date.now()}`);
  };

  // Player cards data
  const playerCards = [
    {
      id: 1,
      name: "DAYNE ZORKO",
      team: "Brisbane Lions",
      number: 7,
      background: "from-red-800 to-red-900",
      image:
        "https://images.pexels.com/photos/159666/rugby-runner-player-running-159666.jpeg",
      stats: {
        goalAccuracy: 67,
        handballs: 16,
        disposals: 34,
        kicks: 18,
        marks: 8,
        tackles: 6,
      },
    },
    {
      id: 2,
      name: "MARCUS BONTEMPELLI",
      team: "Western Bulldogs",
      number: 4,
      background: "from-orange-600 to-orange-700",
      image:
        "https://images.pexels.com/photos/159555/soccer-football-athlete-player-159555.jpeg",
      stats: {
        goalAccuracy: 60,
        handballs: 18,
        disposals: 42,
        kicks: 24,
        marks: 10,
        tackles: 8,
      },
    },
    {
      id: 3,
      name: "PATRICK CRIPPS",
      team: "Carlton",
      number: 9,
      background: "from-blue-800 to-blue-900",
      image: "https://images.pexels.com/photos/209961/pexels-photo-209961.jpeg",
      stats: {
        goalAccuracy: 100,
        handballs: 12,
        disposals: 38,
        kicks: 26,
        marks: 7,
        tackles: 9,
      },
    },
    {
      id: 4,
      name: "DUSTIN MARTIN",
      team: "Richmond",
      number: 3,
      background: "from-yellow-500 to-yellow-600",
      image:
        "https://images.pexels.com/photos/159684/soccer-football-soccer-player-sport-159684.jpeg",
      stats: {
        goalAccuracy: 80,
        handballs: 8,
        disposals: 28,
        kicks: 20,
        marks: 6,
        tackles: 4,
      },
    },
  ];

  // Player comparison chart data
  const playerComparisonData = [
    {
      stat: "Kicks",
      [selectedPlayer.name]: selectedPlayer.kicks,
      [comparisonPlayer.name]: comparisonPlayer.kicks,
    },
    {
      stat: "Handballs",
      [selectedPlayer.name]: selectedPlayer.handballs,
      [comparisonPlayer.name]: comparisonPlayer.handballs,
    },
    {
      stat: "Marks",
      [selectedPlayer.name]: selectedPlayer.marks,
      [comparisonPlayer.name]: comparisonPlayer.marks,
    },
    {
      stat: "Tackles",
      [selectedPlayer.name]: selectedPlayer.tackles,
      [comparisonPlayer.name]: comparisonPlayer.tackles,
    },
    {
      stat: "Goals",
      [selectedPlayer.name]: selectedPlayer.goals,
      [comparisonPlayer.name]: comparisonPlayer.goals,
    },
    {
      stat: "Efficiency",
      [selectedPlayer.name]: selectedPlayer.efficiency,
      [comparisonPlayer.name]: comparisonPlayer.efficiency,
    },
  ];

  const filteredPlayers = mockPlayers.filter(
    (player) =>
      player.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedTeam === "all" || player.team === selectedTeam),
  );

  // Handle card click
  const handleCardClick = (card, index) => {
    setSelectedCard(card);
    setSelectedCardIndex(index);
    // Toggle expanded state
    setExpandedCardId(expandedCardId === card.id ? null : card.id);
  };

  // Initialize selectedCard when component mounts
  useEffect(() => {
    if (playerCards.length > 0 && !selectedCard) {
      setSelectedCard(playerCards[0]);
    }
  }, [playerCards, selectedCard]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                  AFL Analytics
                </h1>
                <p className="text-sm text-gray-600">
                  Real-time match insights & player analytics
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge
                variant={isLive ? "destructive" : "secondary"}
                className="animate-pulse"
              >
                <div className="w-2 h-2 rounded-full bg-red-500 mr-2" />
                {isLive ? "LIVE" : "OFFLINE"}
              </Badge>
              {userEmail && (
                <span className="text-sm text-gray-600 hidden sm:block">
                  Welcome, {userEmail}
                </span>
              )}
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="video" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger
              value="performance"
              className="flex items-center gap-2"
            >
              <BarChart3 className="w-4 h-4" />
              Player Performance
            </TabsTrigger>
            <TabsTrigger value="crowd" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Crowd Monitor
            </TabsTrigger>
            <TabsTrigger value="reports" className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              Reports
            </TabsTrigger>
            <TabsTrigger value="team" className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              Team Match
            </TabsTrigger>
            <TabsTrigger value="video" className="flex items-center gap-2">
              <Video className="w-4 h-4" />
              Video Analysis
            </TabsTrigger>
          </TabsList>

          {/* Team Match Performance */}
          <TabsContent value="team" className="space-y-6">
            {/* Filters */}
            <div className="bg-white border rounded-lg p-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-stretch">
                <div className="sm:col-span-1">
                  <Input
                    placeholder="Search team, venue..."
                    value={teamSearch}
                    onChange={(e) => setTeamSearch(e.target.value)}
                  />
                </div>
                <div className="sm:col-span-1">
                  <Select value={teamFilter} onValueChange={setTeamFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Team" />
                    </SelectTrigger>
                    <SelectContent>
                      {teamTeams.map((t) => (
                        <SelectItem key={t} value={t}>
                          {t === "all" ? "All Teams" : t}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="sm:col-span-1">
                  <Select value={teamRound} onValueChange={setTeamRound}>
                    <SelectTrigger>
                      <SelectValue placeholder="Round" />
                    </SelectTrigger>
                    <SelectContent>
                      {teamRounds.map((r) => (
                        <SelectItem key={r} value={r}>
                          {r === "all" ? "All Rounds" : r}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* Summary */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-gray-600">Matches</div>
                  <div className="text-2xl font-semibold">{teamSummary.games}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-gray-600">Total Goals</div>
                  <div className="text-2xl font-semibold">{teamSummary.goals}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-gray-600">Total Disposals</div>
                  <div className="text-2xl font-semibold">{teamSummary.disposals.toLocaleString()}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-gray-600">Inside 50s</div>
                  <div className="text-2xl font-semibold">{teamSummary.inside50}</div>
                </CardContent>
              </Card>
            </div>

            {/* Compare Teams */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Compare Teams
                </CardTitle>
                <CardDescription>Select two teams to compare totals across listed matches</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <Select value={teamA} onValueChange={setTeamA}>
                      <SelectTrigger>
                        <SelectValue placeholder="Team A" />
                      </SelectTrigger>
                      <SelectContent>
                        {teamTeams.filter(t=>t!=="all").map((t) => (
                          <SelectItem key={t} value={t}>{t}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Select value={teamB} onValueChange={setTeamB}>
                      <SelectTrigger>
                        <SelectValue placeholder="Team B" />
                      </SelectTrigger>
                      <SelectContent>
                        {teamTeams.filter(t=>t!=="all").map((t) => (
                          <SelectItem key={t} value={t}>{t}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center">
                    <Badge variant="outline" className="w-full justify-center">
                      {teamA !== "all" && teamB !== "all" && teamA !== teamB ? "Ready" : "Select two different teams"}
                    </Badge>
                  </div>
                </div>

                {teamA !== "all" && teamB !== "all" && teamA !== teamB && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <TeamCompareBar label="Goals" aLabel={teamA} aValue={teamCompare.a.goals} bLabel={teamB} bValue={teamCompare.b.goals} />
                    <TeamCompareBar label="Disposals" aLabel={teamA} aValue={teamCompare.a.disposals} bLabel={teamB} bValue={teamCompare.b.disposals} />
                    <TeamCompareBar label="Marks" aLabel={teamA} aValue={teamCompare.a.marks} bLabel={teamB} bValue={teamCompare.b.marks} />
                    <TeamCompareBar label="Tackles" aLabel={teamA} aValue={teamCompare.a.tackles} bLabel={teamB} bValue={teamCompare.b.tackles} />
                    <TeamCompareBar label="Inside 50" aLabel={teamA} aValue={teamCompare.a.inside50} bLabel={teamB} bValue={teamCompare.b.inside50} />
                    <TeamCompareBar label="Avg Efficiency %" aLabel={teamA} aValue={teamCompare.aEff} bLabel={teamB} bValue={teamCompare.bEff} />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Matches list */}
            <div className="grid grid-cols-1 gap-4">
              {teamFiltered.map((m) => {
                const homePoints = m.stats.home.goals * 6 + m.stats.home.behinds;
                const awayPoints = m.stats.away.goals * 6 + m.stats.away.behinds;
                const winPct = Math.min(100, Math.max(0, Math.round((homePoints / (homePoints + awayPoints || 1)) * 100)));
                return (
                  <Card key={m.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Flag className="w-4 h-4 text-blue-600" />
                          <CardTitle className="text-base">
                            {m.teams.home} vs {m.teams.away}
                          </CardTitle>
                        </div>
                        <Badge variant="outline">{m.round}</Badge>
                      </div>
                      <CardDescription>
                        {m.venue} • {new Date(m.date).toLocaleDateString()}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                        <div className="space-y-1">
                          <div className="text-sm text-gray-600">Score</div>
                          <div className="text-2xl font-semibold">
                            {homePoints} - {awayPoints}
                          </div>
                          <div className="text-xs text-gray-500">
                            {m.stats.home.goals}.{m.stats.home.behinds} vs {m.stats.away.goals}.{m.stats.away.behinds}
                          </div>
                        </div>
                        <div className="md:col-span-2">
                          <div className="text-sm text-gray-600 mb-1">Win Probability ({m.teams.home})</div>
                          <Progress value={winPct} />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <TeamCompareBar label="Disposals" aLabel={m.teams.home} aValue={m.stats.home.disposals} bLabel={m.teams.away} bValue={m.stats.away.disposals} />
                        <TeamCompareBar label="Marks" aLabel={m.teams.home} aValue={m.stats.home.marks} bLabel={m.teams.away} bValue={m.stats.away.marks} />
                        <TeamCompareBar label="Tackles" aLabel={m.teams.home} aValue={m.stats.home.tackles} bLabel={m.teams.away} bValue={m.stats.away.tackles} />
                        <TeamCompareBar label="Clearances" aLabel={m.teams.home} aValue={m.stats.home.clearances} bLabel={m.teams.away} bValue={m.stats.away.clearances} />
                        <TeamCompareBar label="Inside 50" aLabel={m.teams.home} aValue={m.stats.home.inside50} bLabel={m.teams.away} bValue={m.stats.away.inside50} />
                        <TeamCompareBar label="Efficiency %" aLabel={m.teams.home} aValue={m.stats.home.efficiency} bLabel={m.teams.away} bValue={m.stats.away.efficiency} />
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          {/* Player Performance Tracker */}
          <TabsContent value="performance" className="space-y-6">
            <div className="flex flex-col lg:flex-row gap-6">
              {/* Search and Filters */}
              <Card className="lg:w-1/3">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Search className="w-5 h-5" />
                    Player Search & Filters
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">
                      Search Players
                    </label>
                    <Input
                      placeholder="Search by name..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">
                      Filter by Team
                    </label>
                    <Select
                      value={selectedTeam}
                      onValueChange={setSelectedTeam}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select team" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Teams</SelectItem>
                        <SelectItem value="Western Bulldogs">
                          Western Bulldogs
                        </SelectItem>
                        <SelectItem value="Richmond">Richmond</SelectItem>
                        <SelectItem value="Geelong">Geelong</SelectItem>
                        <SelectItem value="Melbourne">Melbourne</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {filteredPlayers.map((player) => (
                      <div
                        key={player.id}
                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                          selectedPlayer.id === player.id
                            ? "border-blue-500 bg-blue-50"
                            : "border-gray-200 hover:border-gray-300"
                        }`}
                        onClick={() => setSelectedPlayer(player)}
                      >
                        <div className="font-medium">{player.name}</div>
                        <div className="text-sm text-gray-600">
                          {player.team} ��� {player.position}
                        </div>
                        <div className="text-xs text-green-600 mt-1">
                          Efficiency: {player.efficiency}%
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Player Statistics */}
              <div className="lg:w-2/3 space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>Player Statistics - {selectedPlayer.name}</span>
                      <Badge variant="outline">{selectedPlayer.team}</Badge>
                    </CardTitle>
                    <CardDescription>{selectedPlayer.position}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {selectedPlayer.kicks}
                        </div>
                        <div className="text-sm text-gray-600">Kicks</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {selectedPlayer.handballs}
                        </div>
                        <div className="text-sm text-gray-600">Handballs</div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {selectedPlayer.marks}
                        </div>
                        <div className="text-sm text-gray-600">Marks</div>
                      </div>
                      <div className="text-center p-4 bg-orange-50 rounded-lg">
                        <div className="text-2xl font-bold text-orange-600">
                          {selectedPlayer.tackles}
                        </div>
                        <div className="text-sm text-gray-600">Tackles</div>
                      </div>
                      <div className="text-center p-4 bg-red-50 rounded-lg">
                        <div className="text-2xl font-bold text-red-600">
                          {selectedPlayer.goals}
                        </div>
                        <div className="text-sm text-gray-600">Goals</div>
                      </div>
                      <div className="text-center p-4 bg-yellow-50 rounded-lg">
                        <div className="text-2xl font-bold text-yellow-600">
                          {selectedPlayer.efficiency}%
                        </div>
                        <div className="text-sm text-gray-600">Efficiency</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* AFL Trading Cards */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Activity className="w-5 h-5" />
                        Player Profiles
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowAllCards(!showAllCards)}
                      >
                        {showAllCards ? "Show One" : "View All"}
                      </Button>
                    </CardTitle>
                    <CardDescription>
                      View AFL player profiles with stats and performance data
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {showAllCards ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {playerCards.map((card, index) => {
                          const isExpanded = expandedCardId === card.id;
                          return (
                            <div
                              key={card.id}
                              className={`relative w-full mx-auto cursor-pointer transform transition-all duration-500 hover:shadow-xl ${
                                isExpanded
                                  ? "col-span-full max-w-2xl scale-105 z-10"
                                  : "max-w-xs hover:scale-105"
                              }`}
                              onClick={() => handleCardClick(card, index)}
                            >
                              <div className="absolute top-3 left-3 z-20">
                                <div className="bg-white rounded-full p-2 shadow-md">
                                  <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                                    <span className="text-white font-bold text-xs">
                                      AFL
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <div className="absolute top-3 right-3 z-20">
                                <div className="bg-black/70 text-white px-2 py-1 rounded text-sm font-bold">
                                  #{card.number}
                                </div>
                              </div>
                              {isExpanded && (
                                <div className="absolute top-3 left-1/2 transform -translate-x-1/2 z-20">
                                  <div className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-bold animate-pulse">
                                    EXPANDED VIEW
                                  </div>
                                </div>
                              )}
                              <div
                                className={`relative rounded-lg overflow-hidden shadow-lg border-2 bg-gradient-to-b ${card.background} transition-all duration-500 ${
                                  isExpanded
                                    ? "h-[500px] border-green-400"
                                    : "h-80 border-gray-200"
                                }`}
                              >
                                <img
                                  src={card.image}
                                  alt={card.name}
                                  className={`w-full h-full object-cover transition-opacity duration-500 ${
                                    isExpanded ? "opacity-95" : "opacity-80"
                                  }`}
                                />
                                <div
                                  className={`absolute inset-0 bg-gradient-to-b transition-opacity duration-500 ${
                                    isExpanded
                                      ? "from-transparent via-black/20 to-black/90"
                                      : "from-transparent via-transparent to-black/80"
                                  }`}
                                />
                                <div
                                  className={`absolute left-3 right-3 z-10 transition-all duration-500 ${
                                    isExpanded ? "top-16" : "top-12"
                                  }`}
                                >
                                  <h3
                                    className={`text-white font-bold leading-tight transition-all duration-500 ${
                                      isExpanded ? "text-2xl" : "text-lg"
                                    }`}
                                  >
                                    {card.name}
                                  </h3>
                                  <p
                                    className={`text-white/80 transition-all duration-500 ${
                                      isExpanded ? "text-lg" : "text-sm"
                                    }`}
                                  >
                                    {card.team}
                                  </p>
                                  {isExpanded && (
                                    <div className="mt-3 flex gap-2 opacity-0 animate-[fadeIn_0.5s_ease-in-out_0.3s_forwards]">
                                      <div className="px-2 py-1 bg-white/20 backdrop-blur-sm rounded text-white text-xs">
                                        🏆 Season MVP
                                      </div>
                                      <div className="px-2 py-1 bg-white/20 backdrop-blur-sm rounded text-white text-xs">
                                        ��� Top Performer
                                      </div>
                                    </div>
                                  )}
                                </div>
                                <div
                                  className={`absolute left-3 right-3 z-10 transition-all duration-500 ${
                                    isExpanded ? "bottom-32" : "bottom-16"
                                  }`}
                                >
                                  <div
                                    className={`bg-black/80 backdrop-blur-sm rounded transition-all duration-500 ${
                                      isExpanded ? "p-4" : "p-3"
                                    }`}
                                  >
                                    <div
                                      className={`text-white space-y-1 transition-all duration-500 ${
                                        isExpanded ? "text-sm" : "text-xs"
                                      }`}
                                    >
                                      <div className="flex justify-between">
                                        <span>GOAL ACCURACY:</span>
                                        <span className="font-bold">
                                          {card.stats.goalAccuracy}%
                                        </span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span>HANDBALLS:</span>
                                        <span className="font-bold">
                                          {card.stats.handballs}
                                        </span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span>DISPOSALS:</span>
                                        <span className="font-bold">
                                          {card.stats.disposals}
                                        </span>
                                      </div>
                                      {isExpanded && (
                                        <div className="opacity-0 animate-[fadeIn_0.5s_ease-in-out_0.4s_forwards]">
                                          <div className="border-t border-white/20 my-2"></div>
                                          <div className="flex justify-between">
                                            <span>EFFICIENCY:</span>
                                            <span className="font-bold">
                                              87%
                                            </span>
                                          </div>
                                          <div className="flex justify-between">
                                            <span>CONTESTED MARKS:</span>
                                            <span className="font-bold">4</span>
                                          </div>
                                          <div className="flex justify-between">
                                            <span>INTERCEPTS:</span>
                                            <span className="font-bold">3</span>
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                                <div
                                  className={`absolute bottom-0 left-0 right-0 bg-gradient-to-r from-red-600 to-red-700 z-10 transition-all duration-500 ${
                                    isExpanded ? "p-4" : "p-3"
                                  }`}
                                >
                                  <div
                                    className={`grid grid-cols-3 gap-2 text-white text-center transition-all duration-500 ${
                                      isExpanded ? "mb-2" : ""
                                    }`}
                                  >
                                    <div>
                                      <div
                                        className={`font-bold transition-all duration-500 ${
                                          isExpanded ? "text-xl" : "text-lg"
                                        }`}
                                      >
                                        {card.stats.kicks}
                                      </div>
                                      <div
                                        className={`transition-all duration-500 ${
                                          isExpanded ? "text-sm" : "text-xs"
                                        }`}
                                      >
                                        KICKS
                                      </div>
                                    </div>
                                    <div>
                                      <div
                                        className={`font-bold transition-all duration-500 ${
                                          isExpanded ? "text-xl" : "text-lg"
                                        }`}
                                      >
                                        {card.stats.marks}
                                      </div>
                                      <div
                                        className={`transition-all duration-500 ${
                                          isExpanded ? "text-sm" : "text-xs"
                                        }`}
                                      >
                                        MARKS
                                      </div>
                                    </div>
                                    <div>
                                      <div
                                        className={`font-bold transition-all duration-500 ${
                                          isExpanded ? "text-xl" : "text-lg"
                                        }`}
                                      >
                                        {card.stats.tackles}
                                      </div>
                                      <div
                                        className={`transition-all duration-500 ${
                                          isExpanded ? "text-sm" : "text-xs"
                                        }`}
                                      >
                                        TACKLES
                                      </div>
                                    </div>
                                  </div>
                                  {isExpanded && (
                                    <div className="text-center text-white/80 text-xs opacity-0 animate-[fadeIn_0.5s_ease-in-out_0.5s_forwards]">
                                      Click again to collapse • Background image
                                      now more visible
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <div className="flex flex-col items-center space-y-4">
                        <div className="flex items-center space-x-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const newIndex = Math.max(
                                0,
                                selectedCardIndex - 1,
                              );
                              setSelectedCardIndex(newIndex);
                              setSelectedCard(playerCards[newIndex]);
                            }}
                            disabled={selectedCardIndex === 0}
                          >
                            ← Previous
                          </Button>
                          <span className="text-sm text-gray-600">
                            {selectedCardIndex + 1} of {playerCards.length}
                          </span>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const newIndex = Math.min(
                                playerCards.length - 1,
                                selectedCardIndex + 1,
                              );
                              setSelectedCardIndex(newIndex);
                              setSelectedCard(playerCards[newIndex]);
                            }}
                            disabled={
                              selectedCardIndex === playerCards.length - 1
                            }
                          >
                            Next →
                          </Button>
                        </div>

                        <div
                          className={`relative w-full mx-auto cursor-pointer transform transition-all duration-500 hover:shadow-xl ${
                            expandedCardId === playerCards[selectedCardIndex].id
                              ? "max-w-2xl scale-105"
                              : "max-w-sm hover:scale-105"
                          }`}
                          onClick={() =>
                            handleCardClick(
                              playerCards[selectedCardIndex],
                              selectedCardIndex,
                            )
                          }
                        >
                          {(() => {
                            const card = playerCards[selectedCardIndex];
                            const isExpanded = expandedCardId === card.id;
                            return (
                              <>
                                <div className="absolute top-3 left-3 z-20">
                                  <div className="bg-white rounded-full p-2 shadow-md">
                                    <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                                      <span className="text-white font-bold text-xs">
                                        AFL
                                      </span>
                                    </div>
                                  </div>
                                </div>
                                <div className="absolute top-3 right-3 z-20">
                                  <div className="bg-black/70 text-white px-2 py-1 rounded text-sm font-bold">
                                    #{card.number}
                                  </div>
                                </div>
                                {isExpanded && (
                                  <div className="absolute top-3 left-1/2 transform -translate-x-1/2 z-20">
                                    <div className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-bold animate-pulse">
                                      EXPANDED VIEW
                                    </div>
                                  </div>
                                )}
                                <div
                                  className={`relative rounded-lg overflow-hidden shadow-lg border-2 bg-gradient-to-b ${card.background} transition-all duration-500 ${
                                    isExpanded
                                      ? "h-[600px] border-green-400"
                                      : "h-96 border-gray-200"
                                  }`}
                                >
                                  <img
                                    src={card.image}
                                    alt={card.name}
                                    className={`w-full h-full object-cover transition-opacity duration-500 ${
                                      isExpanded ? "opacity-95" : "opacity-80"
                                    }`}
                                  />
                                  <div
                                    className={`absolute inset-0 bg-gradient-to-b transition-opacity duration-500 ${
                                      isExpanded
                                        ? "from-transparent via-black/20 to-black/90"
                                        : "from-transparent via-transparent to-black/80"
                                    }`}
                                  />
                                  <div
                                    className={`absolute left-3 right-3 z-10 transition-all duration-500 ${
                                      isExpanded ? "top-16" : "top-12"
                                    }`}
                                  >
                                    <h3
                                      className={`text-white font-bold leading-tight transition-all duration-500 ${
                                        isExpanded ? "text-3xl" : "text-xl"
                                      }`}
                                    >
                                      {card.name}
                                    </h3>
                                    <p
                                      className={`text-white/80 transition-all duration-500 ${
                                        isExpanded ? "text-xl" : "text-base"
                                      }`}
                                    >
                                      {card.team}
                                    </p>
                                    {isExpanded && (
                                      <div className="mt-4 flex gap-3 opacity-0 animate-[fadeIn_0.5s_ease-in-out_0.3s_forwards]">
                                        <div className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded text-white text-sm">
                                          🏆 Season MVP
                                        </div>
                                        <div className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded text-white text-sm">
                                          ⭐ Top Performer
                                        </div>
                                        <div className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded text-white text-sm">
                                          💪 Best Midfielder
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                  <div
                                    className={`absolute left-3 right-3 z-10 transition-all duration-500 ${
                                      isExpanded ? "bottom-40" : "bottom-20"
                                    }`}
                                  >
                                    <div
                                      className={`bg-black/80 backdrop-blur-sm rounded transition-all duration-500 ${
                                        isExpanded ? "p-6" : "p-4"
                                      }`}
                                    >
                                      <div
                                        className={`text-white space-y-2 transition-all duration-500 ${
                                          isExpanded ? "text-base" : "text-sm"
                                        }`}
                                      >
                                        <div className="flex justify-between">
                                          <span>GOAL ACCURACY:</span>
                                          <span className="font-bold">
                                            {card.stats.goalAccuracy}%
                                          </span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span>HANDBALLS:</span>
                                          <span className="font-bold">
                                            {card.stats.handballs}
                                          </span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span>DISPOSALS:</span>
                                          <span className="font-bold">
                                            {card.stats.disposals}
                                          </span>
                                        </div>
                                        {isExpanded && (
                                          <div className="opacity-0 animate-[fadeIn_0.5s_ease-in-out_0.4s_forwards]">
                                            <div className="border-t border-white/20 my-3"></div>
                                            <div className="grid grid-cols-2 gap-4">
                                              <div className="flex justify-between">
                                                <span>EFFICIENCY:</span>
                                                <span className="font-bold">
                                                  87%
                                                </span>
                                              </div>
                                              <div className="flex justify-between">
                                                <span>INTERCEPTS:</span>
                                                <span className="font-bold">
                                                  3
                                                </span>
                                              </div>
                                              <div className="flex justify-between">
                                                <span>CONTESTED MARKS:</span>
                                                <span className="font-bold">
                                                  4
                                                </span>
                                              </div>
                                              <div className="flex justify-between">
                                                <span>ONE PERCENTERS:</span>
                                                <span className="font-bold">
                                                  7
                                                </span>
                                              </div>
                                            </div>
                                            <div className="border-t border-white/20 mt-3 pt-3">
                                              <div className="text-center">
                                                <span className="text-white/70 text-sm">
                                                  MATCH RATING
                                                </span>
                                                <div className="text-yellow-400 text-2xl font-bold">
                                                  ★ 9.2/10
                                                </div>
                                              </div>
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                  <div
                                    className={`absolute bottom-0 left-0 right-0 bg-gradient-to-r from-red-600 to-red-700 z-10 transition-all duration-500 ${
                                      isExpanded ? "p-6" : "p-4"
                                    }`}
                                  >
                                    <div
                                      className={`grid grid-cols-3 gap-2 text-white text-center transition-all duration-500 ${
                                        isExpanded ? "mb-3" : ""
                                      }`}
                                    >
                                      <div>
                                        <div
                                          className={`font-bold transition-all duration-500 ${
                                            isExpanded ? "text-2xl" : "text-xl"
                                          }`}
                                        >
                                          {card.stats.kicks}
                                        </div>
                                        <div
                                          className={`transition-all duration-500 ${
                                            isExpanded ? "text-base" : "text-sm"
                                          }`}
                                        >
                                          KICKS
                                        </div>
                                      </div>
                                      <div>
                                        <div
                                          className={`font-bold transition-all duration-500 ${
                                            isExpanded ? "text-2xl" : "text-xl"
                                          }`}
                                        >
                                          {card.stats.marks}
                                        </div>
                                        <div
                                          className={`transition-all duration-500 ${
                                            isExpanded ? "text-base" : "text-sm"
                                          }`}
                                        >
                                          MARKS
                                        </div>
                                      </div>
                                      <div>
                                        <div
                                          className={`font-bold transition-all duration-500 ${
                                            isExpanded ? "text-2xl" : "text-xl"
                                          }`}
                                        >
                                          {card.stats.tackles}
                                        </div>
                                        <div
                                          className={`transition-all duration-500 ${
                                            isExpanded ? "text-base" : "text-sm"
                                          }`}
                                        >
                                          TACKLES
                                        </div>
                                      </div>
                                    </div>
                                    {isExpanded && (
                                      <div className="text-center text-white/80 text-sm opacity-0 animate-[fadeIn_0.5s_ease-in-out_0.5s_forwards]">
                                        Click again to collapse • Background
                                        image more visible • Full player details
                                        shown
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </>
                            );
                          })()}
                        </div>

                        <div className="text-center text-sm text-gray-600 max-w-md">
                          <p className="font-medium">
                            Current: {playerCards[selectedCardIndex].name} from{" "}
                            {playerCards[selectedCardIndex].team}
                          </p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Player Comparison */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="w-5 h-5" />
                      Player Comparison
                    </CardTitle>
                    <CardDescription>
                      Compare {selectedPlayer.name} with another player
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-6">
                      <Select
                        value={comparisonPlayer.name}
                        onValueChange={(name) => {
                          const player = mockPlayers.find(
                            (p) => p.name === name,
                          );
                          if (player) setComparisonPlayer(player);
                        }}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select player to compare" />
                        </SelectTrigger>
                        <SelectContent>
                          {mockPlayers
                            .filter((p) => p.id !== selectedPlayer.id)
                            .map((player) => (
                              <SelectItem key={player.id} value={player.name}>
                                {player.name} ({player.team})
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {/* Progress Bar Comparison */}
                      <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-gray-700">
                          Statistical Comparison
                        </h4>
                        {[
                          "kicks",
                          "handballs",
                          "marks",
                          "tackles",
                          "goals",
                        ].map((stat) => (
                          <div key={stat} className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="capitalize">{stat}</span>
                              <span>
                                {
                                  selectedPlayer[
                                    stat as keyof typeof selectedPlayer
                                  ]
                                }{" "}
                                vs{" "}
                                {
                                  comparisonPlayer[
                                    stat as keyof typeof comparisonPlayer
                                  ]
                                }
                              </span>
                            </div>
                            <div className="flex gap-2">
                              <div className="flex-1">
                                <Progress
                                  value={
                                    ((selectedPlayer[
                                      stat as keyof typeof selectedPlayer
                                    ] as number) /
                                      Math.max(
                                        selectedPlayer[
                                          stat as keyof typeof selectedPlayer
                                        ] as number,
                                        comparisonPlayer[
                                          stat as keyof typeof comparisonPlayer
                                        ] as number,
                                      )) *
                                    100
                                  }
                                  className="h-2"
                                />
                                <div className="text-xs text-gray-600 mt-1">
                                  {selectedPlayer.name}
                                </div>
                              </div>
                              <div className="flex-1">
                                <Progress
                                  value={
                                    ((comparisonPlayer[
                                      stat as keyof typeof comparisonPlayer
                                    ] as number) /
                                      Math.max(
                                        selectedPlayer[
                                          stat as keyof typeof selectedPlayer
                                        ] as number,
                                        comparisonPlayer[
                                          stat as keyof typeof comparisonPlayer
                                        ] as number,
                                      )) *
                                    100
                                  }
                                  className="h-2"
                                />
                                <div className="text-xs text-gray-600 mt-1">
                                  {comparisonPlayer.name}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Line Chart Comparison */}
                      <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-gray-700">
                          Performance Trend
                        </h4>
                        <div className="h-64 w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={playerComparisonData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis
                                dataKey="stat"
                                tick={{ fontSize: 12 }}
                                angle={-45}
                                textAnchor="end"
                                height={80}
                              />
                              <YAxis tick={{ fontSize: 12 }} />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: "#f8f9fa",
                                  border: "1px solid #e9ecef",
                                  borderRadius: "6px",
                                }}
                              />
                              <Legend />
                              <Line
                                type="monotone"
                                dataKey={selectedPlayer.name}
                                stroke="#059669"
                                strokeWidth={3}
                                dot={{ fill: "#059669", strokeWidth: 2, r: 4 }}
                                activeDot={{
                                  r: 6,
                                  stroke: "#059669",
                                  strokeWidth: 2,
                                }}
                              />
                              <Line
                                type="monotone"
                                dataKey={comparisonPlayer.name}
                                stroke="#2563eb"
                                strokeWidth={3}
                                dot={{ fill: "#2563eb", strokeWidth: 2, r: 4 }}
                                activeDot={{
                                  r: 6,
                                  stroke: "#2563eb",
                                  strokeWidth: 2,
                                }}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                        <div className="text-xs text-gray-600 text-center">
                          Performance metrics comparison between selected
                          players
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Team Match Performance */}
          <TabsContent value="team" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Team Match Performance
                  </CardTitle>
                  <CardDescription>
                    Quick overview of recent team match metrics and navigation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-blue-50 rounded">
                      <div className="text-lg font-bold text-blue-700">Goals</div>
                      <div className="text-sm text-gray-700">Team scoring trends</div>
                    </div>
                    <div className="p-3 bg-green-50 rounded">
                      <div className="text-lg font-bold text-green-700">Disposals</div>
                      <div className="text-sm text-gray-700">Ball movement & control</div>
                    </div>
                    <div className="p-3 bg-orange-50 rounded">
                      <div className="text-lg font-bold text-orange-700">Inside 50s</div>
                      <div className="text-sm text-gray-700">Forward entries</div>
                    </div>
                    <div className="p-3 bg-purple-50 rounded">
                      <div className="text-lg font-bold text-purple-700">Tackles</div>
                      <div className="text-sm text-gray-700">Pressure acts</div>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <Button onClick={() => navigate("/team-match-performance")} className="bg-gradient-to-r from-green-600 to-blue-600">
                      Open Full Team View
                    </Button>
                    <Button variant="outline" onClick={() => navigate("/player-performance")}>
                      Go to Player Performance
                    </Button>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">How to use</CardTitle>
                  <CardDescription>
                    Explore team-level insights and jump to player details
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc pl-5 text-sm text-gray-700 space-y-2">
                    <li>Review team metrics and compare trends</li>
                    <li>Click "Open Full Team View" for detailed comparisons</li>
                    <li>Use "Go to Player Performance" for individual breakdowns</li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Crowd Monitoring Dashboard */}
          <TabsContent value="crowd" className="space-y-6">
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
                <TabsTrigger value="timeline">Timeline</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <div className="grid lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <MapPin className="w-5 h-5" />
                        Stadium Zone Density
                      </CardTitle>
                      <CardDescription>
                        Real-time crowd distribution across stadium zones
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {crowdZones.map((zone, index) => (
                          <div key={index} className="space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="font-medium">{zone.zone}</span>
                              <div className="flex items-center gap-2">
                                <span className="text-sm text-gray-600">
                                  {zone.current.toLocaleString()} /{" "}
                                  {zone.capacity.toLocaleString()}
                                </span>
                                {zone.trend === "up" && (
                                  <TrendingUp className="w-4 h-4 text-green-500" />
                                )}
                                {zone.trend === "down" && (
                                  <TrendingDown className="w-4 h-4 text-red-500" />
                                )}
                                {zone.trend === "stable" && (
                                  <div className="w-4 h-4 rounded-full bg-gray-400" />
                                )}
                              </div>
                            </div>
                            <Progress value={zone.density} className="h-3" />
                            <div className="text-xs text-gray-600 text-right">
                              {zone.density}% capacity
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Eye className="w-5 h-5" />
                        Visual Stadium Map
                      </CardTitle>
                      <CardDescription>
                        Interactive crowd density visualization
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="relative bg-green-50 rounded-lg p-4 min-h-80">
                        {/* AFL Ground - Oval Shape */}
                        <div
                          className="absolute inset-6 border-4 border-green-600 bg-green-200"
                          style={{
                            borderRadius: "50%",
                            clipPath: "ellipse(45% 40% at 50% 50%)",
                          }}
                        >
                          {/* Goal squares */}
                          <div className="absolute top-2 left-1/2 transform -translate-x-1/2 w-8 h-6 border-2 border-green-700 bg-green-300"></div>
                          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 w-8 h-6 border-2 border-green-700 bg-green-300"></div>

                          {/* Center circle */}
                          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-12 h-12 border-2 border-green-700 rounded-full"></div>

                          {/* AFL text */}
                          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-xs font-bold text-green-800 mt-6">
                            AFL GROUND
                          </div>
                        </div>

                        {/* Dynamic Zone overlays */}
                        {crowdZones.map((zone, index) => (
                          <div
                            key={index}
                            className="absolute transition-all duration-1000 cursor-pointer hover:scale-105"
                            style={{
                              ...zone.position,
                              backgroundColor: zone.color,
                              opacity: (zone.density / 100) * 0.8 + 0.2,
                              borderRadius: "8px",
                              border: "2px solid rgba(255,255,255,0.8)",
                            }}
                            title={`${zone.zone}: ${zone.current.toLocaleString()}/${zone.capacity.toLocaleString()} (${zone.density}%)`}
                          >
                            <div className="p-2 text-white text-center">
                              <div className="text-xs font-medium leading-tight">
                                {zone.zone.split(" ")[0]}
                              </div>
                              <div className="text-xs font-bold">
                                {zone.density}%
                              </div>
                              <div className="text-xs opacity-90">
                                {zone.current.toLocaleString()}
                              </div>
                            </div>
                          </div>
                        ))}

                        {/* Stadium info */}
                        <div className="absolute top-2 right-2 flex items-center gap-2">
                          <span className="text-xs font-medium text-gray-700 bg-white/80 px-2 py-1 rounded">
                            MCG
                          </span>
                        </div>
                      </div>

                      {/* Enhanced Legend */}
                      <div className="mt-4 space-y-2">
                        <div className="flex justify-between items-center text-xs">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-green-500 rounded"></div>
                            <span>Low (0-49%)</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                            <span>Medium (50-84%)</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-orange-500 rounded"></div>
                            <span>High (85-94%)</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-red-600 rounded"></div>
                            <span>Critical (95%+)</span>
                          </div>
                        </div>

                        {/* Summary stats */}
                        <div className="flex justify-between items-center text-xs bg-gray-50 p-2 rounded">
                          <span>
                            Total Attendance:{" "}
                            <strong>
                              {crowdZones
                                .reduce((sum, zone) => sum + zone.current, 0)
                                .toLocaleString()}
                            </strong>
                          </span>
                          <span>
                            Avg Density:{" "}
                            <strong>
                              {Math.round(
                                crowdZones.reduce(
                                  (sum, zone) => sum + zone.density,
                                  0,
                                ) / crowdZones.length,
                              )}
                              %
                            </strong>
                          </span>
                          <span>
                            Critical Zones:{" "}
                            <strong className="text-red-600">
                              {
                                crowdZones.filter((zone) => zone.density >= 95)
                                  .length
                              }
                            </strong>
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Calendar className="w-5 h-5" />
                      Historical Crowd Data
                    </CardTitle>
                    <CardDescription>
                      Crowd patterns from previous matches
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {crowdZones
                            .reduce((sum, zone) => sum + zone.current, 0)
                            .toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-600">
                          Current Attendance
                        </div>
                        <div className="text-xs text-green-600 mt-1">
                          Live Stadium Data
                        </div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {Math.round(
                            crowdZones.reduce(
                              (sum, zone) => sum + zone.density,
                              0,
                            ) / crowdZones.length,
                          )}
                          %
                        </div>
                        <div className="text-sm text-gray-600">
                          Average Density
                        </div>
                        <div className="text-xs text-green-600 mt-1">
                          Across {crowdZones.length} zones
                        </div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {crowdZones
                            .reduce((sum, zone) => sum + zone.capacity, 0)
                            .toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-600">
                          Total Capacity
                        </div>
                        <div className="text-xs text-gray-600 mt-1">
                          Stadium Maximum
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="analytics" className="space-y-6">
                <div className="grid lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <PieChart className="w-5 h-5" />
                        Density Distribution Pie Chart
                      </CardTitle>
                      <CardDescription>
                        Visual breakdown of zones by density levels
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={[
                                {
                                  name: "Low (0-49%)",
                                  value: crowdZones.filter(
                                    (zone) => zone.density < 50,
                                  ).length,
                                  color: "#22c55e",
                                },
                                {
                                  name: "Medium (50-84%)",
                                  value: crowdZones.filter(
                                    (zone) =>
                                      zone.density >= 50 && zone.density < 85,
                                  ).length,
                                  color: "#f59e0b",
                                },
                                {
                                  name: "High (85-94%)",
                                  value: crowdZones.filter(
                                    (zone) =>
                                      zone.density >= 85 && zone.density < 95,
                                  ).length,
                                  color: "#f97316",
                                },
                                {
                                  name: "Critical (95%+)",
                                  value: crowdZones.filter(
                                    (zone) => zone.density >= 95,
                                  ).length,
                                  color: "#dc2626",
                                },
                              ].filter((item) => item.value > 0)}
                              cx="50%"
                              cy="50%"
                              innerRadius={60}
                              outerRadius={120}
                              paddingAngle={2}
                              dataKey="value"
                              label={({ value, percent }) =>
                                value > 0
                                  ? `${value} (${(percent * 100).toFixed(0)}%)`
                                  : ""
                              }
                              labelLine={false}
                            >
                              {[
                                {
                                  name: "Low (0-49%)",
                                  value: crowdZones.filter(
                                    (zone) => zone.density < 50,
                                  ).length,
                                  color: "#22c55e",
                                },
                                {
                                  name: "Medium (50-84%)",
                                  value: crowdZones.filter(
                                    (zone) =>
                                      zone.density >= 50 && zone.density < 85,
                                  ).length,
                                  color: "#f59e0b",
                                },
                                {
                                  name: "High (85-94%)",
                                  value: crowdZones.filter(
                                    (zone) =>
                                      zone.density >= 85 && zone.density < 95,
                                  ).length,
                                  color: "#f97316",
                                },
                                {
                                  name: "Critical (95%+)",
                                  value: crowdZones.filter(
                                    (zone) => zone.density >= 95,
                                  ).length,
                                  color: "#dc2626",
                                },
                              ]
                                .filter((item) => item.value > 0)
                                .map((entry, index) => (
                                  <Cell
                                    key={`cell-${index}`}
                                    fill={entry.color}
                                  />
                                ))}
                            </Pie>
                            <Tooltip
                              content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                  const data = payload[0].payload;
                                  const densityRange = data.name;
                                  let zones = [];

                                  if (densityRange.includes("Low (0-49%)")) {
                                    zones = crowdZones.filter(
                                      (zone) => zone.density < 50,
                                    );
                                  } else if (
                                    densityRange.includes("Medium (50-84%)")
                                  ) {
                                    zones = crowdZones.filter(
                                      (zone) =>
                                        zone.density >= 50 && zone.density < 85,
                                    );
                                  } else if (
                                    densityRange.includes("High (85-94%)")
                                  ) {
                                    zones = crowdZones.filter(
                                      (zone) =>
                                        zone.density >= 85 && zone.density < 95,
                                    );
                                  } else if (
                                    densityRange.includes("Critical (95%+)")
                                  ) {
                                    zones = crowdZones.filter(
                                      (zone) => zone.density >= 95,
                                    );
                                  }

                                  return (
                                    <div className="bg-white p-3 border rounded-lg shadow-lg">
                                      <p className="font-medium">{data.name}</p>
                                      <p className="text-sm text-gray-600">
                                        {data.value} zone
                                        {data.value !== 1 ? "s" : ""}
                                      </p>
                                      {zones.length > 0 && (
                                        <div className="mt-2 text-xs">
                                          <p className="font-medium">Zones:</p>
                                          {zones.map((zone) => (
                                            <p key={zone.zone}>
                                              • {zone.zone} ({zone.density}%)
                                            </p>
                                          ))}
                                        </div>
                                      )}
                                    </div>
                                  );
                                }
                                return null;
                              }}
                            />
                            <Legend
                              verticalAlign="bottom"
                              height={36}
                              formatter={(value) => (
                                <span className="text-sm">{value}</span>
                              )}
                            />
                          </PieChart>
                        </ResponsiveContainer>
                      </div>

                      {/* Summary below chart */}
                      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span>Total Zones:</span>
                            <span className="font-medium">
                              {crowdZones.length}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Safe Zones:</span>
                            <span className="font-medium text-green-600">
                              {
                                crowdZones.filter((zone) => zone.density < 85)
                                  .length
                              }
                            </span>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span>Alert Zones:</span>
                            <span className="font-medium text-orange-600">
                              {
                                crowdZones.filter(
                                  (zone) =>
                                    zone.density >= 85 && zone.density < 95,
                                ).length
                              }
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Critical Zones:</span>
                            <span className="font-medium text-red-600">
                              {
                                crowdZones.filter((zone) => zone.density >= 95)
                                  .length
                              }
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="w-5 h-5" />
                        Zone Analysis
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {crowdZones.map((zone, index) => {
                          const densityLevel =
                            zone.density >= 95
                              ? "Critical"
                              : zone.density >= 85
                                ? "High"
                                : zone.density >= 70
                                  ? "Medium"
                                  : "Low";
                          const colorClass =
                            zone.density >= 95
                              ? "text-red-600"
                              : zone.density >= 85
                                ? "text-orange-600"
                                : zone.density >= 70
                                  ? "text-yellow-600"
                                  : "text-green-600";

                          return (
                            <div key={index} className="p-3 border rounded-lg">
                              <div className="flex justify-between items-center mb-2">
                                <span className="font-medium">{zone.zone}</span>
                                <span
                                  className={`text-sm font-medium ${colorClass}`}
                                >
                                  {densityLevel}
                                </span>
                              </div>
                              <Progress
                                value={zone.density}
                                className="h-2 mb-1"
                              />
                              <div className="text-xs text-gray-600">
                                {zone.current.toLocaleString()} /{" "}
                                {zone.capacity.toLocaleString()}({zone.density}
                                %)
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="timeline" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Calendar className="w-5 h-5" />
                      Crowd Density Timeline
                    </CardTitle>
                    <CardDescription>
                      Historical crowd data and density trends over time
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart
                          data={generateTimelineFromStadiumData(crowdZones)}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="time" tick={{ fontSize: 12 }} />
                          <YAxis
                            yAxisId="attendance"
                            orientation="left"
                            tick={{ fontSize: 12 }}
                            label={{
                              value: "Attendance",
                              angle: -90,
                              position: "insideLeft",
                            }}
                          />
                          <YAxis
                            yAxisId="density"
                            orientation="right"
                            tick={{ fontSize: 12 }}
                            label={{
                              value: "Density %",
                              angle: 90,
                              position: "insideRight",
                            }}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "white",
                              border: "1px solid #ccc",
                              borderRadius: "8px",
                              fontSize: "12px",
                            }}
                            formatter={(value, name) => {
                              if (name === "attendance")
                                return [
                                  value.toLocaleString(),
                                  "Total Attendance",
                                ];
                              if (name === "density")
                                return [`${value}%`, "Average Density"];
                              if (name === "critical")
                                return [value, "Critical Zones"];
                              if (name === "high")
                                return [value, "High Density Zones"];
                              return [value, name];
                            }}
                          />
                          <Legend />
                          <Area
                            yAxisId="attendance"
                            type="monotone"
                            dataKey="attendance"
                            stackId="1"
                            stroke="#3b82f6"
                            fill="#3b82f6"
                            fillOpacity={0.6}
                            name="Total Attendance"
                          />
                          <Area
                            yAxisId="density"
                            type="monotone"
                            dataKey="density"
                            stackId="2"
                            stroke="#10b981"
                            fill="#10b981"
                            fillOpacity={0.6}
                            name="Average Density %"
                          />
                          <Area
                            yAxisId="density"
                            type="monotone"
                            dataKey="critical"
                            stackId="3"
                            stroke="#ef4444"
                            fill="#ef4444"
                            fillOpacity={0.8}
                            name="Critical Zones"
                          />
                          <Area
                            yAxisId="density"
                            type="monotone"
                            dataKey="high"
                            stackId="4"
                            stroke="#f97316"
                            fill="#f97316"
                            fillOpacity={0.8}
                            name="High Density Zones"
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                <div className="grid lg:grid-cols-3 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Peak Hours</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {generateTimelineFromStadiumData(crowdZones)
                          .sort((a, b) => b.attendance - a.attendance)
                          .slice(0, 3)
                          .map((entry, index) => (
                            <div
                              key={index}
                              className="flex justify-between items-center p-2 bg-gray-50 rounded"
                            >
                              <span className="text-sm font-medium">
                                {entry.time}
                              </span>
                              <div className="text-right">
                                <div className="text-sm font-bold">
                                  {entry.attendance.toLocaleString()}
                                </div>
                                <div className="text-xs text-gray-600">
                                  {entry.density}% density
                                </div>
                              </div>
                            </div>
                          ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Density Trends</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="p-3 bg-blue-50 rounded">
                          <div className="text-lg font-bold text-blue-700">
                            {Math.round(
                              crowdZones.reduce(
                                (sum, zone) => sum + zone.density,
                                0,
                              ) / crowdZones.length,
                            )}
                            %
                          </div>
                          <div className="text-sm text-blue-600">
                            Current Average Density
                          </div>
                        </div>
                        <div className="p-3 bg-red-50 rounded">
                          <div className="text-lg font-bold text-red-700">
                            {
                              crowdZones.filter((zone) => zone.density >= 95)
                                .length
                            }
                          </div>
                          <div className="text-sm text-red-600">
                            Critical Zones
                          </div>
                        </div>
                        <div className="p-3 bg-orange-50 rounded">
                          <div className="text-lg font-bold text-orange-700">
                            {
                              crowdZones.filter(
                                (zone) =>
                                  zone.density >= 85 && zone.density < 95,
                              ).length
                            }
                          </div>
                          <div className="text-sm text-orange-600">
                            High Density Zones
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">
                        Capacity Insights
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="p-3 bg-green-50 rounded">
                          <div className="text-lg font-bold text-green-700">
                            {Math.round(
                              (crowdZones.reduce(
                                (sum, zone) => sum + zone.current,
                                0,
                              ) /
                                crowdZones.reduce(
                                  (sum, zone) => sum + zone.capacity,
                                  0,
                                )) *
                                100,
                            )}
                            %
                          </div>
                          <div className="text-sm text-green-600">
                            Current Stadium Fill
                          </div>
                        </div>
                        <div className="p-3 bg-purple-50 rounded">
                          <div className="text-lg font-bold text-purple-700">
                            {crowdZones
                              .reduce((sum, zone) => sum + zone.current, 0)
                              .toLocaleString()}
                          </div>
                          <div className="text-sm text-purple-600">
                            Current Attendance
                          </div>
                        </div>
                        <div className="p-3 bg-gray-50 rounded">
                          <div className="text-lg font-bold text-gray-700">
                            {(
                              crowdZones.reduce(
                                (sum, zone) => sum + zone.capacity,
                                0,
                              ) -
                              crowdZones.reduce(
                                (sum, zone) => sum + zone.current,
                                0,
                              )
                            ).toLocaleString()}
                          </div>
                          <div className="text-sm text-gray-600">
                            Available Capacity
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </TabsContent>

          {/* Analytics Report Download */}
          <TabsContent value="reports" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Player Performance Reports
                  </CardTitle>
                  <CardDescription>
                    Generate detailed analytics reports for players and teams
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium">Report Type</label>
                      <Select defaultValue="individual">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="individual">
                            Individual Player Report
                          </SelectItem>
                          <SelectItem value="team">
                            Team Performance Report
                          </SelectItem>
                          <SelectItem value="comparison">
                            Player Comparison Report
                          </SelectItem>
                          <SelectItem value="season">
                            Season Summary Report
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Date Range</label>
                      <Select defaultValue="last7">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="last7">Last 7 days</SelectItem>
                          <SelectItem value="last30">Last 30 days</SelectItem>
                          <SelectItem value="season">Current Season</SelectItem>
                          <SelectItem value="custom">Custom Range</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Format</label>
                      <Select defaultValue="pdf">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="pdf">PDF Report</SelectItem>
                          <SelectItem value="excel">
                            Excel Spreadsheet
                          </SelectItem>
                          <SelectItem value="csv">CSV Data</SelectItem>
                          <SelectItem value="json">JSON Data</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <h4 className="font-medium">Include Sections</h4>
                    <div className="space-y-2">
                      {[
                        "Performance Statistics",
                        "Match Highlights",
                        "Trend Analysis",
                        "Comparison Charts",
                        "Heat Maps",
                      ].map((section) => (
                        <label
                          key={section}
                          className="flex items-center space-x-2"
                        >
                          <input
                            type="checkbox"
                            defaultChecked
                            className="rounded"
                          />
                          <span className="text-sm">{section}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <Button className="w-full bg-gradient-to-r from-green-600 to-blue-600">
                    <Download className="w-4 h-4 mr-2" />
                    Generate Report
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Crowd Analytics Reports
                  </CardTitle>
                  <CardDescription>
                    Generate crowd movement and density reports
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium">Report Type</label>
                      <Select defaultValue="density">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="density">
                            Crowd Density Report
                          </SelectItem>
                          <SelectItem value="movement">
                            Movement Pattern Report
                          </SelectItem>
                          <SelectItem value="capacity">
                            Capacity Utilization Report
                          </SelectItem>
                          <SelectItem value="safety">
                            Safety Analytics Report
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Time Period</label>
                      <Select defaultValue="match">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="match">Current Match</SelectItem>
                          <SelectItem value="gameday">Full Game Day</SelectItem>
                          <SelectItem value="season">
                            Season Analysis
                          </SelectItem>
                          <SelectItem value="custom">Custom Period</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Zone Focus</label>
                      <Select defaultValue="all">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Zones</SelectItem>
                          <SelectItem value="northern">
                            Northern Stand
                          </SelectItem>
                          <SelectItem value="southern">
                            Southern Stand
                          </SelectItem>
                          <SelectItem value="eastern">Eastern Wing</SelectItem>
                          <SelectItem value="western">Western Wing</SelectItem>
                          <SelectItem value="premium">
                            Premium Seating
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <h4 className="font-medium">Analytics Features</h4>
                    <div className="space-y-2">
                      {[
                        "Heat Map Visualization",
                        "Peak Hour Analysis",
                        "Entry/Exit Patterns",
                        "Safety Compliance",
                        "Revenue Optimization",
                      ].map((feature) => (
                        <label
                          key={feature}
                          className="flex items-center space-x-2"
                        >
                          <input
                            type="checkbox"
                            defaultChecked
                            className="rounded"
                          />
                          <span className="text-sm">{feature}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <Button className="w-full bg-gradient-to-r from-green-600 to-blue-600">
                    <Download className="w-4 h-4 mr-2" />
                    Generate Crowd Report
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Recent Reports */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Reports</CardTitle>
                <CardDescription>
                  Download previously generated reports
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    {
                      name: "Weekly Player Performance - Round 15",
                      date: "2024-01-15",
                      size: "2.4 MB",
                      format: "PDF",
                    },
                    {
                      name: "Crowd Density Analysis - MCG",
                      date: "2024-01-14",
                      size: "1.8 MB",
                      format: "Excel",
                    },
                    {
                      name: "Season Summary Report",
                      date: "2024-01-12",
                      size: "5.2 MB",
                      format: "PDF",
                    },
                    {
                      name: "Player Comparison - Top 50",
                      date: "2024-01-10",
                      size: "3.1 MB",
                      format: "Excel",
                    },
                  ].map((report, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex-1">
                        <div className="font-medium">{report.name}</div>
                        <div className="text-sm text-gray-600">
                          {report.date} • {report.size} • {report.format}
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          const reportContent = `AFL Analytics Report: ${report.name}

Generated: ${report.date}
Format: ${report.format}
Size: ${report.size}

This is a sample report from AFL Analytics Platform.
Report details and analysis data would be included here in a real implementation.

Generated on: ${new Date().toLocaleString()}
`;
                          downloadText(
                            reportContent,
                            `${report.name.replace(/[^a-z0-9]/gi, "_")}_${Date.now()}`,
                          );
                        }}
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Video Analytics Input */}
          <TabsContent value="video" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="w-5 h-5" />
                    Video Upload & Analysis
                  </CardTitle>
                  <CardDescription>
                    Upload match videos for AI-powered analysis
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                    <input
                      type="file"
                      accept="video/*"
                      onChange={handleVideoFileSelect}
                      className="hidden"
                      id="video-upload-dashboard"
                    />
                    <label
                      htmlFor="video-upload-dashboard"
                      className="cursor-pointer"
                    >
                      <Video className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                      <div className="text-lg font-medium text-gray-700">
                        {selectedVideoFile
                          ? selectedVideoFile.name
                          : "Drop video files here"}
                      </div>
                      <div className="text-sm text-gray-500">
                        or click to browse
                      </div>
                      <div className="text-xs text-gray-400 mt-2">
                        Supports MP4, MOV, AVI • Max 500MB
                      </div>
                    </label>
                  </div>

                  {selectedVideoFile && (
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Video className="w-4 h-4 text-blue-600" />
                        <span className="font-medium">
                          {selectedVideoFile.name}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        Size:{" "}
                        {(selectedVideoFile.size / 1024 / 1024).toFixed(1)} MB
                      </div>
                    </div>
                  )}

                  {videoAnalysisError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="text-sm text-red-700">
                        {videoAnalysisError}
                      </div>
                    </div>
                  )}

                  {isVideoUploading && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Uploading video...</span>
                        <span>{videoUploadProgress}%</span>
                      </div>
                      <Progress value={videoUploadProgress} className="h-2" />
                    </div>
                  )}

                  {isVideoAnalyzing && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Analyzing video...</span>
                        <span>{videoAnalysisProgress}%</span>
                      </div>
                      <Progress value={videoAnalysisProgress} className="h-2" />
                    </div>
                  )}

                  {videoAnalysisComplete && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full" />
                        <span className="text-sm text-green-700 font-medium">
                          Analysis completed successfully!
                        </span>
                      </div>
                    </div>
                  )}

                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium">
                        Analysis Type
                      </label>
                      <Select
                        value={selectedAnalysisType}
                        onValueChange={setSelectedAnalysisType}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="highlights">
                            Match Highlights
                          </SelectItem>
                          <SelectItem value="player">
                            Player Tracking
                          </SelectItem>
                          <SelectItem value="tactics">
                            Tactical Analysis
                          </SelectItem>
                          <SelectItem value="performance">
                            Performance Metrics
                          </SelectItem>
                          <SelectItem value="crowd">Crowd Reactions</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Focus Areas</label>
                      <div className="grid grid-cols-2 gap-2 mt-2">
                        {[
                          "Goals & Scoring",
                          "Defensive Actions",
                          "Player Movement",
                          "Ball Possession",
                          "Set Pieces",
                          "Injuries",
                        ].map((area) => (
                          <label
                            key={area}
                            className="flex items-center space-x-2"
                          >
                            <input
                              type="checkbox"
                              className="rounded"
                              checked={selectedFocusAreas.includes(area)}
                              onChange={(e) =>
                                handleFocusAreaChange(area, e.target.checked)
                              }
                            />
                            <span className="text-sm">{area}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>

                  <Button
                    className="w-full bg-gradient-to-r from-green-600 to-blue-600"
                    onClick={uploadAndAnalyzeVideo}
                    disabled={
                      !selectedVideoFile || isVideoUploading || isVideoAnalyzing
                    }
                  >
                    <Zap className="w-4 h-4 mr-2" />
                    {isVideoUploading
                      ? "Uploading..."
                      : isVideoAnalyzing
                        ? "Analyzing..."
                        : "Start Analysis"}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="w-5 h-5" />
                    Analysis Results
                  </CardTitle>
                  <CardDescription>
                    AI-generated insights from uploaded videos
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {!videoAnalysisComplete ? (
                    <div className="text-center py-8">
                      <Video className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        No Analysis Results Yet
                      </h3>
                      <p className="text-gray-600">
                        Upload and analyze a video to see detailed insights here
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">
                            Analysis Type:{" "}
                            {selectedAnalysisType === "highlights"
                              ? "Match Highlights"
                              : selectedAnalysisType === "player"
                                ? "Player Tracking"
                                : selectedAnalysisType === "tactics"
                                  ? "Tactical Analysis"
                                  : selectedAnalysisType === "performance"
                                    ? "Performance Metrics"
                                    : "Crowd Reactions"}
                          </span>
                          <Badge variant="secondary">Complete</Badge>
                        </div>
                        <div className="text-sm text-gray-600">
                          Video: {selectedVideoFile?.name}
                        </div>
                      </div>

                      {selectedFocusAreas.length > 0 && (
                        <div className="p-4 bg-green-50 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">
                              Focus Areas Analyzed
                            </span>
                            <Badge variant="secondary">
                              {selectedFocusAreas.length} areas
                            </Badge>
                          </div>
                          <div className="text-sm text-gray-600">
                            {selectedFocusAreas.join(", ")}
                          </div>
                        </div>
                      )}

                      <div className="p-4 bg-purple-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">
                            AI Insights Generated
                          </span>
                          <Badge variant="secondary">Ready</Badge>
                        </div>
                        <div className="text-sm text-gray-600">
                          {selectedAnalysisType === "highlights" &&
                            "Key moments and highlights identified"}
                          {selectedAnalysisType === "player" &&
                            "Player movements and performance tracked"}
                          {selectedAnalysisType === "tactics" &&
                            "Tactical patterns and strategies analyzed"}
                          {selectedAnalysisType === "performance" &&
                            "Performance metrics calculated"}
                          {selectedAnalysisType === "crowd" &&
                            "Crowd reactions and engagement measured"}
                        </div>
                      </div>
                    </div>
                  )}

                  <Separator />

                  <div className="space-y-3">
                    <h4 className="font-medium">Export Analysis</h4>
                    <p className="text-sm text-gray-600">
                      Download analysis data from backend in different formats
                    </p>
                    <div className="space-y-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleDownloadVideoClips}
                        disabled={!videoAnalysisComplete}
                        className="w-full"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Video Clips
                      </Button>
                      <div className="grid grid-cols-3 gap-1">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadReport("pdf")}
                          disabled={!videoAnalysisComplete}
                        >
                          <FileText className="w-4 h-4 mr-1" />
                          PDF
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadReport("json")}
                          disabled={!videoAnalysisComplete}
                        >
                          <Download className="w-4 h-4 mr-1" />
                          JSON
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownloadReport("txt")}
                          disabled={!videoAnalysisComplete}
                        >
                          <FileText className="w-4 h-4 mr-1" />
                          TXT
                        </Button>
                      </div>
                      <div className="text-xs text-gray-500 mt-2 space-y-1">
                        <div>
                          <strong>PDF:</strong> Formatted report for
                          printing/sharing
                        </div>
                        <div>
                          <strong>JSON:</strong> Raw backend data for developers
                        </div>
                        <div>
                          <strong>TXT:</strong> Plain text summary for analysis
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Processing Queue */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Processing Queue
                  <Badge variant="outline" className="ml-auto">
                    {processingQueue.length} items
                  </Badge>
                </CardTitle>
                <CardDescription>
                  Track the status of your video analysis requests
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {processingQueue.map((item) => (
                    <div
                      key={item.id}
                      className="p-4 border rounded-lg bg-gradient-to-r from-white via-gray-50 to-white"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <StatusIcon status={item.status} />
                          <div className="flex-1">
                            <div className="font-medium text-gray-900">
                              {item.name}
                            </div>
                            <div className="text-sm text-gray-600 flex items-center gap-2">
                              <span>{item.analysisType}</span>
                              <span>•</span>
                              <span>{item.duration}</span>
                              <span>•</span>
                              <span>{item.size}</span>
                              {item.priority === "high" && (
                                <>
                                  <span>•</span>
                                  <Badge
                                    variant="destructive"
                                    className="text-xs py-0 px-1"
                                  >
                                    HIGH PRIORITY
                                  </Badge>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={
                              item.status === "completed"
                                ? "default"
                                : item.status === "analyzing" ||
                                    item.status === "processing"
                                  ? "secondary"
                                  : item.status === "uploading"
                                    ? "outline"
                                    : item.status === "failed"
                                      ? "destructive"
                                      : "outline"
                            }
                            className="capitalize"
                          >
                            {item.status}
                          </Badge>
                          {item.retryCount > 0 && (
                            <Badge variant="outline" className="text-xs">
                              Retry #{item.retryCount}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {item.progress > 0 && item.progress < 100 && (
                        <div className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">
                              {item.status === "uploading"
                                ? "Uploading file..."
                                : item.status === "processing"
                                  ? "Pre-processing video..."
                                  : item.status === "analyzing"
                                    ? "Analyzing video content..."
                                    : "Processing..."}
                            </span>
                            <span className="font-medium">
                              {Math.round(item.progress)}%
                            </span>
                          </div>
                          <Progress value={item.progress} className="h-2" />
                          <div className="text-xs text-gray-500">
                            Stage:{" "}
                            {item.processingStage
                              .replace(/_/g, " ")
                              .replace(/\b\w/g, (l) => l.toUpperCase())}
                          </div>
                        </div>
                      )}

                      {item.status === "failed" && (
                        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                          <div className="flex items-center gap-2 text-red-800 text-sm">
                            <div className="w-4 h-4 rounded-full bg-red-500 flex-shrink-0" />
                            <span>
                              Processing failed after {item.errorCount} attempt
                              {item.errorCount > 1 ? "s" : ""}
                            </span>
                          </div>
                          <div className="text-xs text-red-600 mt-1">
                            Common causes: Unsupported format, corrupted file,
                            or insufficient server resources
                          </div>
                        </div>
                      )}

                      <div className="flex justify-between items-center mt-3">
                        <div className="flex flex-col text-sm text-gray-500">
                          <span>
                            Uploaded: {formatTimeAgo(item.uploadTime)}
                          </span>
                          {item.status === "completed" &&
                            item.completedTime && (
                              <span>
                                Completed: {formatTimeAgo(item.completedTime)}
                              </span>
                            )}
                          {item.estimatedCompletion &&
                            item.status !== "completed" && (
                              <span>
                                ETA: {formatETA(item.estimatedCompletion)}
                              </span>
                            )}
                        </div>
                        <div className="flex gap-2">
                          {item.status === "completed" && (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleViewAnalysis(item)}
                                className="text-blue-600 border-blue-600 hover:bg-blue-50"
                              >
                                <Eye className="w-4 h-4 mr-1" />
                                View
                              </Button>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    className="text-green-600 border-green-600 hover:bg-green-50"
                                  >
                                    <Download className="w-4 h-4 mr-1" />
                                    Download
                                    <ChevronDown className="w-3 h-3 ml-1" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem
                                    onClick={() =>
                                      handleDownloadFromQueue(item, "pdf")
                                    }
                                  >
                                    <FileText className="w-4 h-4 mr-2" />
                                    PDF Report
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    onClick={() =>
                                      handleDownloadFromQueue(item, "json")
                                    }
                                  >
                                    <Download className="w-4 h-4 mr-2" />
                                    JSON Data
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    onClick={() =>
                                      handleDownloadFromQueue(item, "txt")
                                    }
                                  >
                                    <FileText className="w-4 h-4 mr-2" />
                                    Text Summary
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </>
                          )}
                          {item.status === "failed" && (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => retryProcessing(item.id)}
                                className="text-blue-600 border-blue-600 hover:bg-blue-50"
                              >
                                <Zap className="w-4 h-4 mr-1" />
                                Retry
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => removeFromQueue(item.id)}
                                className="text-red-600 border-red-600 hover:bg-red-50"
                              >
                                Remove
                              </Button>
                            </>
                          )}
                          {(item.status === "queued" ||
                            item.status === "uploading") && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => removeFromQueue(item.id)}
                              className="text-gray-600"
                            >
                              Cancel
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}

                  {processingQueue.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Clock className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                      <p>No items in processing queue</p>
                      <p className="text-sm">
                        Upload a video to start analysis
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Analysis View Modal */}
      <Dialog open={viewModalOpen} onOpenChange={setViewModalOpen}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Analysis Results: {selectedAnalysisItem?.name}
            </DialogTitle>
            <DialogDescription>
              Complete analysis details for {selectedAnalysisItem?.analysisType}
            </DialogDescription>
          </DialogHeader>

          {selectedAnalysisItem && (
            <div className="space-y-6">
              {/* Analysis Overview */}
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Video Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="text-sm">
                      <span className="text-gray-600">Duration:</span>{" "}
                      {selectedAnalysisItem.duration}
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">File Size:</span>{" "}
                      {selectedAnalysisItem.size}
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">Analysis Type:</span>{" "}
                      {selectedAnalysisItem.analysisType}
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">Completed:</span>{" "}
                      {selectedAnalysisItem.completedTime
                        ? formatTimeAgo(selectedAnalysisItem.completedTime)
                        : "N/A"}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">
                      Processing Details
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="text-sm">
                      <span className="text-gray-600">Priority:</span>
                      <Badge
                        variant={
                          selectedAnalysisItem.priority === "high"
                            ? "destructive"
                            : selectedAnalysisItem.priority === "medium"
                              ? "secondary"
                              : "outline"
                        }
                        className="ml-2 text-xs"
                      >
                        {selectedAnalysisItem.priority}
                      </Badge>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">Status:</span>
                      <Badge variant="default" className="ml-2 text-xs">
                        {selectedAnalysisItem.status}
                      </Badge>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">Stage:</span>{" "}
                      {selectedAnalysisItem.processingStage
                        .replace(/_/g, " ")
                        .replace(/\b\w/g, (l: string) => l.toUpperCase())}
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">Progress:</span>{" "}
                      {selectedAnalysisItem.progress}%
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Enhanced Analysis Results with Charts */}
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Analysis Results</h3>
                  <Badge
                    variant="outline"
                    className="bg-green-50 text-green-700 border-green-200"
                  >
                    <div className="w-2 h-2 rounded-full bg-green-500 mr-2" />
                    Analysis Complete
                  </Badge>
                </div>

                {(() => {
                  // Simple mock data to avoid chart rendering issues
                  return (
                    <>
                      {/* Player Performance Analysis - Fixed */}
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base flex items-center gap-2">
                            <BarChart3 className="w-4 h-4" />
                            Player Performance Analysis
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            {/* Player Stats Grid */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              <div className="p-3 bg-blue-50 rounded-lg">
                                <div className="font-medium">
                                  Marcus Bontempelli
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                  Goals: 2 | Tackles: 6 | Efficiency: 85.7%
                                </div>
                                <div className="text-sm text-gray-600">
                                  Max Speed: 32.4 km/h | Distance: 12.8 km
                                </div>
                              </div>
                              <div className="p-3 bg-green-50 rounded-lg">
                                <div className="font-medium">
                                  Patrick Cripps
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                  Goals: 1 | Tackles: 9 | Efficiency: 88.6%
                                </div>
                                <div className="text-sm text-gray-600">
                                  Max Speed: 29.8 km/h | Distance: 13.2 km
                                </div>
                              </div>
                              <div className="p-3 bg-purple-50 rounded-lg">
                                <div className="font-medium">
                                  Clayton Oliver
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                  Goals: 0 | Tackles: 7 | Efficiency: 82.3%
                                </div>
                                <div className="text-sm text-gray-600">
                                  Max Speed: 28.1 km/h | Distance: 11.5 km
                                </div>
                              </div>
                              <div className="p-3 bg-orange-50 rounded-lg">
                                <div className="font-medium">
                                  Christian Petracca
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                  Goals: 3 | Tackles: 4 | Efficiency: 89.2%
                                </div>
                                <div className="text-sm text-gray-600">
                                  Max Speed: 31.8 km/h | Distance: 10.9 km
                                </div>
                              </div>
                            </div>

                            {/* Chart Placeholder */}
                            <div className="h-64 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center">
                              <div className="text-center">
                                <BarChart3 className="w-12 h-12 mx-auto text-gray-400 mb-2" />
                                <div className="text-lg font-medium text-gray-600">
                                  Performance Charts
                                </div>
                                <div className="text-sm text-gray-500">
                                  Interactive visualizations will be displayed
                                  here
                                </div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      {/* Crowd Analysis - Simplified */}
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            Crowd Analysis
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                              <div className="p-3 bg-green-50 rounded-lg">
                                <div className="font-medium">
                                  Northern Stand
                                </div>
                                <div className="text-sm text-gray-600">
                                  14,250 / 15,000 (95.0%)
                                </div>
                                <div className="text-sm text-gray-600">
                                  Noise: 95.2 dB peak
                                </div>
                              </div>
                              <div className="p-3 bg-blue-50 rounded-lg">
                                <div className="font-medium">
                                  Southern Stand
                                </div>
                                <div className="text-sm text-gray-600">
                                  11,680 / 12,000 (97.3%)
                                </div>
                                <div className="text-sm text-gray-600">
                                  Noise: 92.8 dB peak
                                </div>
                              </div>
                              <div className="p-3 bg-purple-50 rounded-lg">
                                <div className="font-medium">Eastern Wing</div>
                                <div className="text-sm text-gray-600">
                                  7,080 / 8,000 (88.5%)
                                </div>
                                <div className="text-sm text-gray-600">
                                  Noise: 87.4 dB peak
                                </div>
                              </div>
                            </div>

                            {/* Crowd Chart Placeholder */}
                            <div className="h-48 bg-gradient-to-br from-blue-50 to-green-50 rounded-lg border-2 border-dashed border-blue-300 flex items-center justify-center">
                              <div className="text-center">
                                <Users className="w-10 h-10 mx-auto text-blue-400 mb-2" />
                                <div className="text-lg font-medium text-blue-600">
                                  Crowd Density Charts
                                </div>
                                <div className="text-sm text-blue-500">
                                  Stadium utilization and movement patterns
                                </div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      {/* Key Highlights */}
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base flex items-center gap-2">
                            <Target className="w-4 h-4" />
                            Key Highlights
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-3">
                            <div className="p-3 bg-yellow-50 border-l-4 border-yellow-400">
                              <div className="font-medium">
                                00:03:45 - Opening Goal
                              </div>
                              <div className="text-sm text-gray-600">
                                Marcus Bontempelli scores with crowd eruption
                                (94% confidence)
                              </div>
                            </div>
                            <div className="p-3 bg-green-50 border-l-4 border-green-400">
                              <div className="font-medium">
                                00:18:23 - Spectacular Mark
                              </div>
                              <div className="text-sm text-gray-600">
                                Defensive mark leads to standing ovation (91%
                                confidence)
                              </div>
                            </div>
                            <div className="p-3 bg-blue-50 border-l-4 border-blue-400">
                              <div className="font-medium">
                                00:34:56 - Crucial Tackle
                              </div>
                              <div className="text-sm text-gray-600">
                                Game-changing defensive play (88% confidence)
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>

                      {/* Analysis Summary */}
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base flex items-center gap-2">
                            <Target className="w-4 h-4" />
                            Analysis Summary
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="grid md:grid-cols-3 gap-4">
                            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                              <div className="flex items-center gap-2 mb-2">
                                <TrendingUp className="w-4 h-4 text-blue-600" />
                                <span className="font-medium text-blue-800">
                                  Top Performer
                                </span>
                              </div>
                              <div className="text-sm text-blue-700">
                                Patrick Cripps leads with 88.6% efficiency and
                                strong defensive stats
                              </div>
                            </div>
                            <div className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg border border-green-200">
                              <div className="flex items-center gap-2 mb-2">
                                <Users className="w-4 h-4 text-green-600" />
                                <span className="font-medium text-green-800">
                                  Crowd Impact
                                </span>
                              </div>
                              <div className="text-sm text-green-700">
                                Southern Stand achieved 97.3% density with peak
                                engagement
                              </div>
                            </div>
                            <div className="p-4 bg-gradient-to-br from-purple-50 to-violet-50 rounded-lg border border-purple-200">
                              <div className="flex items-center gap-2 mb-2">
                                <BarChart3 className="w-4 h-4 text-purple-600" />
                                <span className="font-medium text-purple-800">
                                  Match Flow
                                </span>
                              </div>
                              <div className="text-sm text-purple-700">
                                Q4 showed highest intensity with 5 goals and 89%
                                efficiency
                              </div>
                            </div>
                          </div>
                          <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
                            <div className="flex items-start gap-3">
                              <div className="w-6 h-6 rounded-full bg-green-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                                <div className="w-2 h-2 rounded-full bg-white" />
                              </div>
                              <div>
                                <div className="font-medium text-gray-800">
                                  Analysis Quality Score: 9.2/10
                                </div>
                                <div className="text-sm text-gray-600 mt-1">
                                  High-confidence analysis with 94.8% accuracy
                                  across all tracking metrics
                                </div>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </>
                  );
                })()}
              </div>

              {/* Download Options */}
              <div className="flex justify-between items-center pt-4 border-t">
                <div className="text-sm text-gray-600">
                  Download this analysis in different formats
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      handleDownloadFromQueue(selectedAnalysisItem, "pdf")
                    }
                  >
                    <FileText className="w-4 h-4 mr-1" />
                    PDF
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      handleDownloadFromQueue(selectedAnalysisItem, "json")
                    }
                  >
                    <Download className="w-4 h-4 mr-1" />
                    JSON
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      handleDownloadFromQueue(selectedAnalysisItem, "txt")
                    }
                  >
                    <FileText className="w-4 h-4 mr-1" />
                    TXT
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setViewModalOpen(false)}
                    className="ml-4"
                  >
                    Close
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
