import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Flag } from "lucide-react";
import TeamCompareBar from "@/components/dashboard/TeamCompareBar";

export default function MatchesList() {
  // Mock matches data - this should come from the backend
  const matches = [
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
  ];

  if (!matches || matches.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No matches available</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {matches.map((m) => {
        const homePoints = m.stats.home.goals * 6 + m.stats.home.behinds;
        const awayPoints = m.stats.away.goals * 6 + m.stats.away.behinds;
        const winPct = Math.min(100, Math.max(0, Math.round((homePoints / (homePoints + awayPoints || 1)) * 100)));
        return (
          <Card key={m.id}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Flag className="w-4 h-4 text-purple-600" />
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
  );
}
