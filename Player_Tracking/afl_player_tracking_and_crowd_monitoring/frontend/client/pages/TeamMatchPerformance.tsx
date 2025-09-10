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
  const [team, setTeam] = useState("all");

  const rounds = useMemo(() => [
    "all",
    ...Array.from(new Set(demoMatches.map((m) => m.round))),
  ], []);

  const teams = useMemo(() => {
    const set = new Set<string>();
    demoMatches.forEach((m) => {
      set.add(m.teams.home);
      set.add(m.teams.away);
    });
    return ["all", ...Array.from(set).sort()];
  }, []);

  const filtered = useMemo(() => {
    return demoMatches.filter((m) => {
      const matchesRound = round === "all" || m.round === round;
      const matchesTeam = team === "all" || m.teams.home === team || m.teams.away === team;
      const hay = `${m.teams.home} ${m.teams.away} ${m.venue}`.toLowerCase();
      const q = search.trim().toLowerCase();
      return matchesRound && matchesTeam && (q === "" || hay.includes(q));
    });
  }, [round, team, search]);

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

  // Team comparison state
  const [teamA, setTeamA] = useState<string>("all");
  const [teamB, setTeamB] = useState<string>("all");

  const calcTeamTotals = (teamName: string) => {
    const base = { goals: 0, behinds: 0, disposals: 0, marks: 0, tackles: 0, clearances: 0, inside50: 0, efficiencySum: 0, efficiencyCount: 0 };
    if (!teamName || teamName === "all") return base;
    for (const m of demoMatches) {
      if (m.teams.home === teamName) {
        base.goals += m.stats.home.goals;
        base.behinds += m.stats.home.behinds;
        base.disposals += m.stats.home.disposals;
        base.marks += m.stats.home.marks;
        base.tackles += m.stats.home.tackles;
        base.clearances += m.stats.home.clearances;
        base.inside50 += m.stats.home.inside50;
        base.efficiencySum += m.stats.home.efficiency;
        base.efficiencyCount += 1;
      }
      if (m.teams.away === teamName) {
        base.goals += m.stats.away.goals;
        base.behinds += m.stats.away.behinds;
        base.disposals += m.stats.away.disposals;
        base.marks += m.stats.away.marks;
        base.tackles += m.stats.away.tackles;
        base.clearances += m.stats.away.clearances;
        base.inside50 += m.stats.away.inside50;
        base.efficiencySum += m.stats.away.efficiency;
        base.efficiencyCount += 1;
      }
    }
    return base;
  };

  const compare = useMemo(() => {
    const a = calcTeamTotals(teamA);
    const b = calcTeamTotals(teamB);
    const aEff = a.efficiencyCount ? Math.round(a.efficiencySum / a.efficiencyCount) : 0;
    const bEff = b.efficiencyCount ? Math.round(b.efficiencySum / b.efficiencyCount) : 0;
    return { a, b, aEff, bEff };
  }, [teamA, teamB]);

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
        <div className="px-4 py-3 grid grid-cols-1 sm:grid-cols-3 gap-3 items-stretch">
          <div className="sm:col-span-1">
            <Input
              placeholder="Search team, venue..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="sm:col-span-1">
            <Select value={team} onValueChange={setTeam}>
              <SelectTrigger>
                <SelectValue placeholder="Team" />
              </SelectTrigger>
              <SelectContent>
                {teams.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t === "all" ? "All Teams" : t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="sm:col-span-1">
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

      {/* Compare Teams */}
      <div className="p-4">
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
                    {teams.filter(t=>t!=="all").map((t) => (
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
                    {teams.filter(t=>t!=="all").map((t) => (
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
                <CompareBar label="Goals" aLabel={teamA} aValue={compare.a.goals} bLabel={teamB} bValue={compare.b.goals} />
                <CompareBar label="Disposals" aLabel={teamA} aValue={compare.a.disposals} bLabel={teamB} bValue={compare.b.disposals} />
                <CompareBar label="Marks" aLabel={teamA} aValue={compare.a.marks} bLabel={teamB} bValue={compare.b.marks} />
                <CompareBar label="Tackles" aLabel={teamA} aValue={compare.a.tackles} bLabel={teamB} bValue={compare.b.tackles} />
                <CompareBar label="Inside 50" aLabel={teamA} aValue={compare.a.inside50} bLabel={teamB} bValue={compare.b.inside50} />
                <CompareBar label="Avg Efficiency %" aLabel={teamA} aValue={compare.aEff} bLabel={teamB} bValue={compare.bEff} colorA="bg-indigo-500" colorB="bg-emerald-600" />
              </div>
            )}
          </CardContent>
        </Card>
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
