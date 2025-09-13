import React from "react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function TeamMatchFilters({
  teamSearch,
  setTeamSearch,
  teamFilter,
  setTeamFilter,
  teamRound,
  setTeamRound,
  teamRounds,
  teamTeams,
}: {
  teamSearch: string;
  setTeamSearch: (v: string) => void;
  teamFilter: string;
  setTeamFilter: (v: string) => void;
  teamRound: string;
  setTeamRound: (v: string) => void;
  teamRounds: string[];
  teamTeams: string[];
}) {
  return (
    <div className="bg-white border rounded-lg p-4">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-stretch">
        <div className="sm:col-span-1">
          <Input placeholder="Search team, venue..." value={teamSearch} onChange={(e) => setTeamSearch(e.target.value)} />
        </div>
        <div className="sm:col-span-1">
          <Select value={teamFilter} onValueChange={setTeamFilter}>
            <SelectTrigger>
              <SelectValue placeholder="Team" />
            </SelectTrigger>
            <SelectContent>
              {teamTeams.map((t) => (
                <SelectItem key={t} value={t}>
                  {t === "all" ? "All Teams" : t}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="sm:col-span-1">
          <Select value={teamRound} onValueChange={setTeamRound}>
            <SelectTrigger>
              <SelectValue placeholder="Round" />
            </SelectTrigger>
            <SelectContent>
              {teamRounds.map((r) => (
                <SelectItem key={r} value={r}>
                  {r === "all" ? "All Rounds" : r}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}
