import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { BarChart3, Star, TrendingUp, Target, Users, Award, Activity } from "lucide-react";
import PlayerSearchFilters from "../PlayerSearchFilters";
import PlayerStatsGrid from "../PlayerStatsGrid";
import PlayerTradingCards from "../PlayerTradingCards";
import PlayerComparison from "../PlayerComparison";
import type { Player } from "@/hooks/useDashboardState";

interface PlayerPerformanceTabProps {
  selectedPlayer: Player;
  setSelectedPlayer: (player: Player) => void;
  comparisonPlayer: Player;
  setComparisonPlayer: (player: Player) => void;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  selectedTeam: string;
  setSelectedTeam: (team: string) => void;
  filteredPlayers: Player[];
  availableTeams: string[];
  performanceTrendData: any[];
  playerComparisonData: any[];
}

export default function PlayerPerformanceTab({
  selectedPlayer,
  setSelectedPlayer,
  comparisonPlayer,
  setComparisonPlayer,
  searchTerm,
  setSearchTerm,
  selectedTeam,
  setSelectedTeam,
  filteredPlayers,
  availableTeams,
  performanceTrendData,
  playerComparisonData,
}: PlayerPerformanceTabProps) {
  // Calculate player performance metrics
  const playerMetrics = {
    totalDisposals: selectedPlayer?.kicks + selectedPlayer?.handballs || 0,
    goalAccuracy: selectedPlayer?.efficiency || 0,
    performanceRating: selectedPlayer?.rating || 0,
    seasonGames: 15, // Mock data
    averageDisposals: Math.round((selectedPlayer?.kicks + selectedPlayer?.handballs || 0) * 0.9),
    teamRank: Math.floor(Math.random() * 5) + 1, // Mock ranking
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <BarChart3 className="w-6 h-6" />
            Player Performance
          </h2>
          <p className="text-gray-600">Real-time player statistics and performance insights</p>
        </div>
        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
          <TrendingUp className="w-3 h-3 mr-1" />
          Live Data
        </Badge>
      </div>

      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Disposals</p>
                <p className="text-2xl font-bold text-purple-600">{playerMetrics.totalDisposals}</p>
                <p className="text-xs text-gray-500">This Season</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <Target className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Goal Accuracy</p>
                <p className="text-2xl font-bold text-green-600">{playerMetrics.goalAccuracy}%</p>
                <p className="text-xs text-gray-500">Efficiency Rate</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <Award className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Performance Rating</p>
                <p className="text-2xl font-bold text-orange-600">{playerMetrics.performanceRating}</p>
                <p className="text-xs text-gray-500">Out of 5.0</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-full">
                <Star className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Team Ranking</p>
                <p className="text-2xl font-bold text-blue-600">#{playerMetrics.teamRank}</p>
                <p className="text-xs text-gray-500">In Team</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left Sidebar - Player Search & Filters */}
        <div className="col-span-3">
          <PlayerSearchFilters
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            selectedTeam={selectedTeam}
            setSelectedTeam={setSelectedTeam}
            filteredPlayers={filteredPlayers}
            selectedPlayer={selectedPlayer}
            onSelectPlayer={setSelectedPlayer}
            availableTeams={availableTeams}
          />
        </div>

        {/* Main Content Area */}
        <div className="col-span-9 space-y-6">
          {/* Player Statistics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Player Statistics - {selectedPlayer?.name || 'No Player Selected'}</span>
                <Badge variant="outline">{selectedPlayer?.team || 'Unknown'}</Badge>
              </CardTitle>
              <CardDescription>
                Current season performance metrics and trends
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PlayerStatsGrid selectedPlayer={selectedPlayer} performanceTrendData={performanceTrendData} />
            </CardContent>
          </Card>

          {/* Player Trading Cards */}
          <PlayerTradingCards 
            selectedPlayer={selectedPlayer}
            onPlayerSelect={setSelectedPlayer}
          />

          {/* Player Comparison */}
          <PlayerComparison
            selectedPlayer={selectedPlayer}
            comparisonPlayer={comparisonPlayer}
            setComparisonPlayer={setComparisonPlayer}
            mockPlayers={filteredPlayers}
            playerComparisonData={playerComparisonData}
          />
        </div>
      </div>
    </div>
  );
}
