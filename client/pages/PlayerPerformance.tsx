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
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import MobileNavigation from "@/components/MobileNavigation";
import LiveClock from "@/components/LiveClock";
import {
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  Target,
  Activity,
  Zap,
  Award,
  Users,
  BarChart3,
  LineChart,
  PieChart,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart as RechartsLineChart,
  Line,
  ResponsiveContainer,
} from "recharts";

// AFL Player data with realistic statistics
const aflPlayers = [
  {
    id: 1,
    name: "DAYNE ZORKO",
    fullName: "Dayne Zorko",
    number: "7",
    team: "Brisbane Lions",
    teamColor: "#8B0000", // Maroon
    position: "Midfielder",
    age: 34,
    height: "178cm",
    weight: "75kg",
    image: "/api/placeholder/200/250", // Placeholder for player image
    stats: {
      goalsAccuracy: 56.7,
      handballs: 23,
      disposals: 34,
      kicks: 18,
      marks: 8,
      tackles: 4,
      freeKicksFor: 2,
      freeKicksAgainst: 1,
      efficiency: 78.5,
      contestedPossessions: 12,
      uncontestedPossessions: 22
    },
    performanceData: [
      { round: 'R18', score: 85 },
      { round: 'R19', score: 92 },
      { round: 'R20', score: 78 },
      { round: 'R21', score: 88 },
      { round: 'R22', score: 95 },
    ]
  },
  {
    id: 2,
    name: "MARCUS BONTEMPELLI",
    fullName: "Marcus Bontempelli",
    number: "4",
    team: "Western Bulldogs",
    teamColor: "#FF6B35", // Orange/Red
    position: "Midfielder",
    age: 28,
    height: "193cm",
    weight: "92kg",
    image: "/api/placeholder/200/250",
    stats: {
      goalsAccuracy: 67.3,
      handballs: 28,
      disposals: 42,
      kicks: 24,
      marks: 10,
      tackles: 6,
      freeKicksFor: 3,
      freeKicksAgainst: 2,
      efficiency: 85.2,
      contestedPossessions: 18,
      uncontestedPossessions: 24
    },
    performanceData: [
      { round: 'R18', score: 88 },
      { round: 'R19', score: 91 },
      { round: 'R20', score: 85 },
      { round: 'R21', score: 93 },
      { round: 'R22', score: 89 },
    ]
  },
  {
    id: 3,
    name: "PATRICK CRIPPS",
    fullName: "Patrick Cripps",
    number: "9",
    team: "Carlton",
    teamColor: "#1E3A8A", // Navy Blue
    position: "Midfielder",
    age: 29,
    height: "195cm",
    weight: "95kg",
    image: "/api/placeholder/200/250",
    stats: {
      goalsAccuracy: 72.1,
      handballs: 22,
      disposals: 38,
      kicks: 26,
      marks: 7,
      tackles: 8,
      freeKicksFor: 4,
      freeKicksAgainst: 1,
      efficiency: 82.7,
      contestedPossessions: 20,
      uncontestedPossessions: 18
    },
    performanceData: [
      { round: 'R18', score: 90 },
      { round: 'R19', score: 87 },
      { round: 'R20', score: 92 },
      { round: 'R21', score: 85 },
      { round: 'R22', score: 91 },
    ]
  },
  {
    id: 4,
    name: "DUSTIN MARTIN",
    fullName: "Dustin Martin",
    number: "4",
    team: "Richmond",
    teamColor: "#FFFF00", // Yellow
    position: "Forward",
    age: 32,
    height: "187cm",
    weight: "92kg",
    image: "/api/placeholder/200/250",
    stats: {
      goalsAccuracy: 65.8,
      handballs: 15,
      disposals: 28,
      kicks: 20,
      marks: 6,
      tackles: 3,
      freeKicksFor: 1,
      freeKicksAgainst: 0,
      efficiency: 89.4,
      contestedPossessions: 10,
      uncontestedPossessions: 18
    },
    performanceData: [
      { round: 'R18', score: 82 },
      { round: 'R19', score: 89 },
      { round: 'R20', score: 91 },
      { round: 'R21', score: 87 },
      { round: 'R22', score: 85 },
    ]
  }
];

export default function PlayerPerformance() {
  const [isLive, setIsLive] = useState(true);
  const [selectedPlayers, setSelectedPlayers] = useState([aflPlayers[0], aflPlayers[1]]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");
  const [selectedPosition, setSelectedPosition] = useState("all");

  const teams = ["all", ...Array.from(new Set(aflPlayers.map(p => p.team)))];
  const positions = ["all", ...Array.from(new Set(aflPlayers.map(p => p.position)))];

  const filteredPlayers = aflPlayers.filter(
    (player) =>
      player.fullName.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedTeam === "all" || player.team === selectedTeam) &&
      (selectedPosition === "all" || player.position === selectedPosition)
  );

  const AFLPlayerCard = ({ player }: { player: typeof aflPlayers[0] }) => (
    <div className="relative w-full max-w-sm mx-auto">
      {/* AFL Logo */}
      <div className="absolute top-4 left-4 z-10">
        <div className="bg-white rounded-full p-2">
          <div className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-xs">AFL</span>
          </div>
        </div>
      </div>

      {/* Main Card */}
      <div 
        className="relative h-80 rounded-lg overflow-hidden shadow-lg"
        style={{ backgroundColor: player.teamColor }}
      >
        {/* Player Image Area */}
        <div className="relative h-full w-full">
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          
          {/* Player Name */}
          <div className="absolute top-16 left-4 right-4">
            <h2 className="text-white font-bold text-xl tracking-wide">
              {player.name}
            </h2>
          </div>

          {/* Player Number */}
          <div className="absolute top-4 right-4">
            <div className="text-white/80 font-bold text-lg">
              #{player.number}
            </div>
          </div>

          {/* Stats Section */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-yellow-400 to-yellow-500 p-4">
            <div className="grid grid-cols-3 gap-2 text-black">
              <div className="text-center">
                <div className="font-bold text-lg">{player.stats.disposals}</div>
                <div className="text-xs font-medium">DISPOSALS</div>
              </div>
              <div className="text-center">
                <div className="font-bold text-lg">{player.stats.kicks}</div>
                <div className="text-xs font-medium">KICKS</div>
              </div>
              <div className="text-center">
                <div className="font-bold text-lg">{player.stats.handballs}</div>
                <div className="text-xs font-medium">HANDBALLS</div>
              </div>
            </div>
          </div>

          {/* Performance Stats */}
          <div className="absolute bottom-20 left-4 right-4">
            <div className="bg-black/70 rounded p-2 text-white text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>EFFICIENCY: {player.stats.efficiency}%</div>
                <div>MARKS: {player.stats.marks}</div>
                <div>TACKLES: {player.stats.tackles}</div>
                <div>GOALS ACC: {player.stats.goalsAccuracy}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Team Badge */}
      <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2">
        <div className="bg-white rounded-full p-2 shadow-lg">
          <div className="text-xs font-bold text-center px-2">
            {player.team.split(' ').map(word => word[0]).join('')}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100">
      <MobileNavigation />

      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-6">
          {/* Live Clock */}
          <LiveClock
            isLive={isLive}
            onToggleLive={setIsLive}
            matchTime={{ quarter: 2, timeRemaining: "15:23" }}
          />

          {/* Header */}
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Player Performance Analytics</h1>
            <p className="text-gray-600">Compare AFL players with detailed statistics and performance metrics</p>
          </div>

          {/* Filters Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Player Selection & Filters
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Search Players</label>
                  <Input
                    placeholder="Search by name..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Filter by Team</label>
                  <Select value={selectedTeam} onValueChange={setSelectedTeam}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select team" />
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

                <div>
                  <label className="block text-sm font-medium mb-2">Filter by Position</label>
                  <Select value={selectedPosition} onValueChange={setSelectedPosition}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select position" />
                    </SelectTrigger>
                    <SelectContent>
                      {positions.map((position) => (
                        <SelectItem key={position} value={position}>
                          {position === "all" ? "All Positions" : position}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Player Selection Dropdowns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <label className="block text-sm font-medium mb-2">Select Player 1</label>
                  <Select 
                    value={selectedPlayers[0]?.id.toString()} 
                    onValueChange={(value) => {
                      const player = filteredPlayers.find(p => p.id.toString() === value);
                      if (player) setSelectedPlayers([player, selectedPlayers[1]]);
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose first player" />
                    </SelectTrigger>
                    <SelectContent>
                      {filteredPlayers.map((player) => (
                        <SelectItem key={player.id} value={player.id.toString()}>
                          {player.fullName} ({player.team})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Select Player 2</label>
                  <Select 
                    value={selectedPlayers[1]?.id.toString()} 
                    onValueChange={(value) => {
                      const player = filteredPlayers.find(p => p.id.toString() === value);
                      if (player) setSelectedPlayers([selectedPlayers[0], player]);
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose second player" />
                    </SelectTrigger>
                    <SelectContent>
                      {filteredPlayers.map((player) => (
                        <SelectItem key={player.id} value={player.id.toString()}>
                          {player.fullName} ({player.team})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Player Cards Display */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {selectedPlayers.map((player, index) => (
              <div key={player.id} className="space-y-2">
                <h3 className="text-center font-medium text-gray-700">
                  Player {index + 1}
                </h3>
                <AFLPlayerCard player={player} />
              </div>
            ))}
          </div>

          {/* Performance Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Over Time Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Over Time</CardTitle>
                <CardDescription>Last 5 rounds performance comparison</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RechartsLineChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="round" />
                    <YAxis domain={[70, 100]} />
                    <Tooltip />
                    <Legend />
                    <Line 
                      dataKey="score" 
                      data={selectedPlayers[0]?.performanceData || []}
                      stroke="#8884d8" 
                      strokeWidth={3}
                      name={selectedPlayers[0]?.fullName || "Player 1"}
                    />
                    <Line 
                      dataKey="score" 
                      data={selectedPlayers[1]?.performanceData || []}
                      stroke="#82ca9d" 
                      strokeWidth={3}
                      name={selectedPlayers[1]?.fullName || "Player 2"}
                    />
                  </RechartsLineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Player Metrics Comparison */}
            <Card>
              <CardHeader>
                <CardTitle>Player Metrics</CardTitle>
                <CardDescription>Key statistics comparison</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={[
                    {
                      metric: 'Disposals',
                      [selectedPlayers[0]?.fullName || 'Player 1']: selectedPlayers[0]?.stats.disposals || 0,
                      [selectedPlayers[1]?.fullName || 'Player 2']: selectedPlayers[1]?.stats.disposals || 0,
                    },
                    {
                      metric: 'Kicks',
                      [selectedPlayers[0]?.fullName || 'Player 1']: selectedPlayers[0]?.stats.kicks || 0,
                      [selectedPlayers[1]?.fullName || 'Player 2']: selectedPlayers[1]?.stats.kicks || 0,
                    },
                    {
                      metric: 'Marks',
                      [selectedPlayers[0]?.fullName || 'Player 1']: selectedPlayers[0]?.stats.marks || 0,
                      [selectedPlayers[1]?.fullName || 'Player 2']: selectedPlayers[1]?.stats.marks || 0,
                    },
                    {
                      metric: 'Tackles',
                      [selectedPlayers[0]?.fullName || 'Player 1']: selectedPlayers[0]?.stats.tackles || 0,
                      [selectedPlayers[1]?.fullName || 'Player 2']: selectedPlayers[1]?.stats.tackles || 0,
                    },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey={selectedPlayers[0]?.fullName || 'Player 1'} fill="#ef4444" />
                    <Bar dataKey={selectedPlayers[1]?.fullName || 'Player 2'} fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Stats Comparison Table */}
          <Card>
            <CardHeader>
              <CardTitle>Detailed Statistics Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Statistic</th>
                      <th className="text-center p-2">{selectedPlayers[0]?.fullName}</th>
                      <th className="text-center p-2">{selectedPlayers[1]?.fullName}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { key: 'disposals', label: 'Disposals' },
                      { key: 'kicks', label: 'Kicks' },
                      { key: 'handballs', label: 'Handballs' },
                      { key: 'marks', label: 'Marks' },
                      { key: 'tackles', label: 'Tackles' },
                      { key: 'efficiency', label: 'Efficiency %' },
                      { key: 'goalsAccuracy', label: 'Goals Accuracy %' },
                    ].map((stat) => (
                      <tr key={stat.key} className="border-b hover:bg-gray-50">
                        <td className="p-2 font-medium">{stat.label}</td>
                        <td className="p-2 text-center">
                          {selectedPlayers[0]?.stats[stat.key as keyof typeof selectedPlayers[0]['stats']] || 0}
                        </td>
                        <td className="p-2 text-center">
                          {selectedPlayers[1]?.stats[stat.key as keyof typeof selectedPlayers[1]['stats']] || 0}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
