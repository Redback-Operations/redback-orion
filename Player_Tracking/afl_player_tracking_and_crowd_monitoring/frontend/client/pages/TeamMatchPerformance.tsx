import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import {
  Activity,
  Users,
  ArrowRight,
  BarChart3,
  Flag,
  Target,
  TrendingUp,
} from "lucide-react";

// Sample team match data (static for demo)
const demoMatches = [
  {
    id: 1,
    round: "Round 12",
    venue: "MCG",
    date: "2025-07-02",
    teams: {
      home: "Western Bulldogs",
      away: "Richmond",
    },
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
    teams: {
      home: "Geelong",
      away: "Collingwood",
    },
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
    teams: {
      home: "Adelaide",
      away: "Port Adelaide",
    },
    stats: {
      home: { goals: 11, behinds: 13, disposals: 372, marks: 81, tackles: 64, clearances: 37, inside50: 58, efficiency: 73 },
      away: { goals: 12, behinds: 10, disposals: 365, marks: 75, tackles: 59, clearances: 35, inside50: 54, efficiency: 75 },
    },
  },
];

export default function TeamMatchPerformance() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [round, setRound] = useState("all");

  const rounds = useMemo(() => [
    "all",
    ...Array.from(new Set(demoMatches.map((m) => m.round))),
  ], []);

  const filtered = useMemo(() => {
    return demoMatches.filter((m) => {
      const matchesRound = round === "all" || m.round === round;
      const hay = `${m.teams.home} ${m.teams.away} ${m.venue}`.toLowerCase();
      const q = search.trim().toLowerCase();
      return matchesRound && (q === "" || hay.includes(q));
    });
  }, [round, search]);

  const totalSummary = useMemo(() => {
    const base = {
      games: 0,
      goals: 0,
      behinds: 0,
      disposals: 0,
      marks: 0,
      tackles: 0,
      clearances: 0,
      inside50: 0,
    };
    return filtered.reduce((acc, m) => {
      acc.games += 1;
      acc.goals += m.stats.home.goals + m.stats.away.goals;
      acc.behinds += m.stats.home.behinds + m.stats.away.behinds;
      acc.disposals += m.stats.home.disposals + m.stats.away.disposals;
      acc.marks += m.stats.home.marks + m.stats.away.marks;
      acc.tackles += m.stats.home.tackles + m.stats.away.tackles;
      acc.clearances += m.stats.home.clearances + m.stats.away.clearances;
      acc.inside50 += m.stats.home.inside50 + m.stats.away.inside50;
      return acc;
    }, base);
  }, [filtered]);

  const Metric = ({ label, value, suffix = "" }: { label: string; value: number; suffix?: string }) => (
    <div className="p-4 rounded-lg bg-white border">
      <div className="text-sm text-gray-600">{label}</div>
      <div className="text-2xl font-semibold">{value.toLocaleString()}{suffix}</div>
    </div>
  );

  const CompareBar = ({
    label,
    aLabel,
    aValue,
    bLabel,
    bValue,
    colorA = "bg-blue-500",
    colorB = "bg-green-600",
  }: {
    label: string;
    aLabel: string;
    aValue: number;
    bLabel: string;
    bValue: number;
    colorA?: string;
    colorB?: string;
  }) => {
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
              <div className={`${colorA} h-3 rounded-full`} style={{ width: `${aPct}%` }} />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-28 text-xs text-green-700 truncate">{bLabel}</span>
            <div className="flex-1 bg-gray-200 rounded-full h-3">
              <div className={`${colorB} h-3 rounded-full`} style={{ width: `${bPct}%` }} />
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">AFL Analytics</h1>
              <p className="text-sm text-gray-600">Team match performance overview</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="hidden sm:flex">Updated now</Badge>
            <Button onClick={() => navigate("/player-performance")} className="bg-gradient-to-r from-green-600 to-blue-600">
              <BarChart3 className="w-4 h-4 mr-2" />
              Player Performance
            </Button>
          </div>
        </div>
      </header>

      {/* Filters */}
      <div className="bg-white border-b">
        <div className="px-4 py-3 flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
          <div className="flex-1">
            <Input
              placeholder="Search team, venue..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-60">
            <Select value={round} onValueChange={setRound}>
              <SelectTrigger>
                <SelectValue placeholder="Round" />
              </SelectTrigger>
              <SelectContent>
                {rounds.map((r) => (
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
      <div className="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Metric label="Matches" value={totalSummary.games} />
        <Metric label="Total Goals" value={totalSummary.goals} />
        <Metric label="Total Disposals" value={totalSummary.disposals} />
        <Metric label="Inside 50s" value={totalSummary.inside50} />
      </div>

      {/* Matches list */}
      <div className="p-4 grid grid-cols-1 gap-4">
        {filtered.map((m) => {
          const homePoints = m.stats.home.goals * 6 + m.stats.home.behinds;
          const awayPoints = m.stats.away.goals * 6 + m.stats.away.behinds;
          const homeWin = homePoints >= awayPoints;
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
                {/* Score */}
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

                {/* Key metric comparisons */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <CompareBar
                    label="Disposals"
                    aLabel={m.teams.home}
                    aValue={m.stats.home.disposals}
                    bLabel={m.teams.away}
                    bValue={m.stats.away.disposals}
                  />
                  <CompareBar
                    label="Marks"
                    aLabel={m.teams.home}
                    aValue={m.stats.home.marks}
                    bLabel={m.teams.away}
                    bValue={m.stats.away.marks}
                  />
                  <CompareBar
                    label="Tackles"
                    aLabel={m.teams.home}
                    aValue={m.stats.home.tackles}
                    bLabel={m.teams.away}
                    bValue={m.stats.away.tackles}
                  />
                  <CompareBar
                    label="Clearances"
                    aLabel={m.teams.home}
                    aValue={m.stats.home.clearances}
                    bLabel={m.teams.away}
                    bValue={m.stats.away.clearances}
                  />
                  <CompareBar
                    label="Inside 50"
                    aLabel={m.teams.home}
                    aValue={m.stats.home.inside50}
                    bLabel={m.teams.away}
                    bValue={m.stats.away.inside50}
                  />
                  <CompareBar
                    label="Efficiency %"
                    aLabel={m.teams.home}
                    aValue={m.stats.home.efficiency}
                    bLabel={m.teams.away}
                    bValue={m.stats.away.efficiency}
                    colorA="bg-indigo-500"
                    colorB="bg-emerald-600"
                  />
                </div>

                {/* Quick action */}
                <div className="flex items-center justify-end">
                  <Button variant="outline" onClick={() => navigate("/player-performance")}> 
                    <Users className="w-4 h-4 mr-2" />
                    View Player Performance
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
