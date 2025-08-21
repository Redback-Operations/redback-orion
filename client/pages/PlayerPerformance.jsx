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
import MobileNavigation from "@/components/MobileNavigation.jsx";
import LiveClock from "@/components/LiveClock.jsx";
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
  LineChart,
  PieChart,
} from "lucide-react";

// Detailed player data with realistic AFL statistics
const generatePlayerData = () => {
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
      },
      form: [85, 89, 91, 87, 93, 88, 87],
      heatMap: [
        { zone: "Forward 50", touches: 12, effectiveness: 85 },
        { zone: "Center Bounce", touches: 18, effectiveness: 92 },
        { zone: "Defensive 50", touches: 10, effectiveness: 78 },
      ],
    },
    {
      id: 2,
      name: "Dustin Martin",
      team: "Richmond",
      position: "Forward",
      number: 4,
      age: 32,
      height: "1.87m",
      weight: "92kg",
      stats: {
        kicks: 22,
        handballs: 8,
        disposals: 30,
        marks: 6,
        tackles: 4,
        goals: 3,
        behinds: 2,
        efficiency: 82,
        contested: 14,
        uncontested: 16,
        clangers: 2,
        inside50s: 5,
        rebounds: 1,
        onePercenters: 1,
        turnovers: 3,
        intercepted: 1,
        goalAccuracy: 60,
      },
      form: [78, 82, 85, 80, 88, 84, 82],
      heatMap: [
        { zone: "Forward 50", touches: 20, effectiveness: 88 },
        { zone: "Center Bounce", touches: 8, effectiveness: 75 },
        { zone: "Defensive 50", touches: 2, effectiveness: 50 },
      ],
    },
    {
      id: 3,
      name: "Patrick Dangerfield",
      team: "Geelong",
      position: "Midfielder",
      number: 35,
      age: 34,
      height: "1.89m",
      weight: "92kg",
      stats: {
        kicks: 25,
        handballs: 15,
        disposals: 40,
        marks: 7,
        tackles: 8,
        goals: 1,
        behinds: 0,
        efficiency: 84,
        contested: 22,
        uncontested: 18,
        clangers: 4,
        inside50s: 6,
        rebounds: 3,
        onePercenters: 3,
        turnovers: 5,
        intercepted: 2,
        goalAccuracy: 100,
      },
      form: [88, 84, 82, 86, 90, 85, 84],
      heatMap: [
        { zone: "Forward 50", touches: 8, effectiveness: 75 },
        { zone: "Center Bounce", touches: 24, effectiveness: 87 },
        { zone: "Defensive 50", touches: 8, effectiveness: 88 },
      ],
    },
    {
      id: 4,
      name: "Max Gawn",
      team: "Melbourne",
      position: "Ruckman",
      number: 11,
      age: 32,
      height: "2.08m",
      weight: "108kg",
      stats: {
        kicks: 18,
        handballs: 6,
        disposals: 24,
        marks: 10,
        tackles: 3,
        goals: 1,
        behinds: 0,
        efficiency: 78,
        contested: 16,
        uncontested: 8,
        clangers: 2,
        inside50s: 4,
        rebounds: 6,
        onePercenters: 8,
        turnovers: 3,
        intercepted: 1,
        goalAccuracy: 100,
      },
      form: [82, 78, 85, 83, 80, 79, 78],
      heatMap: [
        { zone: "Forward 50", touches: 6, effectiveness: 83 },
        { zone: "Center Bounce", touches: 14, effectiveness: 71 },
        { zone: "Defensive 50", touches: 4, effectiveness: 100 },
      ],
    },
  ];

  return players;
};

export default function PlayerPerformance() {
  const [isLive, setIsLive] = useState(true);
  const [players, setPlayers] = useState(generatePlayerData());
  const [selectedPlayer, setSelectedPlayer] = useState(players[0]);
  const [comparisonPlayer, setComparisonPlayer] = useState(players[1]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");
  const [selectedPosition, setSelectedPosition] = useState("all");

  // Simulate live data updates
  useEffect(() => {
    if (!isLive) return;

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
    }, 5000);

    return () => clearInterval(interval);
  }, [isLive]);

  const filteredPlayers = players.filter(
    (player) =>
      player.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedTeam === "all" || player.team === selectedTeam) &&
      (selectedPosition === "all" || player.position === selectedPosition),
  );

  const StatCard = ({ title, value, subtitle, trend, color = "blue" }) => (
    <div className={`p-4 rounded-lg bg-${color}-50 border border-${color}-100`}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium text-gray-600">{title}</span>
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
      <div className={`text-2xl font-bold text-${color}-600`}>{value}</div>
      {subtitle && <div className="text-xs text-gray-500 mt-1">{subtitle}</div>}
    </div>
  );

  const ComparisonChart = ({ stat, player1, player2 }) => {
    const val1 = player1.stats[stat] || 0;
    const val2 = player2.stats[stat] || 0;
    const max = Math.max(val1, val2);

    return (
      <div className="space-y-2">
        <div className="flex justify-between text-sm font-medium capitalize">
          <span>{stat.replace(/([A-Z])/g, " $1").trim()}</span>
          <span>
            {val1} vs {val2}
          </span>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs w-16 truncate">
              {player1.name.split(" ")[0]}
            </span>
            <div className="flex-1">
              <Progress value={(val1 / max) * 100} className="h-2" />
            </div>
            <span className="text-xs w-8">{val1}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs w-16 truncate">
              {player2.name.split(" ")[0]}
            </span>
            <div className="flex-1">
              <Progress
                value={(val2 / max) * 100}
                className="h-2 bg-orange-100"
              />
            </div>
            <span className="text-xs w-8">{val2}</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <MobileNavigation />

      {/* Main Content */}
      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-4">
          {/* Live Clock */}
          <LiveClock
            isLive={isLive}
            onToggleLive={setIsLive}
            matchTime={{ quarter: 2, timeRemaining: "15:23" }}
          />

          {/* Search and Filters */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Search className="w-5 h-5" />
                Player Search & Filters
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Input
                placeholder="Search by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Select value={selectedTeam} onValueChange={setSelectedTeam}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by team" />
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

          {/* Player Selection */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {filteredPlayers.slice(0, 8).map((player) => (
              <button
                key={player.id}
                onClick={() => setSelectedPlayer(player)}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  selectedPlayer.id === player.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 hover:border-gray-300 bg-white"
                }`}
              >
                <div className="font-medium text-sm truncate">
                  {player.name}
                </div>
                <div className="text-xs text-gray-600">{player.team}</div>
                <div className="text-xs text-green-600">#{player.number}</div>
              </button>
            ))}
          </div>

          {/* Player Details */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl">
                    {selectedPlayer.name}
                  </CardTitle>
                  <CardDescription className="flex items-center gap-4 text-sm">
                    <span>{selectedPlayer.team}</span>
                    <span>#{selectedPlayer.number}</span>
                    <span>{selectedPlayer.position}</span>
                    <Badge variant="outline">{selectedPlayer.age}y</Badge>
                  </CardDescription>
                </div>
                <div className="text-right text-sm text-gray-600">
                  <div>{selectedPlayer.height}</div>
                  <div>{selectedPlayer.weight}</div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="stats" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="stats">Stats</TabsTrigger>
                  <TabsTrigger value="form">Form</TabsTrigger>
                  <TabsTrigger value="heatmap">Heat Map</TabsTrigger>
                  <TabsTrigger value="compare">Compare</TabsTrigger>
                </TabsList>

                <TabsContent value="stats" className="space-y-4">
                  {/* Core Stats */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <StatCard
                      title="Disposals"
                      value={selectedPlayer.stats.disposals}
                      color="blue"
                      trend="up"
                    />
                    <StatCard
                      title="Kicks"
                      value={selectedPlayer.stats.kicks}
                      color="green"
                    />
                    <StatCard
                      title="Handballs"
                      value={selectedPlayer.stats.handballs}
                      color="purple"
                    />
                    <StatCard
                      title="Marks"
                      value={selectedPlayer.stats.marks}
                      color="orange"
                    />
                    <StatCard
                      title="Tackles"
                      value={selectedPlayer.stats.tackles}
                      color="red"
                    />
                    <StatCard
                      title="Goals"
                      value={selectedPlayer.stats.goals}
                      color="yellow"
                    />
                  </div>

                  {/* Advanced Stats */}
                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-900">
                      Advanced Metrics
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Efficiency</span>
                          <span className="font-medium">
                            {selectedPlayer.stats.efficiency}%
                          </span>
                        </div>
                        <Progress
                          value={selectedPlayer.stats.efficiency}
                          className="h-2"
                        />
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Goal Accuracy</span>
                          <span className="font-medium">
                            {selectedPlayer.stats.goalAccuracy}%
                          </span>
                        </div>
                        <Progress
                          value={selectedPlayer.stats.goalAccuracy}
                          className="h-2"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                      <div className="p-2 bg-gray-50 rounded">
                        <div className="text-lg font-semibold">
                          {selectedPlayer.stats.contested}
                        </div>
                        <div className="text-xs text-gray-600">Contested</div>
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        <div className="text-lg font-semibold">
                          {selectedPlayer.stats.uncontested}
                        </div>
                        <div className="text-xs text-gray-600">Uncontested</div>
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        <div className="text-lg font-semibold">
                          {selectedPlayer.stats.inside50s}
                        </div>
                        <div className="text-xs text-gray-600">Inside 50s</div>
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        <div className="text-lg font-semibold">
                          {selectedPlayer.stats.clangers}
                        </div>
                        <div className="text-xs text-gray-600">Clangers</div>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="form" className="space-y-4">
                  <div className="space-y-3">
                    <h4 className="font-medium">Recent Form (Last 7 Games)</h4>
                    <div className="grid grid-cols-7 gap-1">
                      {selectedPlayer.form.map((score, index) => (
                        <div key={index} className="text-center">
                          <div
                            className={`p-2 rounded text-xs font-medium ${
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
                            R{7 - index}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="text-sm text-gray-600">
                      Average:{" "}
                      {(
                        selectedPlayer.form.reduce((a, b) => a + b, 0) /
                        selectedPlayer.form.length
                      ).toFixed(1)}
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="heatmap" className="space-y-4">
                  <div className="space-y-3">
                    <h4 className="font-medium">Field Position Heat Map</h4>
                    {selectedPlayer.heatMap.map((zone, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>{zone.zone}</span>
                          <span>
                            {zone.touches} touches • {zone.effectiveness}%
                            effective
                          </span>
                        </div>
                        <div className="flex gap-2">
                          <div className="flex-1">
                            <Progress
                              value={(zone.touches / 30) * 100}
                              className="h-3"
                            />
                            <div className="text-xs text-gray-500 mt-1">
                              Touches
                            </div>
                          </div>
                          <div className="flex-1">
                            <Progress
                              value={zone.effectiveness}
                              className="h-3"
                            />
                            <div className="text-xs text-gray-500 mt-1">
                              Effectiveness
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="compare" className="space-y-4">
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium">
                        Compare with:
                      </label>
                      <Select
                        value={comparisonPlayer.name}
                        onValueChange={(name) => {
                          const player = players.find((p) => p.name === name);
                          if (player) setComparisonPlayer(player);
                        }}
                      >
                        <SelectTrigger className="w-full mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {players
                            .filter((p) => p.id !== selectedPlayer.id)
                            .map((player) => (
                              <SelectItem key={player.id} value={player.name}>
                                {player.name} ({player.team})
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-4">
                      {[
                        "disposals",
                        "kicks",
                        "handballs",
                        "marks",
                        "tackles",
                        "goals",
                        "efficiency",
                      ].map((stat) => (
                        <ComparisonChart
                          key={stat}
                          stat={stat}
                          player1={selectedPlayer}
                          player2={comparisonPlayer}
                        />
                      ))}
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
