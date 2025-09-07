import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import {
  Target,
  Zap,
  TrendingUp,
  TrendingDown,
  Award,
  Activity,
} from "lucide-react";

interface PlayerStats {
  disposals: number;
  kicks: number;
  handballs: number;
  marks: number;
  tackles: number;
  goals: number;
  behinds: number;
  efficiency: number;
  contested: number;
  uncontested: number;
  inside50s: number;
  goalAccuracy: number;
  avgSpeed: number;
  maxSpeed: number;
  distance: number;
  clangers: number;
  rebounds: number;
  onePercenters: number;
  turnovers: number;
  intercepted: number;
}

interface AFLPlayer {
  id: number;
  name: string;
  team: string;
  position: string;
  number: number;
  age: number;
  height: string;
  weight: string;
  photo?: string;
  stats: PlayerStats;
  form: number[];
  heatMap: Array<{
    zone: string;
    touches: number;
    effectiveness: number;
  }>;
}

interface AFLPlayerCardProps {
  player: AFLPlayer;
  isSelected?: boolean;
  onClick?: () => void;
  className?: string;
}

export default function AFLPlayerCard({
  player,
  isSelected = false,
  onClick,
  className,
}: AFLPlayerCardProps) {
  const [isFlipped, setIsFlipped] = useState(false);

  const handleCardClick = () => {
    setIsFlipped(!isFlipped);
    onClick?.();
  };

  const getTeamColor = (team: string) => {
    const teamColors: Record<string, string> = {
      "Western Bulldogs": "bg-blue-600",
      Richmond: "bg-yellow-500",
      Geelong: "bg-blue-800",
      Melbourne: "bg-red-600",
      Carlton: "bg-blue-500",
      Adelaide: "bg-red-500",
      "West Coast": "bg-blue-700",
      Collingwood: "bg-black",
      Essendon: "bg-red-700",
      Fremantle: "bg-purple-600",
    };
    return teamColors[team] || "bg-gray-600";
  };

  const getPositionIcon = (position: string) => {
    switch (position.toLowerCase()) {
      case "midfielder":
        return <Activity className="w-4 h-4" />;
      case "forward":
        return <Target className="w-4 h-4" />;
      case "defender":
        return <Award className="w-4 h-4" />;
      case "ruckman":
        return <Zap className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const recentForm = player.form?.slice(-3) || [80, 85, 90];
  const avgForm = recentForm.reduce((a, b) => a + b, 0) / recentForm.length;
  const formTrend = recentForm[recentForm.length - 1] > recentForm[0];

  return (
    <Card
      className={cn(
        "group cursor-pointer transition-all duration-300 hover:shadow-lg transform-gpu",
        "relative w-full h-64 [perspective:1000px]",
        isSelected && "ring-2 ring-blue-500 ring-offset-2",
        className,
      )}
      onClick={handleCardClick}
    >
      <div
        className={cn(
          "relative w-full h-full transition-transform duration-700 [transform-style:preserve-3d]",
          isFlipped && "[transform:rotateY(180deg)]",
        )}
      >
        {/* Front of card - Player Info */}
        <div className="absolute inset-0 [backface-visibility:hidden]">
          <CardContent className="p-0 h-full">
            {/* Header with team colors */}
            <div
              className={cn(
                "h-20 rounded-t-lg flex items-center justify-between px-4 text-white",
                getTeamColor(player.team),
              )}
            >
              <div className="flex items-center gap-2">
                <div className="text-3xl font-bold">#{player.number}</div>
                {getPositionIcon(player.position)}
              </div>
              <div className="text-right">
                <div className="text-sm font-medium">{player.team}</div>
                <div className="text-xs opacity-90">{player.position}</div>
              </div>
            </div>

            {/* Player Photo Area */}
            <div className="relative h-24 bg-gradient-to-b from-gray-100 to-gray-200 flex items-center justify-center">
              {player.photo ? (
                <img
                  src={player.photo}
                  alt={player.name}
                  className="w-20 h-20 rounded-full object-cover border-4 border-white shadow-lg"
                />
              ) : (
                <div className="w-20 h-20 rounded-full bg-gray-300 border-4 border-white shadow-lg flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-600">
                    {player.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </span>
                </div>
              )}
            </div>

            {/* Player Details */}
            <div className="p-4 space-y-3">
              <div className="text-center">
                <h3 className="font-bold text-lg leading-tight">
                  {player.name}
                </h3>
                <p className="text-sm text-gray-600">
                  {player.age}y • {player.height} • {player.weight}
                </p>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-blue-50 rounded-lg p-2">
                  <div className="text-lg font-bold text-blue-600">
                    {player.stats.goals}
                  </div>
                  <div className="text-xs text-gray-600">Goals</div>
                </div>
                <div className="bg-green-50 rounded-lg p-2">
                  <div className="text-lg font-bold text-green-600">
                    {player.stats.disposals}
                  </div>
                  <div className="text-xs text-gray-600">Disposals</div>
                </div>
                <div className="bg-purple-50 rounded-lg p-2">
                  <div className="text-lg font-bold text-purple-600">
                    {player.stats.efficiency}%
                  </div>
                  <div className="text-xs text-gray-600">Efficiency</div>
                </div>
              </div>

              {/* Form indicator */}
              <div className="flex items-center justify-center gap-2">
                <span className="text-xs text-gray-600">Form:</span>
                {formTrend ? (
                  <TrendingUp className="w-4 h-4 text-green-500" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500" />
                )}
                <Badge
                  variant={avgForm >= 85 ? "default" : "secondary"}
                  className="text-xs"
                >
                  {avgForm.toFixed(0)}
                </Badge>
              </div>
            </div>
          </CardContent>
        </div>

        {/* Back of card - Performance Metrics */}
        <div className="absolute inset-0 [backface-visibility:hidden] [transform:rotateY(180deg)]">
          <CardContent className="p-4 h-full">
            <div className="h-full flex flex-col">
              {/* Header */}
              <div className="text-center mb-4">
                <h3 className="font-bold text-lg">{player.name}</h3>
                <p className="text-sm text-gray-600">Performance Metrics</p>
              </div>

              {/* Performance Stats */}
              <div className="flex-1 space-y-3 overflow-y-auto">
                {/* Core Stats */}
                <div className="space-y-2">
                  <h4 className="font-medium text-sm text-gray-700">
                    Core Stats
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="font-semibold">{player.stats.kicks}</div>
                      <div className="text-gray-600">Kicks</div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="font-semibold">
                        {player.stats.handballs}
                      </div>
                      <div className="text-gray-600">Handballs</div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="font-semibold">{player.stats.marks}</div>
                      <div className="text-gray-600">Marks</div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="font-semibold">
                        {player.stats.tackles}
                      </div>
                      <div className="text-gray-600">Tackles</div>
                    </div>
                  </div>
                </div>

                {/* Efficiency Meters */}
                <div className="space-y-2">
                  <h4 className="font-medium text-sm text-gray-700">
                    Efficiency
                  </h4>
                  <div className="space-y-1.5">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span>Overall</span>
                        <span>{player.stats.efficiency}%</span>
                      </div>
                      <Progress
                        value={player.stats.efficiency}
                        className="h-1.5"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span>Goal Accuracy</span>
                        <span>{player.stats.goalAccuracy}%</span>
                      </div>
                      <Progress
                        value={player.stats.goalAccuracy}
                        className="h-1.5"
                      />
                    </div>
                  </div>
                </div>

                {/* Movement Stats */}
                <div className="space-y-2">
                  <h4 className="font-medium text-sm text-gray-700">
                    Movement
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-blue-50 p-2 rounded">
                      <div className="font-semibold">
                        {player.stats.avgSpeed}
                      </div>
                      <div className="text-gray-600">Avg Speed</div>
                    </div>
                    <div className="bg-red-50 p-2 rounded">
                      <div className="font-semibold">
                        {player.stats.maxSpeed}
                      </div>
                      <div className="text-gray-600">Max Speed</div>
                    </div>
                  </div>
                </div>

                {/* Recent Form */}
                <div className="space-y-2">
                  <h4 className="font-medium text-sm text-gray-700">
                    Recent Form
                  </h4>
                  <div className="grid grid-cols-3 gap-1">
                    {recentForm.map((score, index) => (
                      <div
                        key={index}
                        className={cn(
                          "text-center p-1.5 rounded text-xs font-medium",
                          score >= 90
                            ? "bg-green-100 text-green-700"
                            : score >= 80
                              ? "bg-yellow-100 text-yellow-700"
                              : "bg-red-100 text-red-700",
                        )}
                      >
                        {score}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Click hint */}
              <div className="text-center mt-2">
                <p className="text-xs text-gray-500">Click to flip back</p>
              </div>
            </div>
          </CardContent>
        </div>
      </div>
    </Card>
  );
}
