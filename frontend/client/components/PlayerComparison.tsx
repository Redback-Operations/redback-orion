import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
} from "recharts";
import { cn } from "@/lib/utils";
import { ArrowLeftRight, BarChart3, TrendingUp, Award } from "lucide-react";

import { formatStat, type Player, type Stat } from "@/lib/players";

/** value as a percentage of max, or null if it wasn't measured. */
const percentOf = (value: Stat, max: number): Stat =>
  value === null ? null : Math.round((value / max) * 100);

/** A chart row can only compare two players if both were measured. */
const bothMeasured = (row: { player1: Stat; player2: Stat }) =>
  row.player1 !== null && row.player2 !== null;

interface PlayerComparisonProps {
  players: Player[];
  selectedPlayer1?: Player;
  selectedPlayer2?: Player;
  onPlayerSelect?: (player: Player, position: 1 | 2) => void;
}

export default function PlayerComparison({
  players,
  selectedPlayer1,
  selectedPlayer2,
  onPlayerSelect,
}: PlayerComparisonProps) {
  const [comparisonType, setComparisonType] = useState<
    "radar" | "bar" | "form"
  >("radar");

  const player1 = selectedPlayer1 || players[0];
  const player2 = selectedPlayer2 || players[1];

  // Prepare radar chart data
  const radarData = [
    {
      stat: "Goals",
      player1: player1.stats.goals,
      player2: player2.stats.goals,
      maxValue: Math.max(player1.stats.goals ?? 0, player2.stats.goals ?? 0, 5),
    },
    {
      stat: "Disposals",
      player1: percentOf(player1.stats.disposals, 50),
      player2: percentOf(player2.stats.disposals, 50),
      maxValue: 100,
    },
    {
      stat: "Marks",
      player1: percentOf(player1.stats.marks, 15),
      player2: percentOf(player2.stats.marks, 15),
      maxValue: 100,
    },
    {
      stat: "Tackles",
      player1: percentOf(player1.stats.tackles, 15),
      player2: percentOf(player2.stats.tackles, 15),
      maxValue: 100,
    },
    {
      stat: "Efficiency",
      player1: player1.stats.efficiency,
      player2: player2.stats.efficiency,
      maxValue: 100,
    },
    {
      stat: "Speed",
      player1: percentOf(player1.stats.avgSpeed, 35),
      player2: percentOf(player2.stats.avgSpeed, 35),
      maxValue: 100,
    },
  ].filter(bothMeasured);

  // Prepare bar chart data
  const barData = [
    {
      stat: "Goals",
      player1: player1.stats.goals,
      player2: player2.stats.goals,
    },
    {
      stat: "Disposals",
      player1: player1.stats.disposals,
      player2: player2.stats.disposals,
    },
    {
      stat: "Marks",
      player1: player1.stats.marks,
      player2: player2.stats.marks,
    },
    {
      stat: "Tackles",
      player1: player1.stats.tackles,
      player2: player2.stats.tackles,
    },
    {
      stat: "Kicks",
      player1: player1.stats.kicks,
      player2: player2.stats.kicks,
    },
    {
      stat: "Handballs",
      player1: player1.stats.handballs,
      player2: player2.stats.handballs,
    },
  ].filter(bothMeasured);

  // Prepare form comparison data
  const formData = Array.from(
    { length: Math.max(player1.form.length, player2.form.length) },
    (_, i) => ({
      game: `Game ${i + 1}`,
      // null leaves a gap in the line where a player has no score for that game.
      player1: player1.form[i] ?? null,
      player2: player2.form[i] ?? null,
    }),
  );

  const getTeamColor = (team: string) => {
    const teamColors: Record<string, string> = {
      "Western Bulldogs": "#1E40AF",
      Richmond: "#EAB308",
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

  const swapPlayers = () => {
    if (onPlayerSelect) {
      onPlayerSelect(player2, 1);
      onPlayerSelect(player1, 2);
    }
  };

  const StatComparison = ({
    label,
    value1,
    value2,
    unit = "",
  }: {
    label: string;
    value1: Stat;
    value2: Stat;
    unit?: string;
  }) => {
    // Only pick a winner when both players were measured.
    const comparable = value1 !== null && value2 !== null;
    // `|| 1` stops a divide-by-zero when both values are 0.
    const max = Math.max(value1 ?? 0, value2 ?? 0) || 1;
    const winner1 = comparable && value1 > value2;
    const winner2 = comparable && value2 > value1;
    const tie = comparable && value1 === value2;

    return (
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium">{label}</span>
          <div className="flex items-center gap-2">
            <span
              className={cn("text-sm", winner1 && "font-bold text-green-600")}
            >
              {formatStat(value1, unit)}
            </span>
            <span className="text-gray-400">vs</span>
            <span
              className={cn("text-sm", winner2 && "font-bold text-green-600")}
            >
              {formatStat(value2, unit)}
            </span>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-1">
          <div className="h-2 bg-blue-200 rounded-l">
            <div
              className="h-full bg-blue-500 rounded-l transition-all"
              style={{ width: `${((value1 ?? 0) / max) * 100}%` }}
            />
          </div>
          <div className="h-2 bg-red-200 rounded-r">
            <div
              className="h-full bg-red-500 rounded-r transition-all ml-auto"
              style={{ width: `${((value2 ?? 0) / max) * 100}%` }}
            />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Player Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ArrowLeftRight className="w-5 h-5" />
            Player Comparison
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Player 1 Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Player 1</label>
              <Select
                value={player1.name}
                onValueChange={(name) => {
                  const player = players.find((p) => p.name === name);
                  if (player && onPlayerSelect) {
                    onPlayerSelect(player, 1);
                  }
                }}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {players.map((player) => (
                    <SelectItem key={player.id} value={player.name}>
                      {player.name} ({player.team})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Player 2 Selection */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Player 2</label>
              <Select
                value={player2.name}
                onValueChange={(name) => {
                  const player = players.find((p) => p.name === name);
                  if (player && onPlayerSelect) {
                    onPlayerSelect(player, 2);
                  }
                }}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {players.map((player) => (
                    <SelectItem key={player.id} value={player.name}>
                      {player.name} ({player.team})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center justify-center">
            <Button
              variant="outline"
              size="sm"
              onClick={swapPlayers}
              className="flex items-center gap-2"
            >
              <ArrowLeftRight className="w-4 h-4" />
              Swap Players
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Player Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Player 1 Card */}
        <Card
          className="border-2"
          style={{ borderColor: getTeamColor(player1.team) }}
        >
          <CardHeader className="text-center pb-2">
            <div className="flex items-center justify-center gap-2">
              <div
                className="w-8 h-8 rounded-full text-white flex items-center justify-center text-sm font-bold"
                style={{ backgroundColor: getTeamColor(player1.team) }}
              >
                #{player1.number}
              </div>
              <div>
                <CardTitle className="text-lg">{player1.name}</CardTitle>
                <p className="text-sm text-gray-600">
                  {player1.team} • {player1.position}
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-blue-50 p-2 rounded">
                <div className="text-lg font-bold text-blue-600">
                  {formatStat(player1.stats.goals)}
                </div>
                <div className="text-xs text-gray-600">Goals</div>
              </div>
              <div className="bg-green-50 p-2 rounded">
                <div className="text-lg font-bold text-green-600">
                  {formatStat(player1.stats.disposals)}
                </div>
                <div className="text-xs text-gray-600">Disposals</div>
              </div>
              <div className="bg-purple-50 p-2 rounded">
                <div className="text-lg font-bold text-purple-600">
                  {formatStat(player1.stats.efficiency, "%")}
                </div>
                <div className="text-xs text-gray-600">Efficiency</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Player 2 Card */}
        <Card
          className="border-2"
          style={{ borderColor: getTeamColor(player2.team) }}
        >
          <CardHeader className="text-center pb-2">
            <div className="flex items-center justify-center gap-2">
              <div
                className="w-8 h-8 rounded-full text-white flex items-center justify-center text-sm font-bold"
                style={{ backgroundColor: getTeamColor(player2.team) }}
              >
                #{player2.number}
              </div>
              <div>
                <CardTitle className="text-lg">{player2.name}</CardTitle>
                <p className="text-sm text-gray-600">
                  {player2.team} • {player2.position}
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-blue-50 p-2 rounded">
                <div className="text-lg font-bold text-blue-600">
                  {formatStat(player2.stats.goals)}
                </div>
                <div className="text-xs text-gray-600">Goals</div>
              </div>
              <div className="bg-green-50 p-2 rounded">
                <div className="text-lg font-bold text-green-600">
                  {formatStat(player2.stats.disposals)}
                </div>
                <div className="text-xs text-gray-600">Disposals</div>
              </div>
              <div className="bg-purple-50 p-2 rounded">
                <div className="text-lg font-bold text-purple-600">
                  {formatStat(player2.stats.efficiency, "%")}
                </div>
                <div className="text-xs text-gray-600">Efficiency</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Comparison Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Performance Comparison
            </CardTitle>
            <div className="flex gap-2">
              <Button
                variant={comparisonType === "radar" ? "default" : "outline"}
                size="sm"
                onClick={() => setComparisonType("radar")}
              >
                Radar
              </Button>
              <Button
                variant={comparisonType === "bar" ? "default" : "outline"}
                size="sm"
                onClick={() => setComparisonType("bar")}
              >
                Bar
              </Button>
              <Button
                variant={comparisonType === "form" ? "default" : "outline"}
                size="sm"
                onClick={() => setComparisonType("form")}
              >
                Form
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            {comparisonType === "radar" && (
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="stat" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} tickCount={6} />
                  <Radar
                    name={player1.name}
                    dataKey="player1"
                    stroke={getTeamColor(player1.team)}
                    fill={getTeamColor(player1.team)}
                    fillOpacity={0.2}
                  />
                  <Radar
                    name={player2.name}
                    dataKey="player2"
                    stroke={getTeamColor(player2.team)}
                    fill={getTeamColor(player2.team)}
                    fillOpacity={0.2}
                  />
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            )}

            {comparisonType === "bar" && (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="stat" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar
                    dataKey="player1"
                    fill={getTeamColor(player1.team)}
                    name={player1.name}
                  />
                  <Bar
                    dataKey="player2"
                    fill={getTeamColor(player2.team)}
                    name={player2.name}
                  />
                </BarChart>
              </ResponsiveContainer>
            )}

            {comparisonType === "form" && (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="game" />
                  <YAxis domain={[60, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="player1"
                    stroke={getTeamColor(player1.team)}
                    strokeWidth={2}
                    name={player1.name}
                  />
                  <Line
                    type="monotone"
                    dataKey="player2"
                    stroke={getTeamColor(player2.team)}
                    strokeWidth={2}
                    name={player2.name}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Stat Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="w-5 h-5" />
            Detailed Statistics
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <StatComparison
            label="Disposals"
            value1={player1.stats.disposals}
            value2={player2.stats.disposals}
          />
          <StatComparison
            label="Kicks"
            value1={player1.stats.kicks}
            value2={player2.stats.kicks}
          />
          <StatComparison
            label="Handballs"
            value1={player1.stats.handballs}
            value2={player2.stats.handballs}
          />
          <StatComparison
            label="Marks"
            value1={player1.stats.marks}
            value2={player2.stats.marks}
          />
          <StatComparison
            label="Tackles"
            value1={player1.stats.tackles}
            value2={player2.stats.tackles}
          />
          <StatComparison
            label="Goals"
            value1={player1.stats.goals}
            value2={player2.stats.goals}
          />
          <StatComparison
            label="Efficiency"
            value1={player1.stats.efficiency}
            value2={player2.stats.efficiency}
            unit="%"
          />
          <StatComparison
            label="Goal Accuracy"
            value1={player1.stats.goalAccuracy}
            value2={player2.stats.goalAccuracy}
            unit="%"
          />
          <StatComparison
            label="Average Speed"
            value1={player1.stats.avgSpeed}
            value2={player2.stats.avgSpeed}
            unit=" km/h"
          />
          <StatComparison
            label="Max Speed"
            value1={player1.stats.maxSpeed}
            value2={player2.stats.maxSpeed}
            unit=" km/h"
          />
        </CardContent>
      </Card>
    </div>
  );
}
