import type { DashboardPlayersState } from "@/hooks/useDashboardPlayers";
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
import { Search, MapPin, Target } from "lucide-react";
import { formatStat } from "@/lib/players";
import MockPlayersBanner from "@/components/MockPlayersBanner";

export default function PlayerPerformanceTab({
  playersState,
}: {
  playersState: DashboardPlayersState;
}) {
  const {
    players,
    playersLoading,
    playersError,
    loadDatabasePlayers,
    selectedPlayer,
    setSelectedPlayer,
    comparisonPlayer,
    setComparisonPlayer,
    searchTerm,
    setSearchTerm,
    selectedTeam,
    setSelectedTeam,
    filteredPlayers,
    normalizedPlayerSearch,
    searchedFieldPlayers,
  } = playersState;

  return (
    <>
      <MockPlayersBanner />
      {playersLoading ? (
        <Card>
          <CardContent className="py-10 text-center text-gray-600">
            Loading players...
          </CardContent>
        </Card>
      ) : playersError ? (
        <Card>
          <CardContent className="py-10 text-center">
            <p className="text-red-600">{playersError}</p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => void loadDatabasePlayers()}
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      ) : players.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-gray-600">
            No players are currently available.
          </CardContent>
        </Card>
      ) : selectedPlayer && comparisonPlayer ? (
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Search and Filters */}
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
                <Input
                  placeholder="Search by name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Filter by Team</label>
                <Select value={selectedTeam} onValueChange={setSelectedTeam}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select team" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Teams</SelectItem>
                    {Array.from(
                      new Set(
                        players.map((player) => player.team).filter(Boolean),
                      ),
                    )
                      .sort()
                      .map((team) => (
                        <SelectItem key={team} value={team}>
                          {team}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3 max-h-60 overflow-y-auto">
                {filteredPlayers.map((player) => (
                  <div
                    key={player.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      selectedPlayer.id === player.id
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                    onClick={() => setSelectedPlayer(player)}
                  >
                    <div className="font-medium">{player.name}</div>
                    <div className="text-sm text-gray-600">
                      {player.team} ��� {player.position}
                    </div>
                    <div className="text-xs text-green-600 mt-1">
                      Efficiency: {formatStat(player.efficiency, "%")}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Player Statistics */}
          <div className="lg:w-2/3 space-y-6">
            {/* Live AFL Field Position */}
            <Card className="overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="h-5 w-5 text-green-600" />
                      Player Field Position
                    </CardTitle>
                    <CardDescription className="mt-1">
                      Search for a player to view their primary playing position
                      on the field.
                    </CardDescription>
                  </div>

                  {normalizedPlayerSearch &&
                    searchedFieldPlayers.length > 0 && (
                      <Badge
                        variant="outline"
                        className="w-fit border-green-200 bg-green-50 text-green-700"
                      >
                        {searchedFieldPlayers.length === 1
                          ? `Showing: ${searchedFieldPlayers[0].name}`
                          : `${searchedFieldPlayers.length} matching players`}
                      </Badge>
                    )}
                </div>
              </CardHeader>

              <CardContent>
                <div className="relative mx-auto aspect-[1.55/1] w-full max-w-4xl overflow-hidden rounded-[46%] border-[5px] border-green-800 bg-gradient-to-b from-green-500 via-green-600 to-green-700 shadow-inner">
                  {/* Alternating grass stripes */}
                  <div className="absolute inset-0 grid grid-cols-10 opacity-30">
                    {Array.from({ length: 10 }).map((_, index) => (
                      <div
                        key={index}
                        className={
                          index % 2 === 0 ? "bg-white/10" : "bg-black/5"
                        }
                      />
                    ))}
                  </div>

                  {/* Boundary line */}
                  <div className="absolute inset-[3%] rounded-[46%] border-2 border-white/90" />

                  {/* Centre square */}
                  <div className="absolute left-1/2 top-1/2 h-[31%] w-[26%] -translate-x-1/2 -translate-y-1/2 border-2 border-white/90" />

                  {/* Centre circle */}
                  <div className="absolute left-1/2 top-1/2 h-10 w-10 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white/90 sm:h-14 sm:w-14 lg:h-16 lg:w-16" />

                  {/* 50 metre arcs */}
                  <div className="absolute left-1/2 top-[4%] h-[32%] w-[58%] -translate-x-1/2 rounded-b-[50%] border-b-2 border-l-2 border-r-2 border-white/90" />
                  <div className="absolute bottom-[4%] left-1/2 h-[32%] w-[58%] -translate-x-1/2 rounded-t-[50%] border-l-2 border-r-2 border-t-2 border-white/90" />

                  {/* Goal squares */}
                  <div className="absolute left-1/2 top-[3%] h-[13%] w-[20%] -translate-x-1/2 border-2 border-t-0 border-white/90" />
                  <div className="absolute bottom-[3%] left-1/2 h-[13%] w-[20%] -translate-x-1/2 border-2 border-b-0 border-white/90" />

                  {/* Top goal posts */}
                  <div className="absolute left-1/2 top-0 flex -translate-x-1/2 gap-2 sm:gap-3">
                    <div className="h-5 w-0.5 bg-white sm:h-7 sm:w-1" />
                    <div className="h-7 w-0.5 bg-white sm:h-9 sm:w-1" />
                    <div className="h-7 w-0.5 bg-white sm:h-9 sm:w-1" />
                    <div className="h-5 w-0.5 bg-white sm:h-7 sm:w-1" />
                  </div>

                  {/* Bottom goal posts */}
                  <div className="absolute bottom-0 left-1/2 flex -translate-x-1/2 items-end gap-2 sm:gap-3">
                    <div className="h-5 w-0.5 bg-white sm:h-7 sm:w-1" />
                    <div className="h-7 w-0.5 bg-white sm:h-9 sm:w-1" />
                    <div className="h-7 w-0.5 bg-white sm:h-9 sm:w-1" />
                    <div className="h-5 w-0.5 bg-white sm:h-7 sm:w-1" />
                  </div>

                  {/* No search yet */}
                  {!normalizedPlayerSearch && (
                    <div className="pointer-events-none absolute inset-0 z-10 flex items-center justify-center px-4">
                      <div className="rounded-lg bg-black/55 px-4 py-2 text-center text-xs font-medium text-white shadow-lg backdrop-blur-sm sm:text-sm">
                        Search for a player to view their field position
                      </div>
                    </div>
                  )}

                  {/* Search did not match any player */}
                  {normalizedPlayerSearch &&
                    searchedFieldPlayers.length === 0 && (
                      <div className="pointer-events-none absolute inset-0 z-10 flex items-center justify-center px-4">
                        <div className="rounded-lg bg-black/55 px-4 py-2 text-center text-xs font-medium text-white shadow-lg backdrop-blur-sm sm:text-sm">
                          No matching player found
                        </div>
                      </div>
                    )}

                  {/* Only searched players are rendered on the field */}
                  {normalizedPlayerSearch &&
                    searchedFieldPlayers.map((player) => (
                      <div
                        key={player.id}
                        className="absolute z-20 -translate-x-1/2 -translate-y-1/2"
                        style={{
                          left: `${player.fieldX}%`,
                          top: `${player.fieldY}%`,
                        }}
                      >
                        {/* Animated outer glow */}
                        <div className="absolute left-1/2 top-1/2 h-14 w-14 -translate-x-1/2 -translate-y-1/2 animate-ping rounded-full bg-yellow-300/60 sm:h-16 sm:w-16" />

                        {/* Soft glow */}
                        <div className="absolute left-1/2 top-1/2 h-14 w-14 -translate-x-1/2 -translate-y-1/2 rounded-full bg-yellow-300/40 blur-md sm:h-16 sm:w-16" />

                        {/* Player marker */}
                        <button
                          type="button"
                          onClick={() => setSelectedPlayer(player)}
                          title={`${player.name} - ${player.team} - ${player.position}`}
                          className="relative flex h-9 w-9 scale-125 items-center justify-center rounded-full border-2 border-yellow-200 bg-yellow-400 text-xs font-bold text-gray-950 shadow-lg ring-4 ring-yellow-300/40 transition-all duration-300 hover:scale-[1.35] sm:h-10 sm:w-10 lg:h-11 lg:w-11"
                        >
                          {player.number}
                        </button>

                        {/* Player name */}
                        <div className="absolute left-1/2 top-full mt-2 -translate-x-1/2 whitespace-nowrap rounded-md bg-yellow-400 px-2 py-1 text-[10px] font-semibold text-gray-950 shadow-md sm:text-xs">
                          {player.name}
                        </div>
                      </div>
                    ))}
                </div>

                <div className="mt-4 flex flex-wrap items-center justify-center gap-4 text-xs sm:text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <span className="h-3 w-3 rounded-full bg-yellow-400" />
                    Searched Player
                  </div>

                  {normalizedPlayerSearch && (
                    <button
                      type="button"
                      onClick={() => setSearchTerm("")}
                      className="font-medium text-green-700 transition-colors hover:text-green-800 hover:underline"
                    >
                      Clear field highlight
                    </button>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Player Statistics - {selectedPlayer.name}</span>
                  <Badge variant="outline">{selectedPlayer.team}</Badge>
                </CardTitle>
                <CardDescription>{selectedPlayer.position}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {formatStat(selectedPlayer.kicks)}
                    </div>
                    <div className="text-sm text-gray-600">Kicks</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {formatStat(selectedPlayer.handballs)}
                    </div>
                    <div className="text-sm text-gray-600">Handballs</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {formatStat(selectedPlayer.marks)}
                    </div>
                    <div className="text-sm text-gray-600">Marks</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {formatStat(selectedPlayer.tackles)}
                    </div>
                    <div className="text-sm text-gray-600">Tackles</div>
                  </div>
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      {formatStat(selectedPlayer.goals)}
                    </div>
                    <div className="text-sm text-gray-600">Goals</div>
                  </div>
                  <div
                    className="text-center p-4 bg-yellow-50 rounded-lg cursor-pointer relative group"
                    title="Efficiency Rating"
                  >
                    <div className="text-2xl font-bold text-yellow-600">
                      {formatStat(selectedPlayer.efficiency, "%")}
                    </div>
                    <div className="text-sm text-gray-600">Efficiency</div>
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-10 w-48 bg-gray-800 text-white text-xs rounded-lg p-3 shadow-lg">
                      {selectedPlayer.efficiency === null ? (
                        // Without this, a missing value would fall through
                        // every check below and read "Needs Improvement".
                        <div>Efficiency hasn't been measured for this player yet.</div>
                      ) : (
                        <>
                          <div className="font-bold mb-1">
                            {selectedPlayer.efficiency >= 90
                              ? "🏆 Excellent"
                              : selectedPlayer.efficiency >= 80
                                ? "⭐ Good"
                                : selectedPlayer.efficiency >= 70
                                  ? "👍 Average"
                                  : "📈 Needs Improvement"}
                          </div>
                          <div>
                            {selectedPlayer.efficiency >= 90
                              ? "Elite level performance. Top 10% of all players."
                              : selectedPlayer.efficiency >= 80
                                ? "Strong performance. Above average player."
                                : selectedPlayer.efficiency >= 70
                                  ? "Solid performance. Room to improve."
                                  : "Below average. Focus on consistency."}
                          </div>
                          <div className="mt-1 text-yellow-300">
                            Score: {selectedPlayer.efficiency}/100
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Player Comparison */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Player Comparison
                </CardTitle>
                <CardDescription>
                  Compare {selectedPlayer.name} with another player
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <Select
                    value={comparisonPlayer.name}
                    onValueChange={(name) => {
                      const player = players.find((p) => p.name === name);
                      if (player) setComparisonPlayer(player);
                    }}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select player to compare" />
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
                  {(
                    ["kicks", "handballs", "marks", "tackles", "goals"] as const
                  ).map((stat) => {
                    const a = selectedPlayer[stat];
                    const b = comparisonPlayer[stat];
                    // Bars are scaled to the bigger value. A stat that wasn't
                    // measured shows "—" and an empty bar.
                    const max = Math.max(a ?? 0, b ?? 0, 1);

                    return (
                      <div key={stat} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="capitalize">{stat}</span>
                          <span>
                            {formatStat(a)} vs {formatStat(b)}
                          </span>
                        </div>
                        <div className="flex gap-2">
                          <div className="flex-1">
                            <Progress
                              value={((a ?? 0) / max) * 100}
                              className="h-2"
                            />
                            <div className="text-xs text-gray-600 mt-1">
                              {selectedPlayer.name}
                            </div>
                          </div>
                          <div className="flex-1">
                            <Progress
                              value={((b ?? 0) / max) * 100}
                              className="h-2"
                            />
                            <div className="text-xs text-gray-600 mt-1">
                              {comparisonPlayer.name}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      ) : null}
    </>
  );
}
