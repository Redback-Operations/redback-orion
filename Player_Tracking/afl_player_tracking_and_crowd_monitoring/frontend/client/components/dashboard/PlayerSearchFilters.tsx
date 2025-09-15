import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Search, Users, Target } from "lucide-react";

export default function PlayerSearchFilters({
  searchTerm,
  setSearchTerm,
  selectedTeam,
  setSelectedTeam,
  filteredPlayers,
  selectedPlayer,
  onSelectPlayer,
  availableTeams,
}: {
  searchTerm: string;
  setSearchTerm: (v: string) => void;
  selectedTeam: string;
  setSelectedTeam: (v: string) => void;
  filteredPlayers: any[];
  selectedPlayer: any;
  onSelectPlayer: (player: any) => void;
  availableTeams: string[];
}) {
  return (
    <Card className="h-fit">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Users className="w-5 h-5 text-purple-600" />
          Player Search
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input 
            placeholder="Search players..." 
            value={searchTerm} 
            onChange={(e) => setSearchTerm(e.target.value)} 
            className="pl-10 h-10" 
          />
        </div>

        {/* Team Filter */}
        <Select value={selectedTeam} onValueChange={setSelectedTeam}>
          <SelectTrigger className="h-10">
            <SelectValue placeholder="All teams" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Teams</SelectItem>
            {availableTeams && availableTeams.map((team) => (
              <SelectItem key={team} value={team}>
                {team}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Player List */}
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {filteredPlayers && filteredPlayers.length > 0 ? (
            filteredPlayers.map((player) => (
              <div
                key={player.id}
                className={`p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                  selectedPlayer && selectedPlayer.id === player.id 
                    ? "bg-purple-50 border-2 border-purple-200 shadow-sm" 
                    : "bg-gray-50 hover:bg-gray-100 border border-transparent hover:border-gray-200"
                }`}
                onClick={() => onSelectPlayer(player)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-gray-900 truncate">{player.name}</div>
                    <div className="text-sm text-gray-600 truncate">{player.team}</div>
                  </div>
                  <div className="flex items-center gap-2 ml-2">
                    <Badge variant="secondary" className="text-xs">
                      {player.position}
                    </Badge>
                    <div className="flex items-center gap-1 text-xs text-orange-600">
                      <Target className="w-3 h-3" />
                      {player.efficiency}%
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <Users className="w-8 h-8 text-gray-300 mx-auto mb-2" />
              <p className="text-gray-500 text-sm">No players found</p>
              <p className="text-gray-400 text-xs mt-1">Try adjusting your search or filters</p>
            </div>
          )}
        </div>

        {/* Results Count */}
        {filteredPlayers && filteredPlayers.length > 0 && (
          <div className="text-xs text-gray-500 text-center pt-2 border-t">
            {filteredPlayers.length} player{filteredPlayers.length !== 1 ? 's' : ''} found
          </div>
        )}
      </CardContent>
    </Card>
  );
}
