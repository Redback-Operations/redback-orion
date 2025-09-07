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
} from "lucide-react";

// Comprehensive player data with enhanced AFL statistics
const generatePlayerData = () => {
  const teams = [
    "Western Bulldogs",
    "Richmond",
    "Geelong",
    "Melbourne",
    "Carlton",
    "Adelaide",
    "West Coast",
    "Collingwood",
    "Essendon",
    "Fremantle",
    "Brisbane",
    "Sydney",
    "St Kilda",
    "Port Adelaide",
    "North Melbourne",
    "Gold Coast",
    "GWS Giants",
    "Hawthorn",
  ];

  const positions = ["Midfielder", "Forward", "Defender", "Ruckman"];

  const players = [
    {
      id: 1,
      name: "Marcus Bontempelli",
      team: "Western Bulldogs",
      position: "Midfielder",
      number: 4,
      age: 28,
      height: "1.93m",
      weight: "92kg",
      photo:
        "https://cdn.builder.io/api/v1/image/assets%2Faf9aef6647464a4bb798d09aa34aaa76%2F35a79c1a43bd4be1a3d3d6a95b0b1a79?format=webp&width=100",
      stats: {
        kicks: 28,
        handballs: 12,
        disposals: 40,
        marks: 8,
        tackles: 6,
        goals: 2,
        behinds: 1,
        efficiency: 87,
        contested: 18,
        uncontested: 22,
        clangers: 3,
        inside50s: 7,
        rebounds: 4,
        onePercenters: 2,
        turnovers: 4,
        intercepted: 2,
        goalAccuracy: 67,
        avgSpeed: 24.8,
        maxSpeed: 32.4,
        distance: 12.8,
      },
      form: [85, 89, 91, 87, 93, 88, 87, 90, 85, 92],
      heatMap: [
        { zone: "Forward 50", touches: 12, effectiveness: 85 },
        { zone: "Center Bounce", touches: 18, effectiveness: 92 },
        { zone: "Defensive 50", touches: 10, effectiveness: 78 },
      ],
      possessionData: [
        { time: 0, possession: 12 },
        { time: 5, possession: 8 },
        { time: 10, possession: 15 },
        { time: 15, possession: 20 },
        { time: 20, possession: 18 },
        { time: 25, possession: 22 },
        { time: 30, possession: 25 },
      ],
    },
    {
      id: 2,
      name: "Dayne Zorko",
      team: "Brisbane",
      position: "Midfielder",
      number: 5,
      age: 35,
      height: "1.78m",
      weight: "78kg",
      photo:
        "https://cdn.builder.io/api/v1/image/assets%2Faf9aef6647464a4bb798d09aa34aaa76%2F35a79c1a43bd4be1a3d3d6a95b0b1a79?format=webp&width=100",
      stats: {
        kicks: 31,
        handballs: 14,
        disposals: 45,
        marks: 9,
        tackles: 7,
        goals: 3,
        behinds: 2,
        efficiency: 89,
        contested: 20,
        uncontested: 25,
        clangers: 2,
        inside50s: 8,
        rebounds: 5,
        onePercenters: 1,
        turnovers: 3,
        intercepted: 1,
        goalAccuracy: 75,
        avgSpeed: 26.2,
        maxSpeed: 33.1,
        distance: 13.5,
      },
      form: [92, 85, 88, 94, 91, 89, 93, 87, 90, 95],
      heatMap: [
        { zone: "Forward 50", touches: 15, effectiveness: 88 },
        { zone: "Center Bounce", touches: 22, effectiveness: 90 },
        { zone: "Defensive 50", touches: 8, effectiveness: 85 },
      ],
      possessionData: [
        { time: 0, possession: 8 },
        { time: 5, possession: 12 },
        { time: 10, possession: 18 },
        { time: 15, possession: 20 },
        { time: 20, possession: 23 },
        { time: 25, possession: 26 },
        { time: 30, possession: 30 },
      ],
    },
    // Add more players with similar detailed data structure
    ...Array.from({ length: 16 }, (_, i) => ({
      id: i + 3,
      name: `Player ${i + 3}`,
      team: teams[i % teams.length],
      position: positions[i % positions.length],
      number: (i % 50) + 1,
      age: Math.floor(Math.random() * 15) + 20,
      height: `1.${Math.floor(Math.random() * 30) + 70}m`,
      weight: `${Math.floor(Math.random() * 30) + 75}kg`,
      photo:
        "https://cdn.builder.io/api/v1/image/assets%2Faf9aef6647464a4bb798d09aa34aaa76%2F35a79c1a43bd4be1a3d3d6a95b0b1a79?format=webp&width=100",
      stats: {
        kicks: Math.floor(Math.random() * 20) + 15,
        handballs: Math.floor(Math.random() * 15) + 5,
        disposals: Math.floor(Math.random() * 30) + 25,
        marks: Math.floor(Math.random() * 10) + 3,
        tackles: Math.floor(Math.random() * 8) + 2,
        goals: Math.floor(Math.random() * 5),
        behinds: Math.floor(Math.random() * 3),
        efficiency: Math.floor(Math.random() * 25) + 70,
        contested: Math.floor(Math.random() * 15) + 10,
        uncontested: Math.floor(Math.random() * 20) + 15,
        clangers: Math.floor(Math.random() * 5) + 1,
        inside50s: Math.floor(Math.random() * 8) + 2,
        rebounds: Math.floor(Math.random() * 6) + 1,
        onePercenters: Math.floor(Math.random() * 5) + 1,
        turnovers: Math.floor(Math.random() * 6) + 2,
        intercepted: Math.floor(Math.random() * 3) + 1,
        goalAccuracy: Math.floor(Math.random() * 40) + 60,
        avgSpeed: Math.random() * 10 + 20,
        maxSpeed: Math.random() * 10 + 28,
        distance: Math.random() * 5 + 10,
      },
      form: Array.from(
        { length: 10 },
        () => Math.floor(Math.random() * 25) + 75,
      ),
      heatMap: [
        {
          zone: "Forward 50",
          touches: Math.floor(Math.random() * 15) + 5,
          effectiveness: Math.floor(Math.random() * 20) + 75,
        },
        {
          zone: "Center Bounce",
          touches: Math.floor(Math.random() * 20) + 10,
          effectiveness: Math.floor(Math.random() * 20) + 75,
        },
        {
          zone: "Defensive 50",
          touches: Math.floor(Math.random() * 12) + 3,
          effectiveness: Math.floor(Math.random() * 20) + 75,
        },
      ],
      possessionData: Array.from({ length: 7 }, (_, j) => ({
        time: j * 5,
        possession: Math.floor(Math.random() * 20) + 5 + j * 2,
      })),
    })),
  ];

  return players;
};

export default function PlayerPerformance() {
  const [isLive, setIsLive] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const ENABLE_LIVE_FEATURES = true;

  const [players, setPlayers] = useState(generatePlayerData());
  const [selectedPlayer, setSelectedPlayer] = useState(players[0]);
  const [comparisonPlayer, setComparisonPlayer] = useState(players[1]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");
  const [selectedPosition, setSelectedPosition] = useState("all");
  const [chartType, setChartType] = useState<
    "possession" | "performance" | "comparison"
  >("possession");

  // Simulate live data updates
  useEffect(() => {
    if (!isLive || !isPlaying) return;

    const interval = setInterval(() => {
      setPlayers((prevPlayers) =>
        prevPlayers.map((player) => ({
          ...player,
          stats: {
            ...player.stats,
            disposals: player.stats.disposals + Math.floor(Math.random() * 2),
            efficiency: Math.max(
              60,
              Math.min(95, player.stats.efficiency + (Math.random() - 0.5) * 2),
            ),
          },
        })),
      );
    }, 3000);

    return () => clearInterval(interval);
  }, [isLive, isPlaying]);

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
  ];

  const playerMetrics = [
    { metric: "Goals", value: selectedPlayer.stats.goals, max: 5 },
    {
      metric: "Assists",
      value: Math.floor(selectedPlayer.stats.inside50s / 2),
      max: 4,
    },
    { metric: "Tackles", value: selectedPlayer.stats.tackles, max: 10 },
    { metric: "Marks", value: selectedPlayer.stats.marks, max: 12 },
    { metric: "Efficiency", value: selectedPlayer.stats.efficiency, max: 100 },
    {
      metric: "Speed",
      value: Math.round(selectedPlayer.stats.avgSpeed),
      max: 35,
    },
  ];

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

  const StatCard = ({
    title,
    value,
    subtitle,
    trend,
    color = "blue",
    icon: Icon,
  }: {
    title: string;
    value: string | number;
    subtitle?: string;
    trend?: "up" | "down" | "stable";
    color?: string;
    icon?: any;
  }) => (
    <Card className="relative overflow-hidden">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            {Icon && <Icon className={`w-4 h-4 text-${color}-600`} />}
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
        <div className={`text-2xl font-bold text-${color}-600 mb-1`}>
          {value}
        </div>
        {subtitle && <div className="text-xs text-gray-500">{subtitle}</div>}
        <div
          className={`absolute bottom-0 right-0 w-16 h-16 bg-${color}-100 rounded-full -mr-8 -mb-8 opacity-50`}
        />
      </CardContent>
    </Card>
  );

  const EnhancedPlayerCard = ({ player, isSelected, onClick }: any) => (
    <Card
      className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
        isSelected ? "ring-2 ring-blue-500 ring-offset-2" : ""
      }`}
      onClick={onClick}
    >
      <div
        className="h-24 rounded-t-lg relative"
        style={{ backgroundColor: getTeamColor(player.team) }}
      >
        <div className="absolute top-4 left-4 text-white">
          <div className="text-2xl font-bold">#{player.number}</div>
          <div className="text-sm">{player.team}</div>
        </div>
        <div className="absolute top-4 right-4 text-white text-right">
          <div className="text-xl font-bold">{player.stats.disposals}</div>
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
        </div>

        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="bg-blue-50 p-2 rounded">
            <div className="font-bold text-blue-600">{player.stats.goals}</div>
            <div className="text-gray-600">Goals</div>
          </div>
          <div className="bg-green-50 p-2 rounded">
            <div className="font-bold text-green-600">{player.stats.marks}</div>
            <div className="text-gray-600">Marks</div>
          </div>
          <div className="bg-purple-50 p-2 rounded">
            <div className="font-bold text-purple-600">
              {player.stats.efficiency}%
            </div>
            <div className="text-gray-600">Eff.</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      <MobileNavigation />

      {/* Main Content */}
      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-6">
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
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Live Clock */}
          {ENABLE_LIVE_FEATURES && (
            <LiveClock
              isLive={isLive}
              onToggleLive={setIsLive}
              matchTime={{ quarter: 2, timeRemaining: "15:23" }}
            />
          )}

          {/* Quick Stats Overview */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              title="Players Active"
              value={filteredPlayers.length}
              icon={Users}
              color="blue"
              trend="up"
            />
            <StatCard
              title="Total Goals"
              value={filteredPlayers.reduce((sum, p) => sum + p.stats.goals, 0)}
              icon={Target}
              color="green"
              trend="up"
            />
            <StatCard
              title="Avg Efficiency"
              value={`${Math.round(filteredPlayers.reduce((sum, p) => sum + p.stats.efficiency, 0) / filteredPlayers.length)}%`}
              icon={Activity}
              color="purple"
              trend="stable"
            />
            <StatCard
              title="Total Disposals"
              value={filteredPlayers.reduce(
                (sum, p) => sum + p.stats.disposals,
                0,
              )}
              icon={BarChart3}
              color="orange"
              trend="up"
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
                onClick={() => setSelectedPlayer(player)}
              />
            ))}
          </div>

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
                        {selectedPlayer.stats.goals}
                      </div>
                      <div className="text-xs text-gray-600">GOALS</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {selectedPlayer.stats.disposals}
                      </div>
                      <div className="text-xs text-gray-600">DISPOSALS</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>GOAL ACCURACY</span>
                      <span className="font-semibold">
                        {selectedPlayer.stats.goalAccuracy}%
                      </span>
                    </div>
                    <Progress
                      value={selectedPlayer.stats.goalAccuracy}
                      className="h-2"
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>EFFICIENCY</span>
                      <span className="font-semibold">
                        {selectedPlayer.stats.efficiency}%
                      </span>
                    </div>
                    <Progress
                      value={selectedPlayer.stats.efficiency}
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
                    {chartType === "possession" && (
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
                  value={selectedPlayer.stats.kicks}
                  color="blue"
                />
                <StatCard
                  title="Handballs"
                  value={selectedPlayer.stats.handballs}
                  color="green"
                />
                <StatCard
                  title="Marks"
                  value={selectedPlayer.stats.marks}
                  color="purple"
                />
                <StatCard
                  title="Tackles"
                  value={selectedPlayer.stats.tackles}
                  color="red"
                />
                <StatCard
                  title="Contested"
                  value={selectedPlayer.stats.contested}
                  color="orange"
                />
                <StatCard
                  title="Uncontested"
                  value={selectedPlayer.stats.uncontested}
                  color="yellow"
                />
                <StatCard
                  title="Inside 50s"
                  value={selectedPlayer.stats.inside50s}
                  color="pink"
                />
                <StatCard
                  title="Clangers"
                  value={selectedPlayer.stats.clangers}
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
                  <div className="grid grid-cols-10 gap-2 mb-4">
                    {selectedPlayer.form.map((score, index) => (
                      <div key={index} className="text-center">
                        <div
                          className={`p-2 rounded text-sm font-medium ${
                            score >= 90
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
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="heatmap" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Field Position Heat Map</CardTitle>
                </CardHeader>
                <CardContent>
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
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="compare" className="space-y-4">
              <PlayerComparison
                players={players}
                selectedPlayer1={selectedPlayer}
                selectedPlayer2={comparisonPlayer}
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
}
