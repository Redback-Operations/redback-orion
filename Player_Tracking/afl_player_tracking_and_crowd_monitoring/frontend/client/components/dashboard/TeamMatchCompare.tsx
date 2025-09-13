import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Target } from "lucide-react";
import TeamCompareBar from "@/components/dashboard/TeamCompareBar";

export default function TeamMatchCompare({
  teamA,
  setTeamA,
  teamB,
  setTeamB,
  teamTeams,
  teamCompare,
}: {
  teamA: string;
  setTeamA: (v: string) => void;
  teamB: string;
  setTeamB: (v: string) => void;
  teamTeams: string[];
  teamCompare: { a: any; b: any; aEff: number; bEff: number };
}) {
  const ready = teamA !== "all" && teamB !== "all" && teamA !== teamB;
  return (
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
                {teamTeams.filter((t) => t !== "all").map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
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
                {teamTeams.filter((t) => t !== "all").map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center">
            <Badge variant="outline" className="w-full justify-center">
              {ready ? "Ready" : "Select two different teams"}
            </Badge>
          </div>
        </div>

        {ready && (
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
  );
}
