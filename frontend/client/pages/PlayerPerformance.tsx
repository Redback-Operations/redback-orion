import { useState, useEffect, useRef } from "react";
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
import { BACKEND_URL } from "@/lib/config";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import MobileNavigation from "@/components/MobileNavigation";
import LiveClock from "@/components/LiveClock";
import PlayerComparison from "@/components/PlayerComparison";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Area,
  AreaChart,
} from "recharts";
import {
  Search,
  TrendingUp,
  TrendingDown,
  Target,
  Activity,
  Users,
  BarChart3,
  PieChart as PieChartIcon,
  Play,
  Pause,
  RefreshCw,
  Download,
  Heart,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { canManagePlayers, getAccessToken } from "@/lib/auth";
import MockPlayersBanner from "@/components/MockPlayersBanner";
import {
  averageStats,
  formatStat,
  getPlayers,
  playersToCsv,
  sumStats,
  type Player,
} from "@/lib/players";
import { downloadCSV } from "@/lib/download";

// How often Play Live re-fetches players from the backend.
const LIVE_REFRESH_MS = 10_000;

// Shown in place of a chart when the selected player has no data for it.
const NoChartData = ({
  message,
  className = "",
}: {
  message: string;
  className?: string;
}) => (
  <div
    className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-200 bg-gray-50 p-8 text-center ${className}`}
  >
    <BarChart3 className="mb-2 h-8 w-8 text-gray-300" />
    <p className="text-sm font-medium text-gray-600">No data yet</p>
    <p className="mt-1 text-xs text-gray-500">{message}</p>
  </div>
);


const getTeamColor = (team: string) => {
  const teamColors: Record<string, string> = {
    "Western Bulldogs": "#1E40AF",
    Brisbane: "#8B0000",
    Richmond: "#FFD700",
    Geelong: "#1E3A8A",
    Melbourne: "#DC2626",
    Carlton: "#3B82F6",
    Adelaide: "#EF4444",
    "West Coast": "#1D4ED8",
    Collingwood: "#000000",
    Essendon: "#B91C1C",
    Fremantle: "#9333EA",
  };
  return teamColors[team] || "#6B7280";
};

const getTeamLogo = (team: string) => {
  const teamLogos: Record<string, string> = {
    "Western Bulldogs": "/team-logos/western-bulldogs.svg",
    Richmond: "/team-logos/richmond.svg",
    Geelong: "/team-logos/geelong.svg",
    Melbourne: "/team-logos/melbourne.svg",
    Carlton: "/team-logos/carlton.svg",
    Adelaide: "/team-logos/adelaide.svg",
    "West Coast": "/team-logos/west-coast.svg",
    Collingwood: "/team-logos/collingwood.svg",
    Essendon: "/team-logos/essendon.svg",
    Fremantle: "/team-logos/fremantle.svg",
    Brisbane: "/team-logos/brisbane.svg",
    Sydney: "/team-logos/sydney.svg",
    "St Kilda": "/team-logos/st-kilda.svg",
    "Port Adelaide": "/team-logos/port-adelaide.svg",
    "North Melbourne": "/team-logos/north-melbourne.svg",
    "Gold Coast": "/team-logos/gold-coast.svg",
    "GWS Giants": "/team-logos/gws-giants.svg",
    Hawthorn: "/team-logos/hawthorn.svg",
  };

  return teamLogos[team] || "/team-logos/default.svg";
};

const colorClasses: Record<string, { text: string; bg: string }> = {
  blue:   { text: "text-blue-600",   bg: "bg-blue-100" },
  green:  { text: "text-green-600",  bg: "bg-green-100" },
  purple: { text: "text-purple-600", bg: "bg-purple-100" },
  orange: { text: "text-orange-600", bg: "bg-orange-100" },
  red:    { text: "text-red-600",    bg: "bg-red-100" },
  yellow: { text: "text-yellow-600", bg: "bg-yellow-100" },
  pink:   { text: "text-pink-600",   bg: "bg-pink-100" },
  gray:   { text: "text-gray-600",   bg: "bg-gray-100" },
};

const StatCard = ({
  title,
  value,
  subtitle,
  trend,
  color = "blue",
  icon: Icon,
  active = false,
  onClick,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: "up" | "down" | "stable";
  color?: string;
  icon?: any;
  active?: boolean;
  onClick?: () => void;
}) => {
  // Pick the full class names for this colour. Unknown colours fall back to blue.
  const c = colorClasses[color] ?? colorClasses.blue;

  return (
    <Card
      className={`relative overflow-hidden transition-all duration-200 ${
        onClick ? "cursor-pointer" : ""
      } ${active ? "ring-2 ring-blue-500 ring-offset-2 shadow-lg" : ""}`}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            {Icon && <Icon className={`w-4 h-4 ${c.text}`} />}
            <span className="text-sm font-medium text-gray-600">{title}</span>
          </div>
          {trend && (
            <div className="flex items-center">
              {trend === "up" && (
                <TrendingUp className="w-3 h-3 text-green-500" />
              )}
              {trend === "down" && (
                <TrendingDown className="w-3 h-3 text-red-500" />
              )}
              {trend === "stable" && (
                <div className="w-3 h-3 rounded-full bg-gray-400" />
              )}
            </div>
          )}
        </div>
        <div className={`text-2xl font-bold mb-1 ${c.text}`}>{value}</div>
        {subtitle && <div className="text-xs text-gray-500">{subtitle}</div>}
        <div
          className={`absolute bottom-0 right-0 w-16 h-16 rounded-full -mr-8 -mb-8 opacity-50 ${c.bg}`}
        />
      </CardContent>
    </Card>
  );
};

type EnhancedPlayerCardProps = {
  player: Player;
  isSelected: boolean;
  isFavorite: boolean;
  isDeleting: boolean;
  onClick: () => void;
  onToggleFavorite: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onDelete: () => void;
};

const EnhancedPlayerCard = ({
  player,
  isSelected,
  isFavorite,
  isDeleting,
  onClick,
  onToggleFavorite,
  onDelete,
}: EnhancedPlayerCardProps) => (
  <Card
    className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${isSelected ? "ring-2 ring-blue-500 ring-offset-2" : ""
      }`}
    onClick={onClick}
  >
    <div
      className="h-24 rounded-t-lg relative"
      style={{ backgroundColor: getTeamColor(player.team) }}
    >
      <div className="absolute top-4 left-4 flex items-start gap-3 text-white">
        <div className="w-10 h-10 rounded-full bg-white shadow-sm flex items-center justify-center overflow-hidden">
          <img
            src={getTeamLogo(player.team)}
            alt={`${player.team} logo`}
            className="w-10 h-10 object-cover scale-110"
            onError={(e) => {
              e.currentTarget.src = "/team-logos/default.svg";
            }}
          />
        </div>

        <div>
          <div className="text-2xl font-bold">#{player.number}</div>
          <div className="text-sm">{player.team}</div>
        </div>
      </div>

      <div className="absolute top-4 right-4 text-white text-right">
        <div className="text-xl font-bold">{formatStat(player.stats.disposals)}</div>
        <div className="text-xs">DISPOSALS</div>
      </div>
    </div>

    <CardContent className="p-4">
      <div className="flex items-center gap-3 mb-3">
        {player.photo ? (
          <img
            src={player.photo}
            alt={player.name}
            className="w-12 h-12 rounded-full object-cover border-2 border-white shadow-lg"
          />
        ) : (
          <div className="w-12 h-12 rounded-full bg-gray-300 border-2 border-white shadow-lg flex items-center justify-center">
            <span className="text-sm font-bold text-gray-600">
              {player.name
                .split(" ")
                .map((n: string) => n[0])
                .join("")}
            </span>
          </div>
        )}

        <div className="flex-1">
          <h3 className="font-bold text-sm leading-tight">{player.name}</h3>
          <p className="text-xs text-gray-600">{player.position}</p>
        </div>

        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="shrink-0"
          aria-label={
            isFavorite
              ? `Remove ${player.name} from favourites`
              : `Add ${player.name} to favourites`
          }
          onClick={onToggleFavorite}
        >
          <Heart
            className={`h-5 w-5 ${
              isFavorite
                ? "fill-red-500 text-red-500"
                : "text-gray-500"
            }`}
          />
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="bg-blue-50 p-2 rounded">
          <div className="font-bold text-blue-600">{formatStat(player.stats.goals)}</div>
          <div className="text-gray-600">Goals</div>
        </div>
        <div className="bg-green-50 p-2 rounded">
          <div className="font-bold text-green-600">{formatStat(player.stats.marks)}</div>
          <div className="text-gray-600">Marks</div>
        </div>
        <div className="bg-purple-50 p-2 rounded">
          <div className="font-bold text-purple-600">
            {formatStat(player.stats.efficiency, "%")}
          </div>
          <div className="text-gray-600">Eff.</div>
        </div>
      </div>

      {canManagePlayers() && (
      <Button
        variant="ghost"
        size="sm"
        className="mt-3 w-full text-red-600 hover:bg-red-50"
        disabled={isDeleting}
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        {isDeleting ? "Deleting..." : "Delete"}
      </Button>
      )}
    </CardContent>
  </Card>
);


export default function PlayerPerformance() {
  const [selectedStat, setSelectedStat] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  // The LiveClock counts down from a made-up "Q2 15:23" and isn't connected
  // to a real match. Keep it hidden until the backend provides match time.
  const ENABLE_LIVE_FEATURES = false;

  const [players, setPlayers] = useState<Player[]>([]);
  const [playersLoading, setPlayersLoading] = useState(true);
  const [playersError, setPlayersError] = useState("");
  const [deletingPlayerId, setDeletingPlayerId] = useState<number | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [comparisonPlayer, setComparisonPlayer] = useState<Player | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");
  const [selectedPosition, setSelectedPosition] = useState("all");
  const [chartType, setChartType] = useState<
    "possession" | "performance" | "comparison"
  >("possession");
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [jobs, setJobs] = useState<any[]>([]);
  const token = getAccessToken();
  const [jobStatus, setJobStatus] = useState("");
  const [jobId, setJobId] = useState("");
  const [jobError, setJobError] = useState("");
  const navigate = useNavigate();

  const getFavouriteStorageKey = () => {
    let email = localStorage.getItem("userEmail");

    if (!email) {
      try {
        const storedUser = JSON.parse(localStorage.getItem("user") || "null");
        email = storedUser?.email || null;
      } catch {
        email = null;
      }
    }

    if (!email) return null;

    return `favoritePlayers:${email.trim().toLowerCase()}`;
  };

  const [favoritePlayers, setFavoritePlayers] = useState<Player[]>([]);

  // --- Bulk Excel upload state ---
  const [excelUploadStatus, setExcelUploadStatus] = useState("");
  const [excelUploadErrors, setExcelUploadErrors] = useState<any[]>([]);
  const excelInputRef = useRef<HTMLInputElement>(null);

  const uploadVideo = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${BACKEND_URL}/upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });


    const data = await res.json();
    return data.job_id;
  };

  const fetchJobs = async () => {
    const res = await fetch(`${BACKEND_URL}/jobs?page=1&limit=10`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await res.json();
    return data.jobs;
  };

  const handleUpload = async () => {
    if (!selectedVideo) {
      setUploadStatus("Please choose a video first");
      return;
    }

    setUploadStatus("Uploading...");
    setJobStatus("processing");

    try {
      const id = await uploadVideo(selectedVideo);
      setJobId(id);
      setUploadStatus(`Upload complete. Job ID: ${id}`);
      setJobStatus("done");

      const latestJobs = await fetchJobs();
      setJobs(latestJobs || []);
    } catch (err) {
      console.error(err);
      setJobStatus("failed");
      setJobError("Upload failed. Please try again.");
    }
  };

  const isFavoritePlayer = (playerId: number) => {
    return favoritePlayers.some((favorite) => favorite.id === playerId);
  };

  const toggleFavoritePlayer = (
    event: React.MouseEvent<HTMLButtonElement>,
    player: Player,
  ) => {
    event.stopPropagation();

    const favouriteKey = getFavouriteStorageKey();

    if (!favouriteKey) {
      console.error("Cannot save favourites: no logged-in user email found.");
      return;
    }

    const alreadyFavorite = isFavoritePlayer(player.id);
    const updatedFavorites = alreadyFavorite
      ? favoritePlayers.filter((favorite) => favorite.id !== player.id)
      : [...favoritePlayers, player];

    setFavoritePlayers(updatedFavorites);
    localStorage.setItem(favouriteKey, JSON.stringify(updatedFavorites));
  };

  const handleDeletePlayer = async (playerId: number) => {
    const player = players.find((existingPlayer) => existingPlayer.id === playerId);
    if (!player) return;

    const confirmed = window.confirm(
      `Delete ${player.name}? This will permanently remove the player from the database.`,
    );

    if (!confirmed) return;

    setDeletingPlayerId(player.id);
    setPlayersError("");

    try {
      const response = await fetch(`${BACKEND_URL}/api/player/${player.id}`, {
        method: "DELETE",
        headers: {
          Accept: "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `Failed to delete player (${response.status})`,
        );
      }

      const remainingPlayers = players.filter(
        (existingPlayer) => existingPlayer.id !== player.id,
      );

      setPlayers(remainingPlayers);

      if (selectedPlayer?.id === player.id) {
        setSelectedPlayer(remainingPlayers[0] ?? null);
      }

      if (comparisonPlayer?.id === player.id) {
        setComparisonPlayer(remainingPlayers[0] ?? null);
      }

      const updatedFavorites = favoritePlayers.filter(
        (favorite) => favorite.id !== player.id,
      );

      setFavoritePlayers(updatedFavorites);

      const favouriteKey = getFavouriteStorageKey();
      if (favouriteKey) {
        localStorage.setItem(favouriteKey, JSON.stringify(updatedFavorites));
      }
    } catch (error) {
      console.error("PLAYER DELETE ERROR:", error);
      setPlayersError(
        error instanceof Error ? error.message : "Unable to delete player.",
      );
    } finally {
      setDeletingPlayerId(null);
    }
  };

  // --- Bulk Excel upload handler ---
  const handleExcelUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setExcelUploadStatus("Uploading...");
    setExcelUploadErrors([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${BACKEND_URL}/api/players/upload-excel`, {
        method: "POST",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        const detail = data.detail;
        if (detail && detail.errors) {
          setExcelUploadStatus(
            detail.message || "Some rows had errors — no players were imported",
          );
          setExcelUploadErrors(detail.errors);
        } else {
          setExcelUploadStatus(
            (typeof detail === "string" ? detail : detail?.message) ||
              "Upload failed",
          );
        }
        return;
      }

      setExcelUploadStatus(`${data.players_imported} player(s) imported successfully`);
      fetchPlayers();
    } catch (err) {
      console.error("Excel upload failed:", err);
      setExcelUploadStatus("Upload failed — please try again");
    } finally {
      if (excelInputRef.current) excelInputRef.current.value = "";
    }
  };

  // silent: a background refresh from Play Live. It doesn't show the loading
  // screen, and if it fails it keeps the last good data on screen.
  const fetchPlayers = async ({ silent = false } = {}) => {
    if (!silent) {
      setPlayersLoading(true);
      setPlayersError("");
    }

    try {
      setPlayers(await getPlayers());
      setPlayersError("");
      setLastUpdated(new Date());
    } catch (error) {
      console.error("PLAYER DATABASE ERROR:", error);
      if (!silent) {
        setPlayers([]);
        setPlayersError(
          error instanceof Error
            ? error.message
            : "Unable to load players from database.",
        );
      }
    } finally {
      if (!silent) setPlayersLoading(false);
    }
  };

  useEffect(() => {
    fetchPlayers();
  }, []);

  // Play Live: re-fetch players in the background while it's on.
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      // Skip refreshes while the browser tab is hidden.
      if (document.visibilityState === "visible") {
        fetchPlayers({ silent: true });
      }
    }, LIVE_REFRESH_MS);

    // Runs when Play Live is turned off or the page is left, so timers never pile up.
    return () => clearInterval(interval);
  }, [isPlaying]);

  useEffect(() => {
    try {
      const favouriteKey = getFavouriteStorageKey();

      if (!favouriteKey) {
        setFavoritePlayers([]);
        return;
      }

      const storedFavorites = JSON.parse(
        localStorage.getItem(favouriteKey) || "[]",
      );

      setFavoritePlayers(Array.isArray(storedFavorites) ? storedFavorites : []);
    } catch (error) {
      console.error("Failed to load favorite players:", error);
      setFavoritePlayers([]);
    }
  }, []);

  useEffect(() => {
    if (players.length > 0) {
      setSelectedPlayer((current) =>
        players.find((player) => player.id === current?.id) || players[0],
      );
      setComparisonPlayer((current) =>
        players.find((player) => player.id === current?.id) ||
        players[1] ||
        players[0],
      );
    } else {
      setSelectedPlayer(null);
      setComparisonPlayer(null);
    }
  }, [players]);




  if (playersLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
        <MobileNavigation />
        <div className="lg:ml-64 p-6">
          <Card>
            <CardContent className="p-8 text-center">
              <RefreshCw className="mx-auto mb-4 h-6 w-6 animate-spin text-blue-600" />
              <p className="font-medium">Loading players from database...</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (playersError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
        <MobileNavigation />
        <div className="lg:ml-64 p-6">
          <Card>
            <CardHeader>
              <CardTitle>Unable to load players</CardTitle>
              <CardDescription>
                Player information could not be retrieved from the database.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-red-600">{playersError}</p>
              <Button onClick={() => fetchPlayers()}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (players.length === 0 || !selectedPlayer) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
        <MobileNavigation />
        <div className="lg:ml-64 p-6">
          <Card>
            <CardHeader>
              <CardTitle>No Players</CardTitle>
              <CardDescription>
                There are currently no players stored in the database.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex gap-3">
              <Button
                onClick={() => navigate("/add-player")}
                className="bg-green-600 hover:bg-green-700"
              >
                Add Player
              </Button>
              <Button variant="outline" onClick={() => fetchPlayers()}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const filteredPlayers = players.filter(
    (player) =>
      player.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedTeam === "all" || player.team === selectedTeam) &&
      (selectedPosition === "all" || player.position === selectedPosition),
  );

  const uniqueTeams = [...new Set(players.map((p) => p.team))];

  // Performance metrics data for charts
  const performanceMetrics = [
    {
      name: "Goals",
      value: selectedPlayer.stats.goals,
      target: 3,
      color: "#8884d8",
    },
    {
      name: "Disposals",
      value: selectedPlayer.stats.disposals,
      target: 35,
      color: "#82ca9d",
    },
    {
      name: "Marks",
      value: selectedPlayer.stats.marks,
      target: 10,
      color: "#ffc658",
    },
    {
      name: "Tackles",
      value: selectedPlayer.stats.tackles,
      target: 8,
      color: "#ff7300",
    },
    {
      name: "Efficiency",
      value: selectedPlayer.stats.efficiency,
      target: 85,
      color: "#00ff00",
    },
    // Stats that weren't measured are left off the chart rather than drawn as 0.
  ].filter((metric) => metric.value !== null);

  const { inside50s, avgSpeed } = selectedPlayer.stats;

  const playerMetrics = [
    { metric: "Goals", value: selectedPlayer.stats.goals, max: 5 },
    {
      metric: "Assists",
      value: inside50s === null ? null : Math.floor(inside50s / 2),
      max: 4,
    },
    { metric: "Tackles", value: selectedPlayer.stats.tackles, max: 10 },
    { metric: "Marks", value: selectedPlayer.stats.marks, max: 12 },
    { metric: "Efficiency", value: selectedPlayer.stats.efficiency, max: 100 },
    {
      metric: "Speed",
      value: avgSpeed === null ? null : Math.round(avgSpeed),
      max: 35,
    },
  ].filter((metric) => metric.value !== null);

  // Export: downloads the players that match the current search and filters.
  const handleExport = () => {
    const today = new Date().toLocaleDateString("en-CA"); // YYYY-MM-DD
    downloadCSV(playersToCsv(filteredPlayers), `players-${today}.csv`);
  };

  // Summary tiles. Only measured values count towards totals and averages.
  const totalGoals = sumStats(filteredPlayers.map((p) => p.stats.goals));
  const totalDisposals = sumStats(filteredPlayers.map((p) => p.stats.disposals));
  const averageEfficiency = averageStats(
    filteredPlayers.map((p) => p.stats.efficiency),
  );


  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <MobileNavigation />

      {/* Main Content */}
      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-6">
          <MockPlayersBanner />

          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Player Performance
              </h1>
              <p className="text-gray-600">
                Real-time AFL player analytics and statistics
              </p>
            </div>
            <div className="flex items-center gap-2">
              {isPlaying && lastUpdated && (
                <span className="text-xs text-gray-500 hidden sm:inline">
                  Updated {lastUpdated.toLocaleTimeString()}
                </span>
              )}
              <Button
                variant={isPlaying ? "default" : "outline"}
                size="sm"
                onClick={() => setIsPlaying(!isPlaying)}
                className="flex items-center gap-2"
              >
                {isPlaying ? (
                  <Pause className="w-4 h-4" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                {isPlaying ? "Pause" : "Play"} Live
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExport}
                disabled={filteredPlayers.length === 0}
                title="Download the players shown below as a CSV file"
              >
                <Download className="w-4 h-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>
          {import.meta.env.DEV && (
            <div style={{ margin: "20px", padding: "10px", border: "1px solid gray" }}>
              <h3>Backend Integration Test</h3>

              <input
                type="file"
                accept=".mp4,.avi,.mov"
                onChange={(e) => setSelectedVideo(e.target.files?.[0] || null)}
              />

              <button onClick={handleUpload}>Upload Video</button>
              <p>Status: {jobStatus}</p>

              {jobStatus === "processing" && <p>Processing video...</p>}
              {jobStatus === "done" && <p>Processing completed successfully.</p>}
              {jobStatus === "failed" && <p>{jobError}</p>}

              {jobStatus === "partial" && (
                <button onClick={handleUpload}>Retry</button>
              )}
              <p>{uploadStatus}</p>

              {jobs.map((job) => (
                <div key={job.job_id}>
                  <p>Job ID: {job.job_id}</p>
                  <p>Status: {job.status}</p>
                </div>
              ))}
            </div>
          )}
          
          {/* Live Clock */}
          <div className="bg-white rounded-xl shadow-sm border px-4 py-3 flex items-center justify-between gap-3">
            <div className="flex-1">
              {ENABLE_LIVE_FEATURES && (
                <LiveClock
                  isLive={isLive}
                  onToggleLive={setIsLive}
                  matchTime={{ quarter: 2, timeRemaining: "15:23" }}
                />
              )}
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {canManagePlayers() && (
                <Button
                  type="button"
                  size="sm"
                  onClick={() => {
                    navigate("/add-player");
                  }}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  Add Player
                </Button>
              )}

              {canManagePlayers() && (
                <>
                  <input
                    type="file"
                    accept=".xlsx"
                    ref={excelInputRef}
                    onChange={handleExcelUpload}
                    className="hidden"
                  />
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => excelInputRef.current?.click()}
                  >
                    Bulk Upload
                  </Button>
                </>
              )}
            </div>
          </div>

          {canManagePlayers() && excelUploadStatus && (
            <div className="bg-white rounded-lg border p-3 text-sm">
              <p
                className={
                  excelUploadErrors.length > 0
                    ? "text-red-600"
                    : "text-green-600"
                }
              >
                {excelUploadStatus}
              </p>
              {excelUploadErrors.length > 0 && (
                <ul className="mt-2 space-y-1 text-xs text-gray-600 list-disc list-inside">
                  {excelUploadErrors.map((err: any, i: number) => (
                    <li key={i}>
                      Row {err.row}: {err.errors.join(", ")}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Quick Stats Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              title="Players Active"
              value={filteredPlayers.length}
              icon={Users}
              color="blue"
              trend="up"
              active={selectedStat === "Players Active"}
              onClick={() => setSelectedStat("Players Active")}
            />

            <StatCard
              title="Total Goals"
              value={formatStat(totalGoals)}
              icon={Target}
              color="green"
              trend="up"
              active={selectedStat === "Total Goals"}
              onClick={() => setSelectedStat("Total Goals")}
            />

            <StatCard
              title="Avg Efficiency"
              value={formatStat(
                averageEfficiency === null ? null : Math.round(averageEfficiency),
                "%",
              )}
              icon={Activity}
              color="purple"
              trend="stable"
              active={selectedStat === "Avg Efficiency"}
              onClick={() => setSelectedStat("Avg Efficiency")}
            />

            <StatCard
              title="Total Disposals"
              value={formatStat(totalDisposals)}
              icon={BarChart3}
              color="orange"
              trend="up"
              active={selectedStat === "Total Disposals"}
              onClick={() => setSelectedStat("Total Disposals")}
            />
          </div>

          {/* Search and Filters */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Search className="w-5 h-5" />
                Player Search & Filters
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <Input
                  placeholder="Search by name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full"
                />
                <Select value={selectedTeam} onValueChange={setSelectedTeam}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by team" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Teams</SelectItem>
                    {uniqueTeams.map((team) => (
                      <SelectItem key={team} value={team}>
                        {team}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select
                  value={selectedPosition}
                  onValueChange={setSelectedPosition}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by position" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Positions</SelectItem>
                    <SelectItem value="Midfielder">Midfielder</SelectItem>
                    <SelectItem value="Forward">Forward</SelectItem>
                    <SelectItem value="Defender">Defender</SelectItem>
                    <SelectItem value="Ruckman">Ruckman</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Player Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredPlayers.slice(0, 12).map((player) => (
              <EnhancedPlayerCard
                key={player.id}
                player={player}
                isSelected={selectedPlayer.id === player.id}
                isFavorite={isFavoritePlayer(player.id)}
                isDeleting={deletingPlayerId === player.id}
                onClick={() => setSelectedPlayer(player)}
                onToggleFavorite={(event) => toggleFavoritePlayer(event, player)}
                onDelete={() => handleDeletePlayer(player.id)}
              />
            ))}
          </div>
          {/* Quick Player Selector */}
          <Card className="w-full sm:w-fit">
            <CardContent className="p-4 flex items-center gap-3">
              <span className="text-sm font-medium text-gray-700 whitespace-nowrap">
                Jump to Player:
              </span>
              <Select
                value={selectedPlayer?.id?.toString()}
                onValueChange={(value) => {
                  const player = players.find((p) => p.id.toString() === value);
                  if (player) setSelectedPlayer(player);
                }}
              >
                <SelectTrigger className="w-64">
                  <SelectValue placeholder="Choose a player" />
                </SelectTrigger>
                <SelectContent>
                  {filteredPlayers.map((player) => (
                    <SelectItem key={player.id} value={player.id.toString()}>
                      #{player.number} {player.name} — {player.team}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </CardContent>
          </Card>

          {/* Selected Player Dashboard */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Large Player Card */}
            <Card className="lg:col-span-1">
              <div
                className="h-32 rounded-t-lg relative flex items-center justify-center"
                style={{ backgroundColor: getTeamColor(selectedPlayer.team) }}
              >
                <div className="text-center text-white">
                  <div className="text-4xl font-bold mb-2">
                    #{selectedPlayer.number}
                  </div>
                  <div className="text-lg font-semibold">
                    {selectedPlayer.name}
                  </div>
                  <div className="text-sm opacity-90">
                    {selectedPlayer.team}
                  </div>
                </div>
              </div>
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="text-center">
                    <Badge variant="outline" className="mb-2">
                      {selectedPlayer.position}
                    </Badge>
                    <p className="text-sm text-gray-600">
                      {selectedPlayer.age}y • {selectedPlayer.height} •{" "}
                      {selectedPlayer.weight}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {formatStat(selectedPlayer.stats.goals)}
                      </div>
                      <div className="text-xs text-gray-600">GOALS</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {formatStat(selectedPlayer.stats.disposals)}
                      </div>
                      <div className="text-xs text-gray-600">DISPOSALS</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>GOAL ACCURACY</span>
                      <span className="font-semibold">
                        {formatStat(selectedPlayer.stats.goalAccuracy, "%")}
                      </span>
                    </div>
                    {/* An empty bar for "not measured", not one filled to 0. */}
                    <Progress
                      value={selectedPlayer.stats.goalAccuracy ?? 0}
                      className="h-2"
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>EFFICIENCY</span>
                      <span className="font-semibold">
                        {formatStat(selectedPlayer.stats.efficiency, "%")}
                      </span>
                    </div>
                    <Progress
                      value={selectedPlayer.stats.efficiency ?? 0}
                      className="h-2"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Charts Section */}
            <div className="lg:col-span-2 space-y-6">
              {/* Chart Controls */}
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Performance Analytics
                    </CardTitle>
                    <div className="flex gap-2">
                      <Button
                        variant={
                          chartType === "possession" ? "default" : "outline"
                        }
                        size="sm"
                        onClick={() => setChartType("possession")}
                      >
                        Possession
                      </Button>
                      <Button
                        variant={
                          chartType === "performance" ? "default" : "outline"
                        }
                        size="sm"
                        onClick={() => setChartType("performance")}
                      >
                        Performance
                      </Button>
                      <Button
                        variant={
                          chartType === "comparison" ? "default" : "outline"
                        }
                        size="sm"
                        onClick={() => setChartType("comparison")}
                      >
                        Comparison
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="h-80">
                    {chartType === "possession" &&
                      selectedPlayer.possessionData.length === 0 && (
                        <NoChartData
                          className="h-full"
                          message="Possession over time hasn't been recorded for this player."
                        />
                      )}

                    {chartType === "possession" &&
                      selectedPlayer.possessionData.length > 0 && (
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={selectedPlayer.possessionData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="time" />
                          <YAxis />
                          <Tooltip />
                          <Area
                            type="monotone"
                            dataKey="possession"
                            stroke={getTeamColor(selectedPlayer.team)}
                            fill={getTeamColor(selectedPlayer.team)}
                            fillOpacity={0.3}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    )}

                    {chartType === "performance" && (
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={playerMetrics}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="metric" />
                          <YAxis />
                          <Tooltip />
                          <Bar
                            dataKey="value"
                            fill={getTeamColor(selectedPlayer.team)}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    )}

                    {chartType === "comparison" && (
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart data={performanceMetrics}>
                          <PolarGrid />
                          <PolarAngleAxis dataKey="name" />
                          <PolarRadiusAxis />
                          <Radar
                            name={selectedPlayer.name}
                            dataKey="value"
                            stroke={getTeamColor(selectedPlayer.team)}
                            fill={getTeamColor(selectedPlayer.team)}
                            fillOpacity={0.3}
                          />
                        </RadarChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Additional Stats and Comparison */}
          <Tabs defaultValue="detailed-stats" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="detailed-stats">Detailed Stats</TabsTrigger>
              <TabsTrigger value="form">Form</TabsTrigger>
              <TabsTrigger value="heatmap">Heat Map</TabsTrigger>
              <TabsTrigger value="compare">Compare Players</TabsTrigger>
            </TabsList>

            <TabsContent value="detailed-stats" className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  title="Kicks"
                  value={formatStat(selectedPlayer.stats.kicks)}
                  color="blue"
                />
                <StatCard
                  title="Handballs"
                  value={formatStat(selectedPlayer.stats.handballs)}
                  color="green"
                />
                <StatCard
                  title="Marks"
                  value={formatStat(selectedPlayer.stats.marks)}
                  color="purple"
                />
                <StatCard
                  title="Tackles"
                  value={formatStat(selectedPlayer.stats.tackles)}
                  color="red"
                />
                <StatCard
                  title="Contested"
                  value={formatStat(selectedPlayer.stats.contested)}
                  color="orange"
                />
                <StatCard
                  title="Uncontested"
                  value={formatStat(selectedPlayer.stats.uncontested)}
                  color="yellow"
                />
                <StatCard
                  title="Inside 50s"
                  value={formatStat(selectedPlayer.stats.inside50s)}
                  color="pink"
                />
                <StatCard
                  title="Clangers"
                  value={formatStat(selectedPlayer.stats.clangers)}
                  color="gray"
                />
              </div>
            </TabsContent>

            <TabsContent value="form" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Form (Last 10 Games)</CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedPlayer.form.length === 0 ? (
                    <NoChartData message="Match-by-match form scores haven't been recorded for this player." />
                  ) : (
                  <>
                  <div className="grid grid-cols-10 gap-2 mb-4">
                    {selectedPlayer.form.map((score, index) => (
                      <div key={index} className="text-center">
                        <div
                          className={`p-2 rounded text-sm font-medium ${score >= 90
                            ? "bg-green-100 text-green-700"
                            : score >= 80
                              ? "bg-yellow-100 text-yellow-700"
                              : "bg-red-100 text-red-700"
                            }`}
                        >
                          {score}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          R{10 - index}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={selectedPlayer.form.map((score, index) => ({
                          round: `R${10 - index}`,
                          score,
                        }))}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="round" />
                        <YAxis domain={[60, 100]} />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey="score"
                          stroke={getTeamColor(selectedPlayer.team)}
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  </>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="heatmap" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Field Position Heat Map</CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedPlayer.heatMap.length === 0 ? (
                    <NoChartData message="Touches by field zone haven't been recorded for this player." />
                  ) : (
                  <div className="space-y-4">
                    {selectedPlayer.heatMap.map((zone, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex justify-between text-sm font-medium">
                          <span>{zone.zone}</span>
                          <span>
                            {zone.touches} touches • {zone.effectiveness}%
                            effective
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <div className="text-xs text-gray-500 mb-1">
                              Touches
                            </div>
                            <Progress
                              value={(zone.touches / 30) * 100}
                              className="h-3"
                            />
                          </div>
                          <div>
                            <div className="text-xs text-gray-500 mb-1">
                              Effectiveness
                            </div>
                            <Progress
                              value={zone.effectiveness}
                              className="h-3"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="compare" className="space-y-4">
              <PlayerComparison
                players={players}
                selectedPlayer1={selectedPlayer}
                selectedPlayer2={comparisonPlayer ?? undefined}
                onPlayerSelect={(player, position) => {
                  if (position === 1) {
                    setSelectedPlayer(player);
                  } else {
                    setComparisonPlayer(player);
                  }
                }}
              />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};