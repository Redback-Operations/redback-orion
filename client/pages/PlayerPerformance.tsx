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
import MobileNavigation from "@/components/MobileNavigation";
import LiveClock from "@/components/LiveClock";
import {
  Search,
  Filter,
  Activity,
  BarChart3,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
} from "recharts";

// AFL Player data matching the reference image style
const aflPlayers = [
  {
    id: 1,
    name: "DAYNE ZORKO",
    team: "Brisbane Lions",
    teamAbbr: "BRI",
    number: "7",
    image: "https://cdn.builder.io/api/v1/image/assets%2Faf9aef6647464a4bb798d09aa34aaa76%2F97158aa81af244ddb0f0180f747a397e?format=webp&width=800",
    teamColor: "#8B0000",
    stats: {
      disposals: 34,
      kicks: 18,
      handballs: 16,
      marks: 8,
      tackles: 6,
      goals: 2,
      behinds: 1,
      efficiency: 78.5,
      goalAccuracy: 67,
      contestedPossessions: 12,
      uncontestedPossessions: 22
    }
  },
  {
    id: 2,
    name: "MARCUS BONTEMPELLI",
    team: "Western Bulldogs",
    teamAbbr: "WBD",
    number: "4",
    image: "https://cdn.builder.io/api/v1/image/assets%2Faf9aef6647464a4bb798d09aa34aaa76%2F97158aa81af244ddb0f0180f747a397e?format=webp&width=800",
    teamColor: "#FF6B35",
    stats: {
      disposals: 42,
      kicks: 24,
      handballs: 18,
      marks: 10,
      tackles: 8,
      goals: 3,
      behinds: 2,
      efficiency: 85.2,
      goalAccuracy: 60,
      contestedPossessions: 18,
      uncontestedPossessions: 24
    }
  },
  {
    id: 3,
    name: "PATRICK CRIPPS",
    team: "Carlton",
    teamAbbr: "CAR",
    number: "9",
    image: "https://cdn.builder.io/api/v1/image/assets%2Faf9aef6647464a4bb798d09aa34aaa76%2F97158aa81af244ddb0f0180f747a397e?format=webp&width=800",
    teamColor: "#1E3A8A",
    stats: {
      disposals: 38,
      kicks: 26,
      handballs: 12,
      marks: 7,
      tackles: 9,
      goals: 1,
      behinds: 0,
      efficiency: 82.7,
      goalAccuracy: 100,
      contestedPossessions: 20,
      uncontestedPossessions: 18
    }
  },
  {
    id: 4,
    name: "DUSTIN MARTIN",
    team: "Richmond",
    teamAbbr: "RIC",
    number: "4",
    image: "https://cdn.builder.io/api/v1/image/assets%2Faf9aef6647464a4bb798d09aa34aaa76%2F97158aa81af244ddb0f0180f747a397e?format=webp&width=800",
    teamColor: "#FFDD00",
    stats: {
      disposals: 28,
      kicks: 20,
      handballs: 8,
      marks: 6,
      tackles: 4,
      goals: 4,
      behinds: 1,
      efficiency: 89.4,
      goalAccuracy: 80,
      contestedPossessions: 10,
      uncontestedPossessions: 18
    }
  }
];

// Chart data for analytics
const possessionData = [
  { time: '12', possession: 45 },
  { time: '8', possession: 38 },
  { time: '20', possession: 52 },
  { time: '30', possession: 48 },
];

const playerMetricsData = [
  {
    name: 'Player Stats',
    'Dayne Zorko': 78.5,
    'Marcus Bontempelli': 85.2,
    'Patrick Cripps': 82.7,
    'Dustin Martin': 89.4,
  }
];

export default function PlayerPerformance() {
  const [isLive, setIsLive] = useState(true);
  const [selectedPlayers, setSelectedPlayers] = useState(aflPlayers.slice(0, 4));
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");

  const teams = ["all", ...Array.from(new Set(aflPlayers.map(p => p.team)))];

  const filteredPlayers = aflPlayers.filter(
    (player) =>
      player.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedTeam === "all" || player.team === selectedTeam)
  );

  const AFLTradingCard = ({ player }: { player: typeof aflPlayers[0] }) => (
    <div className="relative w-full max-w-xs mx-auto">
      {/* AFL Logo */}
      <div className="absolute top-3 left-3 z-20">
        <div className="bg-white rounded-full p-2 shadow-md">
          <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-xs">AFL</span>
          </div>
        </div>
      </div>

      {/* Player Number */}
      <div className="absolute top-3 right-3 z-20">
        <div className="bg-black/70 text-white px-2 py-1 rounded text-sm font-bold">
          #{player.number}
        </div>
      </div>

      {/* Main Card */}
      <div className="relative h-80 rounded-lg overflow-hidden shadow-lg border-2 border-gray-200">
        {/* Background Image/Color */}
        <div 
          className="absolute inset-0"
          style={{ backgroundColor: player.teamColor }}
        >
          {/* Player Image */}
          <img 
            src={player.image}
            alt={player.name}
            className="w-full h-full object-cover opacity-20"
          />
          
          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/80" />
        </div>

        {/* Player Name */}
        <div className="absolute top-12 left-3 right-3 z-10">
          <h3 className="text-white font-bold text-lg leading-tight">
            {player.name}
          </h3>
          <p className="text-white/80 text-sm">{player.teamAbbr}</p>
        </div>

        {/* Performance Stats Box */}
        <div className="absolute bottom-16 left-3 right-3 z-10">
          <div className="bg-black/80 backdrop-blur-sm rounded p-3">
            <div className="text-white text-xs space-y-1">
              <div className="flex justify-between">
                <span>GOAL ACCURACY:</span>
                <span className="font-bold">{player.stats.goalAccuracy}%</span>
              </div>
              <div className="flex justify-between">
                <span>HANDBALLS:</span>
                <span className="font-bold">{player.stats.handballs}</span>
              </div>
              <div className="flex justify-between">
                <span>DISPOSALS:</span>
                <span className="font-bold">{player.stats.disposals}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Stats Bar */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-red-600 to-red-700 p-3 z-10">
          <div className="grid grid-cols-3 gap-2 text-white text-center">
            <div>
              <div className="font-bold text-lg">{player.stats.kicks}</div>
              <div className="text-xs">KICKS</div>
            </div>
            <div>
              <div className="font-bold text-lg">{player.stats.marks}</div>
              <div className="text-xs">MARKS</div>
            </div>
            <div>
              <div className="font-bold text-lg">{player.stats.tackles}</div>
              <div className="text-xs">TACKLES</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      <MobileNavigation />

      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-6 space-y-6">
          {/* Live Clock */}
          <LiveClock
            isLive={isLive}
            onToggleLive={setIsLive}
            matchTime={{ quarter: 2, timeRemaining: "15:23" }}
          />

          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Player Filters
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Search Players</label>
                  <Input
                    placeholder="Search by name..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
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
              </div>
            </CardContent>
          </Card>

          {/* Player Cards Grid - Matching the reference image layout */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            {filteredPlayers.slice(0, 4).map((player) => (
              <AFLTradingCard key={player.id} player={player} />
            ))}
          </div>

          {/* Analytics Charts Section - Matching the reference image */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Possession Over Time Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Possession Over Time</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={possessionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Area 
                      type="monotone" 
                      dataKey="possession" 
                      stroke="#3b82f6" 
                      fill="#3b82f6" 
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Player Metrics Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Player Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={playerMetricsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Dayne Zorko" fill="#ef4444" />
                    <Bar dataKey="Marcus Bontempelli" fill="#f97316" />
                    <Bar dataKey="Patrick Cripps" fill="#3b82f6" />
                    <Bar dataKey="Dustin Martin" fill="#eab308" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Individual Player Statistics */}
          <Card>
            <CardHeader>
              <CardTitle>Individual Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-3">Player</th>
                      <th className="text-center p-3">Disposals</th>
                      <th className="text-center p-3">Kicks</th>
                      <th className="text-center p-3">Handballs</th>
                      <th className="text-center p-3">Marks</th>
                      <th className="text-center p-3">Tackles</th>
                      <th className="text-center p-3">Goals</th>
                      <th className="text-center p-3">Efficiency</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPlayers.map((player) => (
                      <tr key={player.id} className="border-b hover:bg-gray-50">
                        <td className="p-3 font-medium">{player.name}</td>
                        <td className="p-3 text-center">{player.stats.disposals}</td>
                        <td className="p-3 text-center">{player.stats.kicks}</td>
                        <td className="p-3 text-center">{player.stats.handballs}</td>
                        <td className="p-3 text-center">{player.stats.marks}</td>
                        <td className="p-3 text-center">{player.stats.tackles}</td>
                        <td className="p-3 text-center">{player.stats.goals}</td>
                        <td className="p-3 text-center">{player.stats.efficiency}%</td>
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
