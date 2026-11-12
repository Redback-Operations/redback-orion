import { getAccessToken } from "@/lib/auth";
import { useState, useEffect } from "react";
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
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";

import MobileNavigation from "@/components/MobileNavigation";
import LiveClock from "@/components/LiveClock";
import AFLPlayerCard from "@/components/AFLPlayerCard";
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
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
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
  Filter,
  TrendingUp,
  TrendingDown,
  Target,
  Activity,
  Zap,
  Award,
  Users,
  BarChart3,
  PieChart as PieChartIcon,
  Play,
  Pause,
  RefreshCw,
  Download,
  Settings,
  Eye,
  Star,
  Heart,
  Trash2,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

// =====================================================
// DATABASE PLAYER TYPES
// =====================================================

interface DatabasePlayer {
  id: number;
  name: string;
  team: string;
  position: string;
  photo?: string | null;
  kicks: number;
  handballs: number;
  marks: number;
  tackles: number;
  goals: number;
  efficiency: number;
  age: number;
  height?: string | null;
  weight?: string | null;
  jersey_number: number;
  inside50s: number;
  disposals: number;
  team_logo?: string | null;
  notes?: string | null;
}

// Convert PlayerResponse from the backend into the shape used by the
// existing Player Performance UI. No player records are hard-coded here.
const normalizePlayer = (player: DatabasePlayer) => ({
  id: player.id,
  name: player.name,
  team: player.team,
  position: player.position,
  number: player.jersey_number ?? 0,
  age: player.age ?? 0,
  height: player.height || "-",
  weight: player.weight || "-",
  photo: player.photo || null,
  teamLogo: player.team_logo || null,
  notes: player.notes || "",
  stats: {
    kicks: player.kicks ?? 0,
    handballs: player.handballs ?? 0,
    disposals: player.disposals ?? 0,
    marks: player.marks ?? 0,
    tackles: player.tackles ?? 0,
    goals: player.goals ?? 0,
    behinds: 0,
    efficiency: player.efficiency ?? 0,
    contested: 0,
    uncontested: 0,
    clangers: 0,
    inside50s: player.inside50s ?? 0,
    rebounds: 0,
    onePercenters: 0,
    turnovers: 0,
    intercepted: 0,
    goalAccuracy: 0,
    avgSpeed: 0,
    maxSpeed: 0,
    distance: 0,
  },
  // These historical/advanced datasets are not present in the current
  // Player database model, so they stay empty instead of being invented.
  form: [],
  heatMap: [],
  possessionData: [],
});

// =====================================================
// COMPONENT
// =====================================================

export default function PlayerPerformance() {
  const navigate =
    useNavigate();

  const [
    selectedStat,
    setSelectedStat,
  ] =
    useState<
      string | null
    >(null);

  const [
    isLive,
    setIsLive,
  ] =
    useState(true);

  const [
    isPlaying,
    setIsPlaying,
  ] =
    useState(false);

  const ENABLE_LIVE_FEATURES =
    true;

  const [
    players,
    setPlayers,
  ] =
    useState<
      any[]
    >([]);

  const [
    selectedPlayer,
    setSelectedPlayer,
  ] =
    useState<any>(
      null,
    );

  const [
    comparisonPlayer,
    setComparisonPlayer,
  ] =
    useState<any>(
      null,
    );

  const [
    searchTerm,
    setSearchTerm,
  ] =
    useState("");

  const [
    selectedTeam,
    setSelectedTeam,
  ] =
    useState(
      "all",
    );

  const [
    selectedPosition,
    setSelectedPosition,
  ] =
    useState(
      "all",
    );

  const [
    chartType,
    setChartType,
  ] =
    useState<
      | "possession"
      | "performance"
      | "comparison"
    >(
      "possession",
    );

  const [
    selectedVideo,
    setSelectedVideo,
  ] =
    useState<
      File | null
    >(null);

  const [
    uploadStatus,
    setUploadStatus,
  ] =
    useState("");

  const [
    jobs,
    setJobs,
  ] =
    useState<
      any[]
    >([]);

  const token = getAccessToken();

  const [
    jobStatus,
    setJobStatus,
  ] =
    useState("");

  const [
    jobId,
    setJobId,
  ] =
    useState("");

  const [
    jobError,
    setJobError,
  ] =
    useState("");

  const [
    playersLoading,
    setPlayersLoading,
  ] =
    useState(true);

  const [
    playersError,
    setPlayersError,
  ] =
    useState("");

  const [
    deletingPlayerId,
    setDeletingPlayerId,
  ] =
    useState<number | null>(
      null,
    );

  // =====================================================
  // USER-SPECIFIC FAVOURITE STORAGE
  // =====================================================

  const getFavouriteStorageKey = () => {
    const email =
      localStorage.getItem("userEmail");

    if (!email) {
      return null;
    }

    return `favoritePlayers:${email
      .trim()
      .toLowerCase()}`;
  };

  // =====================================================
  // FAVOURITE PLAYERS
  // =====================================================

  const [
    favoritePlayers,
    setFavoritePlayers,
  ] =
    useState<
      any[]
    >([]);

  // =====================================================
  // VIDEO UPLOAD
  // =====================================================

  const uploadVideo =
    async (
      file: File,
    ) => {
      const formData =
        new FormData();

      formData.append(
        "file",
        file,
      );

      const res =
        await fetch(
          `${BACKEND_URL}/upload`,
          {
            method:
              "POST",

            headers: {
              Authorization:
                `Bearer ${token}`,
            },

            body:
              formData,
          },
        );

      const data =
        await res.json();

      console.log(
        "UPLOAD RESULT:",
        data,
      );

      return data.job_id;
    };

  const fetchJobs =
    async () => {
      const res =
        await fetch(
          `${BACKEND_URL}/jobs?page=1&limit=10`,
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          },
        );

      const data =
        await res.json();

      console.log(
        "JOBS:",
        data,
      );

      return data.jobs;
    };

  const handleUpload =
    async () => {
      if (
        !selectedVideo
      ) {
        setUploadStatus(
          "Please choose a video first",
        );

        return;
      }

      setUploadStatus(
        "Uploading...",
      );

      setJobStatus(
        "processing",
      );

      try {
        const id =
          await uploadVideo(
            selectedVideo,
          );

        setJobId(id);

        setUploadStatus(
          `Upload complete. Job ID: ${id}`,
        );

        setJobStatus(
          "done",
        );

        const latestJobs =
          await fetchJobs();

        setJobs(
          latestJobs ||
            [],
        );
      } catch (err) {
        console.error(
          err,
        );

        setJobStatus(
          "failed",
        );

        setJobError(
          "Upload failed. Please try again.",
        );
      }
    };

  // =====================================================
  // LOAD PLAYERS FROM DATABASE
  // =====================================================

  const loadPlayers =
    async () => {
      setPlayersLoading(
        true,
      );
      setPlayersError(
        "",
      );

      try {
        const response =
          await fetch(
            `${BACKEND_URL}/api/players`,
            {
              method:
                "GET",
              headers: {
                Accept:
                  "application/json",
                ...(token
                  ? {
                      Authorization:
                        `Bearer ${token}`,
                    }
                  : {}),
              },
            },
          );

        const data =
          await response
            .json()
            .catch(
              () => null,
            );

        if (
          !response.ok
        ) {
          throw new Error(
            data?.detail ||
              data?.message ||
              `Failed to fetch players (${response.status})`,
          );
        }

        if (
          !Array.isArray(
            data,
          )
        ) {
          throw new Error(
            "Invalid player response received from server.",
          );
        }

        const databasePlayers =
          data.map(
            (
              player: DatabasePlayer,
            ) =>
              normalizePlayer(
                player,
              ),
          );

        // Database is the only source of player records.
        setPlayers(
          databasePlayers,
        );
      } catch (
        error
      ) {
        console.error(
          "PLAYER DATABASE ERROR:",
          error,
        );

        // Never fall back to hard-coded/generated players.
        setPlayers(
          [],
        );

        setPlayersError(
          error instanceof
            Error
            ? error.message
            : "Unable to load players from database.",
        );
      } finally {
        setPlayersLoading(
          false,
        );
      }
    };

  useEffect(() => {
    loadPlayers();
  }, []);

  // =====================================================
  // LOAD FAVOURITES
  // =====================================================

  useEffect(() => {
    try {
      const favouriteKey =
        getFavouriteStorageKey();

      if (!favouriteKey) {
        setFavoritePlayers([]);
        return;
      }

      const storedFavorites =
        JSON.parse(
          localStorage.getItem(
            favouriteKey,
          ) ||
            "[]",
        );

      setFavoritePlayers(
        Array.isArray(
          storedFavorites,
        )
          ? storedFavorites
          : [],
      );
    } catch (
      error
    ) {
      console.error(
        "Failed to load favorite players:",
        error,
      );

      setFavoritePlayers(
        [],
      );
    }
  }, []);

  // =====================================================
  // INITIAL / REFRESHED PLAYER SELECTION
  // =====================================================

  useEffect(() => {
    if (
      players.length >
      0
    ) {
      setSelectedPlayer(
        (current: any) =>
          players.find(
            (player) =>
              player.id ===
              current?.id,
          ) ||
          players[0],
      );

      setComparisonPlayer(
        (current: any) =>
          players.find(
            (player) =>
              player.id ===
              current?.id,
          ) ||
          players[1] ||
          players[0],
      );
    } else {
      setSelectedPlayer(
        null,
      );
      setComparisonPlayer(
        null,
      );
    }
  }, [players]);

  // =====================================================
  // LIVE DISPLAY STATE
  // =====================================================

  // Player statistics are not randomly simulated here. Player values shown
  // on this page come from the database. The existing live controls are kept
  // in the UI for future real-time service integration.

  if (
    playersLoading
  ) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
        <MobileNavigation />

        <div className="lg:ml-64 p-6">
          <Card>
            <CardContent className="p-8 text-center">
              <RefreshCw className="mx-auto mb-4 h-6 w-6 animate-spin text-blue-600" />

              <p className="font-medium">
                Loading players from database...
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (
    playersError
  ) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
        <MobileNavigation />

        <div className="lg:ml-64 p-6">
          <Card>
            <CardHeader>
              <CardTitle>
                Unable to load players
              </CardTitle>

              <CardDescription>
                Player information could not be retrieved from the database.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              <p className="text-sm text-red-600">
                {playersError}
              </p>

              <Button
                onClick={
                  loadPlayers
                }
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (
    players.length ===
      0 ||
    !selectedPlayer
  ) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
        <MobileNavigation />

        <div className="lg:ml-64 p-6">
          <Card>
            <CardHeader>
              <CardTitle>
                No Players
              </CardTitle>

              <CardDescription>
                There are currently no players stored in the database.
              </CardDescription>
            </CardHeader>

            <CardContent className="flex gap-3">
              <Button
                onClick={() =>
                  navigate(
                    "/add-player",
                  )
                }
                className="bg-green-600 hover:bg-green-700"
              >
                Add Player
              </Button>

              <Button
                variant="outline"
                onClick={
                  loadPlayers
                }
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // =====================================================
  // FILTER PLAYERS
  // =====================================================

  const filteredPlayers =
    players.filter(
      (player) =>
        player.name
          .toLowerCase()
          .includes(
            searchTerm.toLowerCase(),
          ) &&
        (selectedTeam ===
          "all" ||
          player.team ===
            selectedTeam) &&
        (selectedPosition ===
          "all" ||
          player.position ===
            selectedPosition),
    );

  const uniqueTeams =
    [
      ...new Set(
        players.map(
          (p) =>
            p.team,
        ),
      ),
    ];

  // =====================================================
  // CHART DATA
  // =====================================================

  const performanceMetrics =
    [
      {
        name:
          "Goals",
        value:
          selectedPlayer
            .stats.goals,
        target:
          3,
        color:
          "#8884d8",
      },

      {
        name:
          "Disposals",
        value:
          selectedPlayer
            .stats
            .disposals,
        target:
          35,
        color:
          "#82ca9d",
      },

      {
        name:
          "Marks",
        value:
          selectedPlayer
            .stats.marks,
        target:
          10,
        color:
          "#ffc658",
      },

      {
        name:
          "Tackles",
        value:
          selectedPlayer
            .stats
            .tackles,
        target:
          8,
        color:
          "#ff7300",
      },

      {
        name:
          "Efficiency",
        value:
          selectedPlayer
            .stats
            .efficiency,
        target:
          85,
        color:
          "#00ff00",
      },
    ];

  const playerMetrics =
    [
      {
        metric:
          "Goals",
        value:
          selectedPlayer
            .stats.goals,
        max:
          5,
      },

      {
        metric:
          "Assists",

        value:
          Math.floor(
            selectedPlayer
              .stats
              .inside50s /
              2,
          ),

        max:
          4,
      },

      {
        metric:
          "Tackles",
        value:
          selectedPlayer
            .stats
            .tackles,
        max:
          10,
      },

      {
        metric:
          "Marks",
        value:
          selectedPlayer
            .stats.marks,
        max:
          12,
      },

      {
        metric:
          "Efficiency",
        value:
          selectedPlayer
            .stats
            .efficiency,
        max:
          100,
      },

      {
        metric:
          "Speed",

        value:
          Math.round(
            selectedPlayer
              .stats
              .avgSpeed,
          ),

        max:
          35,
      },
    ];

  // =====================================================
  // FAVOURITE FUNCTIONS
  // =====================================================

  const isFavoritePlayer =
    (
      playerId: number,
    ) => {
      return favoritePlayers.some(
        (
          favorite,
        ) =>
          favorite.id ===
          playerId,
      );
    };

  const toggleFavoritePlayer =
    (
      event: React.MouseEvent<HTMLButtonElement>,
      player: any,
    ) => {
      // Prevent heart click from selecting player card
      event.stopPropagation();

      const favouriteKey =
        getFavouriteStorageKey();

      if (!favouriteKey) {
        console.error(
          "Cannot save favourites: no logged-in user email found.",
        );
        return;
      }

      const alreadyFavorite =
        isFavoritePlayer(
          player.id,
        );

      const updatedFavorites =
        alreadyFavorite
          ? favoritePlayers.filter(
              (
                favorite,
              ) =>
                favorite.id !==
                player.id,
            )
          : [
              ...favoritePlayers,
              player,
            ];

      setFavoritePlayers(
        updatedFavorites,
      );

      localStorage.setItem(
        favouriteKey,
        JSON.stringify(
          updatedFavorites,
        ),
      );
    };

  // =====================================================
  // DELETE PLAYER FROM DATABASE
  // =====================================================

  const handleDeletePlayer =
    async (
      event: React.MouseEvent<HTMLButtonElement>,
      player: any,
    ) => {
      // Prevent delete click from selecting the player card.
      event.stopPropagation();

      const confirmed =
        window.confirm(
          `Delete ${player.name}? This will permanently remove the player from the database.`,
        );

      if (!confirmed) {
        return;
      }

      setDeletingPlayerId(
        player.id,
      );
      setPlayersError(
        "",
      );

      try {
        const response =
          await fetch(
            `${BACKEND_URL}/api/player/${player.id}`,
            {
              method:
                "DELETE",
              headers: {
                Accept:
                  "application/json",
                ...(token
                  ? {
                      Authorization:
                        `Bearer ${token}`,
                    }
                  : {}),
              },
            },
          );

        const data =
          await response
            .json()
            .catch(
              () => null,
            );

        if (
          !response.ok
        ) {
          throw new Error(
            data?.detail ||
              data?.message ||
              `Failed to delete player (${response.status})`,
          );
        }

        const remainingPlayers =
          players.filter(
            (
              existingPlayer,
            ) =>
              existingPlayer.id !==
              player.id,
          );

        setPlayers(
          remainingPlayers,
        );

        // If the deleted player is currently selected, select the first remaining player.
        if (
          selectedPlayer?.id ===
          player.id
        ) {
          setSelectedPlayer(
            remainingPlayers[0] ??
              null,
          );
        }

        // Keep comparison selection valid after deletion.
        if (
          comparisonPlayer?.id ===
          player.id
        ) {
          setComparisonPlayer(
            remainingPlayers[0] ??
              null,
          );
        }

        // Remove deleted player from favourites too.
        const updatedFavorites =
          favoritePlayers.filter(
            (
              favorite,
            ) =>
              favorite.id !==
              player.id,
          );

        setFavoritePlayers(
          updatedFavorites,
        );

        const favouriteKey =
          getFavouriteStorageKey();

        if (favouriteKey) {
          localStorage.setItem(
            favouriteKey,
            JSON.stringify(
              updatedFavorites,
            ),
          );
        }
      } catch (
        error
      ) {
        console.error(
          "PLAYER DELETE ERROR:",
          error,
        );

        setPlayersError(
          error instanceof
            Error
            ? error.message
            : "Unable to delete player.",
        );
      } finally {
        setDeletingPlayerId(
          null,
        );
      }
    };

  // =====================================================
  // TEAM COLOURS
  // =====================================================

  const getTeamColor =
    (
      team: string,
    ) => {
      const teamColors: Record<
        string,
        string
      > = {
        "Western Bulldogs":
          "#1E40AF",

        Brisbane:
          "#8B0000",

        Richmond:
          "#FFD700",

        Geelong:
          "#1E3A8A",

        Melbourne:
          "#DC2626",

        Carlton:
          "#3B82F6",

        Adelaide:
          "#EF4444",

        "West Coast":
          "#1D4ED8",

        Collingwood:
          "#000000",

        Essendon:
          "#B91C1C",

        Fremantle:
          "#9333EA",
      };

      return (
        teamColors[
          team
        ] ||
        "#6B7280"
      );
    };

  // =====================================================
  // TEAM LOGOS
  // =====================================================

  const getTeamLogo =
    (
      team: string,
    ) => {
      const teamLogos: Record<
        string,
        string
      > = {
        "Western Bulldogs":
          "/team-logos/western-bulldogs.svg",

        Richmond:
          "/team-logos/richmond.svg",

        Geelong:
          "/team-logos/geelong.svg",

        Melbourne:
          "/team-logos/melbourne.svg",

        Carlton:
          "/team-logos/carlton.svg",

        Adelaide:
          "/team-logos/adelaide.svg",

        "West Coast":
          "/team-logos/west-coast.svg",

        Collingwood:
          "/team-logos/collingwood.svg",

        Essendon:
          "/team-logos/essendon.svg",

        Fremantle:
          "/team-logos/fremantle.svg",

        Brisbane:
          "/team-logos/brisbane.svg",

        Sydney:
          "/team-logos/sydney.svg",

        "St Kilda":
          "/team-logos/st-kilda.svg",

        "Port Adelaide":
          "/team-logos/port-adelaide.svg",

        "North Melbourne":
          "/team-logos/north-melbourne.svg",

        "Gold Coast":
          "/team-logos/gold-coast.svg",

        "GWS Giants":
          "/team-logos/gws-giants.svg",

        Hawthorn:
          "/team-logos/hawthorn.svg",
      };

      return (
        teamLogos[
          team
        ] ||
        "/team-logos/default.svg"
      );
    };

  // =====================================================
  // QUICK STAT CARD
  // =====================================================

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
    title:
      string;

    value:
      | string
      | number;

    subtitle?:
      string;

    trend?:
      | "up"
      | "down"
      | "stable";

    color?:
      string;

    icon?:
      any;

    active?:
      boolean;

    onClick?:
      () => void;
  }) => (
    <Card
      className={`relative overflow-hidden transition-all duration-200 ${
        onClick
          ? "cursor-pointer"
          : ""
      } ${
        active
          ? "ring-2 ring-blue-500 ring-offset-2 shadow-lg"
          : ""
      }`}
      onClick={
        onClick
      }
    >
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            {Icon && (
              <Icon
                className={`w-4 h-4 text-${color}-600`}
              />
            )}

            <span className="text-sm font-medium text-gray-600">
              {title}
            </span>
          </div>

          {trend && (
            <div className="flex items-center">
              {trend ===
                "up" && (
                <TrendingUp className="w-3 h-3 text-green-500" />
              )}

              {trend ===
                "down" && (
                <TrendingDown className="w-3 h-3 text-red-500" />
              )}

              {trend ===
                "stable" && (
                <div className="w-3 h-3 rounded-full bg-gray-400" />
              )}
            </div>
          )}
        </div>

        <div
          className={`text-2xl font-bold text-${color}-600 mb-1`}
        >
          {value}
        </div>

        {subtitle && (
          <div className="text-xs text-gray-500">
            {subtitle}
          </div>
        )}

        <div
          className={`absolute bottom-0 right-0 w-16 h-16 bg-${color}-100 rounded-full -mr-8 -mb-8 opacity-50`}
        />
      </CardContent>
    </Card>
  );

  // =====================================================
  // PLAYER CARD WITH FAVOURITE HEART
  // =====================================================

  const EnhancedPlayerCard =
    ({
      player,
      isSelected,
      onClick,
    }: any) => (
      <Card
        className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
          isSelected
            ? "ring-2 ring-blue-500 ring-offset-2"
            : ""
        }`}
        onClick={
          onClick
        }
      >
        {/* Team Header */}
        <div
          className="h-24 rounded-t-lg relative"
          style={{
            backgroundColor:
              getTeamColor(
                player.team,
              ),
          }}
        >
          <div className="absolute top-4 left-4 flex items-start gap-3 text-white">
            <div className="w-10 h-10 rounded-full bg-white shadow-sm flex items-center justify-center overflow-hidden">
              <img
                src={
                  player.teamLogo ||
                  getTeamLogo(
                    player.team,
                  )
                }
                alt={`${player.team} logo`}
                className="w-10 h-10 object-cover scale-110"
                onError={(
                  e,
                ) => {
                  e.currentTarget.src =
                    "/team-logos/default.svg";
                }}
              />
            </div>

            <div>
              <div className="text-2xl font-bold">
                #
                {
                  player.number
                }
              </div>

              <div className="text-sm">
                {
                  player.team
                }
              </div>
            </div>
          </div>

          <div className="absolute top-4 right-4 text-white text-right">
            <div className="text-xl font-bold">
              {
                player
                  .stats
                  .disposals
              }
            </div>

            <div className="text-xs">
              DISPOSALS
            </div>
          </div>
        </div>

        {/* Player Content */}
        <CardContent className="p-4">
          <div className="flex items-center gap-3 mb-3">
            {player.photo ? (
              <img
                src={
                  player.photo
                }
                alt={
                  player.name
                }
                className="w-12 h-12 rounded-full object-cover border-2 border-white shadow-lg"
              />
            ) : (
              <div className="w-12 h-12 rounded-full bg-gray-300 border-2 border-white shadow-lg flex items-center justify-center">
                <span className="text-sm font-bold text-gray-600">
                  {player.name
                    .split(
                      " ",
                    )
                    .map(
                      (
                        n: string,
                      ) =>
                        n[0],
                    )
                    .join(
                      "",
                    )}
                </span>
              </div>
            )}

            {/* Player Name */}
            <div className="flex-1">
              <h3 className="font-bold text-sm leading-tight">
                {
                  player.name
                }
              </h3>

              <p className="text-xs text-gray-600">
                {
                  player.position
                }
              </p>
            </div>

            {/* Player Actions */}
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={(
                  event,
                ) =>
                  handleDeletePlayer(
                    event,
                    player,
                  )
                }
                disabled={
                  deletingPlayerId ===
                  player.id
                }
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full transition-all duration-200 hover:scale-110 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                aria-label={`Delete ${player.name}`}
                title="Delete player"
              >
                <Trash2 className="h-4 w-4 text-gray-400 hover:text-red-600" />
              </button>

              <button
                type="button"
                onClick={(
                  event,
                ) =>
                  toggleFavoritePlayer(
                    event,
                    player,
                  )
                }
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full transition-all duration-200 hover:scale-110 hover:bg-red-50"
                aria-label={
                  isFavoritePlayer(
                    player.id,
                  )
                    ? `Remove ${player.name} from favourites`
                    : `Add ${player.name} to favourites`
                }
                title={
                  isFavoritePlayer(
                    player.id,
                  )
                    ? "Remove from favourites"
                    : "Add to favourites"
                }
              >
                <Heart
                  className={`h-5 w-5 transition-all duration-200 ${
                    isFavoritePlayer(
                      player.id,
                    )
                      ? "fill-red-500 text-red-500"
                      : "text-gray-400 hover:text-red-500"
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-2 text-center text-xs">
            <div className="bg-blue-50 p-2 rounded">
              <div className="font-bold text-blue-600">
                {
                  player
                    .stats
                    .goals
                }
              </div>

              <div className="text-gray-600">
                Goals
              </div>
            </div>

            <div className="bg-green-50 p-2 rounded">
              <div className="font-bold text-green-600">
                {
                  player
                    .stats
                    .marks
                }
              </div>

              <div className="text-gray-600">
                Marks
              </div>
            </div>

            <div className="bg-purple-50 p-2 rounded">
              <div className="font-bold text-purple-600">
                {
                  player
                    .stats
                    .efficiency
                }
                %
              </div>

              <div className="text-gray-600">
                Eff.
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <MobileNavigation />

      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-6">
          {/* Header */}

          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Player Performance
              </h1>

              <p className="text-gray-600">
                Real-time AFL player analytics and statistics
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant={
                  isPlaying
                    ? "default"
                    : "outline"
                }
                size="sm"
                onClick={() =>
                  setIsPlaying(
                    !isPlaying,
                  )
                }
                className="flex items-center gap-2"
              >
                {isPlaying ? (
                  <Pause className="w-4 h-4" />
                ) : (
                  <Play className="w-4 h-4" />
                )}

                {isPlaying
                  ? "Pause"
                  : "Play"}{" "}
                Live
              </Button>

              <Button
                variant="outline"
                size="sm"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>
          </div>

          {/* Live Clock */}

          <div className="bg-white rounded-xl shadow-sm border px-4 py-3 flex items-center justify-between gap-3">
            <div className="flex-1">
              {ENABLE_LIVE_FEATURES && (
                <LiveClock
                  isLive={
                    isLive
                  }
                  onToggleLive={
                    setIsLive
                  }
                  matchTime={{
                    quarter:
                      2,
                    timeRemaining:
                      "15:23",
                  }}
                />
              )}
            </div>

            <Button
              type="button"
              size="sm"
              onClick={() => {
                console.log(
                  "navigating to add-player",
                );

                navigate(
                  "/add-player",
                );
              }}
              className="bg-green-600 hover:bg-green-700 text-white shrink-0"
            >
              Add Player
            </Button>
          </div>

          {/* Quick Stats */}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              title="Players Active"
              value={
                filteredPlayers.length
              }
              icon={
                Users
              }
              color="blue"
              trend="up"
              active={
                selectedStat ===
                "Players Active"
              }
              onClick={() =>
                setSelectedStat(
                  "Players Active",
                )
              }
            />

            <StatCard
              title="Total Goals"
              value={filteredPlayers.reduce(
                (
                  sum,
                  p,
                ) =>
                  sum +
                  p.stats
                    .goals,
                0,
              )}
              icon={
                Target
              }
              color="green"
              trend="up"
              active={
                selectedStat ===
                "Total Goals"
              }
              onClick={() =>
                setSelectedStat(
                  "Total Goals",
                )
              }
            />

            <StatCard
              title="Avg Efficiency"
              value={`${
                filteredPlayers.length >
                0
                  ? Math.round(
                      filteredPlayers.reduce(
                        (
                          sum,
                          p,
                        ) =>
                          sum +
                          p.stats
                            .efficiency,
                        0,
                      ) /
                        filteredPlayers.length,
                    )
                  : 0
              }%`}
              icon={
                Activity
              }
              color="purple"
              trend="stable"
              active={
                selectedStat ===
                "Avg Efficiency"
              }
              onClick={() =>
                setSelectedStat(
                  "Avg Efficiency",
                )
              }
            />

            <StatCard
              title="Total Disposals"
              value={filteredPlayers.reduce(
                (
                  sum,
                  p,
                ) =>
                  sum +
                  p.stats
                    .disposals,
                0,
              )}
              icon={
                BarChart3
              }
              color="orange"
              trend="up"
              active={
                selectedStat ===
                "Total Disposals"
              }
              onClick={() =>
                setSelectedStat(
                  "Total Disposals",
                )
              }
            />
          </div>

          {/* Search & Filters */}

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Search className="w-5 h-5" />
                Player Search &
                Filters
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <Input
                  placeholder="Search by name..."
                  value={
                    searchTerm
                  }
                  onChange={(
                    e,
                  ) =>
                    setSearchTerm(
                      e.target
                        .value,
                    )
                  }
                  className="w-full"
                />

                <Select
                  value={
                    selectedTeam
                  }
                  onValueChange={
                    setSelectedTeam
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by team" />
                  </SelectTrigger>

                  <SelectContent>
                    <SelectItem value="all">
                      All Teams
                    </SelectItem>

                    {uniqueTeams.map(
                      (
                        team,
                      ) => (
                        <SelectItem
                          key={
                            team
                          }
                          value={
                            team
                          }
                        >
                          {
                            team
                          }
                        </SelectItem>
                      ),
                    )}
                  </SelectContent>
                </Select>

                <Select
                  value={
                    selectedPosition
                  }
                  onValueChange={
                    setSelectedPosition
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by position" />
                  </SelectTrigger>

                  <SelectContent>
                    <SelectItem value="all">
                      All Positions
                    </SelectItem>

                    <SelectItem value="Midfielder">
                      Midfielder
                    </SelectItem>

                    <SelectItem value="Forward">
                      Forward
                    </SelectItem>

                    <SelectItem value="Defender">
                      Defender
                    </SelectItem>

                    <SelectItem value="Ruckman">
                      Ruckman
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Player Cards */}

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredPlayers
              .slice(
                0,
                12,
              )
              .map(
                (
                  player,
                ) => (
                  <EnhancedPlayerCard
                    key={
                      player.id
                    }
                    player={
                      player
                    }
                    isSelected={
                      selectedPlayer.id ===
                      player.id
                    }
                    onClick={() =>
                      setSelectedPlayer(
                        player,
                      )
                    }
                  />
                ),
              )}
          </div>

          {/* Selected Player Dashboard */}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Selected Player Card */}

            <Card className="lg:col-span-1">
              <div
                className="h-32 rounded-t-lg relative flex items-center justify-center"
                style={{
                  backgroundColor:
                    getTeamColor(
                      selectedPlayer.team,
                    ),
                }}
              >
                <div className="text-center text-white">
                  <div className="text-4xl font-bold mb-2">
                    #
                    {
                      selectedPlayer.number
                    }
                  </div>

                  <div className="text-lg font-semibold">
                    {
                      selectedPlayer.name
                    }
                  </div>

                  <div className="text-sm opacity-90">
                    {
                      selectedPlayer.team
                    }
                  </div>
                </div>
              </div>

              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="text-center">
                    <Badge
                      variant="outline"
                      className="mb-2"
                    >
                      {
                        selectedPlayer.position
                      }
                    </Badge>

                    <p className="text-sm text-gray-600">
                      {
                        selectedPlayer.age
                      }
                      y •{" "}
                      {
                        selectedPlayer.height
                      }{" "}
                      •{" "}
                      {
                        selectedPlayer.weight
                      }
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {
                          selectedPlayer
                            .stats
                            .goals
                        }
                      </div>

                      <div className="text-xs text-gray-600">
                        GOALS
                      </div>
                    </div>

                    <div className="bg-green-50 p-3 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {
                          selectedPlayer
                            .stats
                            .disposals
                        }
                      </div>

                      <div className="text-xs text-gray-600">
                        DISPOSALS
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>
                        GOAL ACCURACY
                      </span>

                      <span className="font-semibold">
                        {
                          selectedPlayer
                            .stats
                            .goalAccuracy
                        }
                        %
                      </span>
                    </div>

                    <Progress
                      value={
                        selectedPlayer
                          .stats
                          .goalAccuracy
                      }
                      className="h-2"
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>
                        EFFICIENCY
                      </span>

                      <span className="font-semibold">
                        {
                          selectedPlayer
                            .stats
                            .efficiency
                        }
                        %
                      </span>
                    </div>

                    <Progress
                      value={
                        selectedPlayer
                          .stats
                          .efficiency
                      }
                      className="h-2"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Charts */}

            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex flex-col gap-3">
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      Performance
                      Analytics
                    </CardTitle>

                    <div className="grid grid-cols-3 gap-2">
                      <Button
                        variant={
                          chartType ===
                          "possession"
                            ? "default"
                            : "outline"
                        }
                        size="sm"
                        onClick={() =>
                          setChartType(
                            "possession",
                          )
                        }
                        className="w-full px-1 text-xs sm:px-3 sm:text-sm"
                      >
                        Possession
                      </Button>

                      <Button
                        variant={
                          chartType ===
                          "performance"
                            ? "default"
                            : "outline"
                        }
                        size="sm"
                        onClick={() =>
                          setChartType(
                            "performance",
                          )
                        }
                        className="w-full px-1 text-xs sm:px-3 sm:text-sm"
                      >
                        Performance
                      </Button>

                      <Button
                        variant={
                          chartType ===
                          "comparison"
                            ? "default"
                            : "outline"
                        }
                        size="sm"
                        onClick={() =>
                          setChartType(
                            "comparison",
                          )
                        }
                        className="w-full px-1 text-xs sm:px-3 sm:text-sm"
                      >
                        Comparison
                      </Button>
                    </div>
                  </div>
                </CardHeader>

                <CardContent>
                  <div className="h-80">
                    {chartType ===
                      "possession" && (
                      <ResponsiveContainer
                        width="100%"
                        height="100%"
                      >
                        <AreaChart
                          data={
                            selectedPlayer.possessionData
                          }
                        >
                          <CartesianGrid strokeDasharray="3 3" />

                          <XAxis dataKey="time" />

                          <YAxis />

                          <Tooltip />

                          <Area
                            type="monotone"
                            dataKey="possession"
                            stroke={getTeamColor(
                              selectedPlayer.team,
                            )}
                            fill={getTeamColor(
                              selectedPlayer.team,
                            )}
                            fillOpacity={
                              0.3
                            }
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    )}

                    {chartType ===
                      "performance" && (
                      <ResponsiveContainer
                        width="100%"
                        height="100%"
                      >
                        <BarChart
                          data={
                            playerMetrics
                          }
                        >
                          <CartesianGrid strokeDasharray="3 3" />

                          <XAxis dataKey="metric" />

                          <YAxis />

                          <Tooltip />

                          <Bar
                            dataKey="value"
                            fill={getTeamColor(
                              selectedPlayer.team,
                            )}
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    )}

                    {chartType ===
                      "comparison" && (
                      <ResponsiveContainer
                        width="100%"
                        height="100%"
                      >
                        <RadarChart
                          data={
                            performanceMetrics
                          }
                        >
                          <PolarGrid />

                          <PolarAngleAxis dataKey="name" />

                          <PolarRadiusAxis />

                          <Radar
                            name={
                              selectedPlayer.name
                            }
                            dataKey="value"
                            stroke={getTeamColor(
                              selectedPlayer.team,
                            )}
                            fill={getTeamColor(
                              selectedPlayer.team,
                            )}
                            fillOpacity={
                              0.3
                            }
                          />
                        </RadarChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Additional Stats */}

          <Tabs
            defaultValue="detailed-stats"
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="detailed-stats">
                Detailed Stats
              </TabsTrigger>

              <TabsTrigger value="form">
                Form
              </TabsTrigger>

              <TabsTrigger value="heatmap">
                Heat Map
              </TabsTrigger>

              <TabsTrigger value="compare">
                Compare Players
              </TabsTrigger>
            </TabsList>

            {/* Detailed */}

            <TabsContent
              value="detailed-stats"
              className="space-y-4"
            >
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  title="Kicks"
                  value={
                    selectedPlayer
                      .stats
                      .kicks
                  }
                  color="blue"
                />

                <StatCard
                  title="Handballs"
                  value={
                    selectedPlayer
                      .stats
                      .handballs
                  }
                  color="green"
                />

                <StatCard
                  title="Marks"
                  value={
                    selectedPlayer
                      .stats
                      .marks
                  }
                  color="purple"
                />

                <StatCard
                  title="Tackles"
                  value={
                    selectedPlayer
                      .stats
                      .tackles
                  }
                  color="red"
                />

                <StatCard
                  title="Contested"
                  value={
                    selectedPlayer
                      .stats
                      .contested
                  }
                  color="orange"
                />

                <StatCard
                  title="Uncontested"
                  value={
                    selectedPlayer
                      .stats
                      .uncontested
                  }
                  color="yellow"
                />

                <StatCard
                  title="Inside 50s"
                  value={
                    selectedPlayer
                      .stats
                      .inside50s
                  }
                  color="pink"
                />

                <StatCard
                  title="Clangers"
                  value={
                    selectedPlayer
                      .stats
                      .clangers
                  }
                  color="gray"
                />
              </div>
            </TabsContent>

            {/* Form */}

            <TabsContent
              value="form"
              className="space-y-4"
            >
              <Card>
                <CardHeader>
                  <CardTitle>
                    Recent Form
                    (Last 10
                    Games)
                  </CardTitle>
                </CardHeader>

                <CardContent>
                  <div className="grid grid-cols-10 gap-2 mb-4">
                    {selectedPlayer.form.map(
                      (
                        score,
                        index,
                      ) => (
                        <div
                          key={
                            index
                          }
                          className="text-center"
                        >
                          <div
                            className={`p-2 rounded text-sm font-medium ${
                              score >=
                              90
                                ? "bg-green-100 text-green-700"
                                : score >=
                                    80
                                  ? "bg-yellow-100 text-yellow-700"
                                  : "bg-red-100 text-red-700"
                            }`}
                          >
                            {
                              score
                            }
                          </div>

                          <div className="text-xs text-gray-500 mt-1">
                            R
                            {10 -
                              index}
                          </div>
                        </div>
                      ),
                    )}
                  </div>

                  <div className="h-64">
                    <ResponsiveContainer
                      width="100%"
                      height="100%"
                    >
                      <LineChart
                        data={selectedPlayer.form.map(
                          (
                            score,
                            index,
                          ) => ({
                            round: `R${
                              10 -
                              index
                            }`,
                            score,
                          }),
                        )}
                      >
                        <CartesianGrid strokeDasharray="3 3" />

                        <XAxis dataKey="round" />

                        <YAxis
                          domain={[
                            60,
                            100,
                          ]}
                        />

                        <Tooltip />

                        <Line
                          type="monotone"
                          dataKey="score"
                          stroke={getTeamColor(
                            selectedPlayer.team,
                          )}
                          strokeWidth={
                            2
                          }
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Heat Map */}

            <TabsContent
              value="heatmap"
              className="space-y-4"
            >
              <Card>
                <CardHeader>
                  <CardTitle>
                    Field Position
                    Heat Map
                  </CardTitle>
                </CardHeader>

                <CardContent>
                  <div className="space-y-4">
                    {selectedPlayer.heatMap.map(
                      (
                        zone,
                        index,
                      ) => (
                        <div
                          key={
                            index
                          }
                          className="space-y-2"
                        >
                          <div className="flex justify-between text-sm font-medium">
                            <span>
                              {
                                zone.zone
                              }
                            </span>

                            <span>
                              {
                                zone.touches
                              }{" "}
                              touches •{" "}
                              {
                                zone.effectiveness
                              }
                              %
                              effective
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <div className="text-xs text-gray-500 mb-1">
                                Touches
                              </div>

                              <Progress
                                value={
                                  (zone.touches /
                                    30) *
                                  100
                                }
                                className="h-3"
                              />
                            </div>

                            <div>
                              <div className="text-xs text-gray-500 mb-1">
                                Effectiveness
                              </div>

                              <Progress
                                value={
                                  zone.effectiveness
                                }
                                className="h-3"
                              />
                            </div>
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Comparison */}

            <TabsContent
              value="compare"
              className="space-y-4"
            >
              <PlayerComparison
                players={
                  players
                }
                selectedPlayer1={
                  selectedPlayer
                }
                selectedPlayer2={
                  comparisonPlayer
                }
                onPlayerSelect={(
                  player,
                  position,
                ) => {
                  if (
                    position ===
                    1
                  ) {
                    setSelectedPlayer(
                      player,
                    );
                  } else {
                    setComparisonPlayer(
                      player,
                    );
                  }
                }}
              />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
