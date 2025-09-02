import { useState, useEffect } from "react";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import MobileNavigation from "@/components/MobileNavigation";
import LiveClock from "@/components/LiveClock";
import { Progress } from "@/components/ui/progress";
import {
  Search,
  Filter,
  Activity,
  BarChart3,
  Users,
  FileText,
  Video,
  Star,
} from "lucide-react";

// Player data
const players = [
  {
    id: 1,
    name: "Marcus Bontempelli",
    team: "Western Bulldogs",
    rating: 4.8,
    position: "Midfielder",
    stats: {
      kicks: 28,
      handballs: 12,
      marks: 8,
      tackles: 6,
      goals: 2,
      efficiency: 87
    }
  },
  {
    id: 2,
    name: "Dustin Martin",
    team: "Richmond",
    rating: 4.6,
    position: "Forward",
    stats: {
      kicks: 22,
      handballs: 8,
      marks: 6,
      tackles: 4,
      goals: 3,
      efficiency: 82
    }
  },
  {
    id: 3,
    name: "Patrick Dangerfield",
    team: "Geelong",
    rating: 4.7,
    position: "Midfielder",
    stats: {
      kicks: 25,
      handballs: 15,
      marks: 7,
      tackles: 8,
      goals: 1,
      efficiency: 84
    }
  }
];

export default function PlayerPerformance() {
  const [isLive, setIsLive] = useState(true);
  const [selectedPlayer, setSelectedPlayer] = useState(players[0]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");

  const teams = ["all", ...Array.from(new Set(players.map(p => p.team)))];

  const filteredPlayers = players.filter(
    (player) =>
      player.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedTeam === "all" || player.team === selectedTeam)
  );

  const StatBox = ({ label, value, color }: { label: string; value: string | number; color: string }) => (
    <div className={`p-4 rounded-lg text-center ${color}`}>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      <div className="text-sm text-white/90">{label}</div>
    </div>
  );

  const ComparisonBar = ({ 
    label, 
    player1Name, 
    player1Value, 
    player2Name, 
    player2Value 
  }: { 
    label: string; 
    player1Name: string; 
    player1Value: number; 
    player2Name: string; 
    player2Value: number; 
  }) => {
    const maxValue = Math.max(player1Value, player2Value);
    const player1Percentage = (player1Value / maxValue) * 100;
    const player2Percentage = (player2Value / maxValue) * 100;

    return (
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="font-medium">{label}</span>
          <span className="text-gray-600">{player1Value} vs {player2Value}</span>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs w-20 text-blue-600">{player1Name}</span>
            <div className="flex-1 bg-gray-200 rounded-full h-6">
              <div 
                className="bg-blue-500 h-6 rounded-full flex items-center justify-end pr-2"
                style={{ width: `${player1Percentage}%` }}
              >
                <span className="text-white text-xs font-medium">{player1Value}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs w-20 text-orange-600">{player2Name}</span>
            <div className="flex-1 bg-gray-200 rounded-full h-6">
              <div 
                className="bg-orange-500 h-6 rounded-full flex items-center justify-end pr-2"
                style={{ width: `${player2Percentage}%` }}
              >
                <span className="text-white text-xs font-medium">{player2Value}</span>
              </div>
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
              <p className="text-sm text-gray-600">Real-time insights & player analytics</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge className="bg-red-500">LIVE</Badge>
            <span className="text-sm text-gray-600">Welcome, demo@aflanalytics.com</span>
            <Button variant="outline" size="sm">Settings</Button>
            <Button variant="outline" size="sm">Logout</Button>
          </div>
        </div>
      </header>

      {/* Main Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="px-4">
          <Tabs defaultValue="player-performance" className="w-full">
            <TabsList className="h-12 bg-transparent border-0 gap-8">
              <TabsTrigger 
                value="player-performance" 
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-blue-600 rounded-none pb-3"
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                Player Performance
              </TabsTrigger>
              <TabsTrigger 
                value="crowd-monitor"
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-blue-600 rounded-none pb-3"
              >
                <Users className="w-4 h-4 mr-2" />
                Crowd Monitor
              </TabsTrigger>
              <TabsTrigger 
                value="reports"
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-blue-600 rounded-none pb-3"
              >
                <FileText className="w-4 h-4 mr-2" />
                Reports
              </TabsTrigger>
              <TabsTrigger 
                value="video-analysis"
                className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-blue-600 rounded-none pb-3"
              >
                <Video className="w-4 h-4 mr-2" />
                Video Analysis
              </TabsTrigger>
            </TabsList>

            <TabsContent value="player-performance" className="mt-0">
              <div className="grid grid-cols-12 gap-6 p-6">
                {/* Left Sidebar - Player Search & Filters */}
                <div className="col-span-3">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        <Search className="w-4 h-4" />
                        Player Search & Filters
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <label className="text-sm font-medium mb-2 block">Search Players</label>
                        <Input
                          placeholder="Search by name..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                        />
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium mb-2 block">Filter by Team</label>
                        <Select value={selectedTeam} onValueChange={setSelectedTeam}>
                          <SelectTrigger>
                            <SelectValue placeholder="All Teams" />
                          </SelectTrigger>
                          <SelectContent>
                            {teams.map((team) => (
                              <SelectItem key={team} value={team}>
                                {team === "all" ? "All Teams" : team}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      {/* Player List */}
                      <div className="space-y-2 pt-4">
                        {filteredPlayers.map((player) => (
                          <div
                            key={player.id}
                            className={`p-3 rounded-lg cursor-pointer transition-colors border ${
                              selectedPlayer.id === player.id
                                ? "bg-blue-50 border-blue-200"
                                : "bg-white border-gray-200 hover:bg-gray-50"
                            }`}
                            onClick={() => setSelectedPlayer(player)}
                          >
                            <div className="font-medium text-sm">{player.name}</div>
                            <div className="text-xs text-gray-600">{player.team}</div>
                            <div className="flex items-center gap-1 mt-1">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`w-3 h-3 ${
                                    i < Math.floor(player.rating)
                                      ? "text-yellow-400 fill-current"
                                      : "text-gray-300"
                                  }`}
                                />
                              ))}
                              <span className="text-xs text-gray-600 ml-1">{player.position}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Main Content Area */}
                <div className="col-span-9 space-y-6">
                  {/* Player Statistics */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span>Player Statistics - {selectedPlayer.name}</span>
                        <Badge variant="outline">Western Bulldogs</Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-6 gap-4">
                        <StatBox label="Kicks" value={selectedPlayer.stats.kicks} color="bg-blue-500" />
                        <StatBox label="Handballs" value={selectedPlayer.stats.handballs} color="bg-green-500" />
                        <StatBox label="Marks" value={selectedPlayer.stats.marks} color="bg-purple-500" />
                        <StatBox label="Tackles" value={selectedPlayer.stats.tackles} color="bg-red-500" />
                        <StatBox label="Goals" value={selectedPlayer.stats.goals} color="bg-orange-500" />
                        <StatBox label="Efficiency" value={`${selectedPlayer.stats.efficiency}%`} color="bg-teal-500" />
                      </div>
                    </CardContent>
                  </Card>

                  {/* Player Comparison */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Player Comparison</CardTitle>
                      <CardDescription>Compare Marcus Bontempelli with another player</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="flex items-center gap-4 mb-4">
                        <Select defaultValue="dustin-martin">
                          <SelectTrigger className="w-48">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="dustin-martin">Dustin Martin (Richmond)</SelectItem>
                            <SelectItem value="patrick-dangerfield">Patrick Dangerfield (Geelong)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-4">
                        <ComparisonBar
                          label="Kicks"
                          player1Name="Marcus Bontempelli"
                          player1Value={28}
                          player2Name="Dustin Martin"
                          player2Value={22}
                        />
                        <ComparisonBar
                          label="Handballs"
                          player1Name="Marcus Bontempelli"
                          player1Value={12}
                          player2Name="Dustin Martin"
                          player2Value={8}
                        />
                        <ComparisonBar
                          label="Marks"
                          player1Name="Marcus Bontempelli"
                          player1Value={8}
                          player2Name="Dustin Martin"
                          player2Value={6}
                        />
                        <ComparisonBar
                          label="Tackles"
                          player1Name="Marcus Bontempelli"
                          player1Value={6}
                          player2Name="Dustin Martin"
                          player2Value={4}
                        />
                        <ComparisonBar
                          label="Goals"
                          player1Name="Marcus Bontempelli"
                          player1Value={2}
                          player2Name="Dustin Martin"
                          player2Value={3}
                        />
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="crowd-monitor">
              <div className="p-6">
                <h2 className="text-2xl font-bold">Crowd Monitor</h2>
                <p className="text-gray-600">Stadium crowd analytics and safety monitoring</p>
              </div>
            </TabsContent>

            <TabsContent value="reports">
              <div className="p-6">
                <h2 className="text-2xl font-bold">Reports</h2>
                <p className="text-gray-600">Generate and download analytical reports</p>
              </div>
            </TabsContent>

            <TabsContent value="video-analysis">
              <div className="p-6">
                <h2 className="text-2xl font-bold">Video Analysis</h2>
                <p className="text-gray-600">AI-powered video analysis and insights</p>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
