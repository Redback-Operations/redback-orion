import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search } from "lucide-react";

export default function PlayerSearchFilters({
  searchTerm,
  setSearchTerm,
  selectedTeam,
  setSelectedTeam,
  filteredPlayers,
  selectedPlayer,
  onSelectPlayer,
}: {
  searchTerm: string;
  setSearchTerm: (v: string) => void;
  selectedTeam: string;
  setSelectedTeam: (v: string) => void;
  filteredPlayers: any[];
  selectedPlayer: any;
  onSelectPlayer: (player: any) => void;
}) {
  return (
    <Card className="lg:w-1/3">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="w-5 h-5" />
          Player Search & Filters
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Search Players</label>
          <Input placeholder="Search by name..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full" />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">Filter by Team</label>
          <Select value={selectedTeam} onValueChange={setSelectedTeam}>
            <SelectTrigger>
              <SelectValue placeholder="Select team" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Teams</SelectItem>
              <SelectItem value="Western Bulldogs">Western Bulldogs</SelectItem>
              <SelectItem value="Richmond">Richmond</SelectItem>
              <SelectItem value="Geelong">Geelong</SelectItem>
              <SelectItem value="Melbourne">Melbourne</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-3 max-h-60 overflow-y-auto">
          {filteredPlayers.map((player) => (
            <div
              key={player.id}
              className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                selectedPlayer.id === player.id ? "border-blue-500 bg-purple-50" : "border-gray-200 hover:border-gray-300"
              }`}
              onClick={() => onSelectPlayer(player)}
            >
              <div className="font-medium">{player.name}</div>
              <div className="text-sm text-gray-600">{player.team} • {player.position}</div>
              <div className="text-xs text-orange-600 mt-1">Efficiency: {player.efficiency}%</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
