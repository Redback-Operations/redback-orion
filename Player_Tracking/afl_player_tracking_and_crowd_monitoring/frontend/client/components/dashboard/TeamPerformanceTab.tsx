import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp, TrendingDown, Users, Target, Calendar, MapPin } from "lucide-react";
import TeamMatchFilters from "./TeamMatchFilters";
import TeamMatchCompare from "./TeamMatchCompare";
import TeamSummaryCards from "./TeamSummaryCards";
import MatchesList from "./MatchesList";

interface TeamPerformanceTabProps {
  teamA: string;
  setTeamA: (team: string) => void;
  teamB: string;
  setTeamB: (team: string) => void;
  teamCompare: any;
  teamTeams: string[];
}

export default function TeamPerformanceTab({
  teamA,
  setTeamA,
  teamB,
  setTeamB,
  teamCompare,
  teamTeams,
}: TeamPerformanceTabProps) {
  // Mock data for team performance charts
  const teamPerformanceData = [
    { metric: "Goals", teamA: teamCompare.a.goals, teamB: teamCompare.b.goals },
    { metric: "Disposals", teamA: teamCompare.a.disposals, teamB: teamCompare.b.disposals },
    { metric: "Marks", teamA: teamCompare.a.marks, teamB: teamCompare.b.marks },
    { metric: "Tackles", teamA: teamCompare.a.tackles, teamB: teamCompare.b.tackles },
    { metric: "Clearances", teamA: teamCompare.a.clearances, teamB: teamCompare.b.clearances },
    { metric: "Inside 50s", teamA: teamCompare.a.inside50, teamB: teamCompare.b.inside50 },
  ];

  return (
    <div className="space-y-6">
      {/* Team Comparison Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Team Performance</h2>
          <p className="text-gray-600">Compare team statistics and match performance</p>
        </div>
        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
          <TrendingUp className="w-3 h-3 mr-1" />
          Live Data
        </Badge>
      </div>

      {/* Team Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Team Comparison
          </CardTitle>
          <CardDescription>
            Select teams to compare their performance metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Team A</label>
              <Select value={teamA} onValueChange={setTeamA}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {teamTeams.map((team) => (
                    <SelectItem key={team} value={team}>
                      {team}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Team B</label>
              <Select value={teamB} onValueChange={setTeamB}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {teamTeams.map((team) => (
                    <SelectItem key={team} value={team}>
                      {team}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Team Summary Cards */}
      <TeamSummaryCards teamCompare={teamCompare} teamA={teamA} teamB={teamB} />

      {/* Performance Comparison Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            Performance Comparison
          </CardTitle>
          <CardDescription>
            Side-by-side comparison of key performance metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={teamPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="metric" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="teamA" fill="#3b82f6" name={teamA} />
                <Bar dataKey="teamB" fill="#f59e0b" name={teamB} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Team Match Comparison */}
      <TeamMatchCompare
        teamA={teamA}
        setTeamA={setTeamA}
        teamB={teamB}
        setTeamB={setTeamB}
        teamTeams={teamTeams}
        teamCompare={teamCompare}
      />

      {/* Recent Matches */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Recent Matches
          </CardTitle>
          <CardDescription>
            Latest match results and statistics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <MatchesList />
        </CardContent>
      </Card>
    </div>
  );
}
