import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar } from "@/components/ui/avatar";
import Link from "next/link";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const players = [
  {
    id: 1,
    name: "Lionel Messi",
    photo: "/players/messi.jpg",
    position: "Forward",
    team: "Inter Miami",
    stats: {
      goals: 30,
      assists: 15,
      distanceCoveredKm: 95.4,
      topSpeedKmH: 33.8,
      passesCompleted: 1240,
      tacklesWon: 8,
      minutesPlayed: 2200
    },
    age: 36,
    nationality: "Argentina",
    bio: "Widely considered the greatest footballer of all time."
  },
  {
    id: 2,
    name: "Cristiano Ronaldo",
    photo: "/players/ronaldo.jpg",
    position: "Forward",
    team: "Al Nassr",
    stats: {
      goals: 28,
      assists: 10,
      distanceCoveredKm: 110.1,
      topSpeedKmH: 34.7,
      passesCompleted: 990,
      tacklesWon: 5,
      minutesPlayed: 2300
    },
    age: 39,
    nationality: "Portugal",
    bio: "Global icon known for his athleticism and goal-scoring prowess."
  },
  {
    id: 3,
    name: "Kylian Mbappé",
    photo: "/players/mbappe.jpg",
    position: "Forward",
    team: "Paris Saint-Germain",
    stats: {
      goals: 25,
      assists: 12,
      distanceCoveredKm: 88.6,
      topSpeedKmH: 36.2,
      passesCompleted: 875,
      tacklesWon: 10,
      minutesPlayed: 2100
    },
    age: 25,
    nationality: "France",
    bio: "Lightning-fast striker known for his finishing and flair."
  },
  {
    id: 4,
    name: "Erling Haaland",
    photo: "/players/haaland.jpg",
    position: "Forward",
    team: "Manchester City",
    stats: {
      goals: 35,
      assists: 7,
      distanceCoveredKm: 97.2,
      topSpeedKmH: 35.1,
      passesCompleted: 720,
      tacklesWon: 6,
      minutesPlayed: 2250
    },
    age: 23,
    nationality: "Norway",
    bio: "Powerful goal-scoring machine dominating the Premier League."
  },
  {
    id: 5,
    name: "Kevin De Bruyne",
    photo: "/players/debruyne.jpg",
    position: "Midfielder",
    team: "Manchester City",
    stats: {
      goals: 10,
      assists: 20,
      distanceCoveredKm: 130.5,
      topSpeedKmH: 31.6,
      passesCompleted: 1500,
      tacklesWon: 20,
      minutesPlayed: 2400
    },
    age: 32,
    nationality: "Belgium",
    bio: "Elite playmaker with pinpoint passing and vision."
  },
  {
    id: 6,
    name: "Neymar Jr",
    photo: "/players/neymar.jpg",
    position: "Forward",
    team: "Al Hilal",
    stats: {
      goals: 22,
      assists: 14,
      distanceCoveredKm: 92.1,
      topSpeedKmH: 33.4,
      passesCompleted: 1085,
      tacklesWon: 11,
      minutesPlayed: 2150
    },
    age: 31,
    nationality: "Brazil",
    bio: "Creative flair and dribbling wizard from Brazil."
  }
];

export default function PlayerDashboard() {
  const [search, setSearch] = useState("");

  const filteredPlayers = players.filter((player) =>
    player.name.toLowerCase().includes(search.toLowerCase())
  );

  const chartData = filteredPlayers.map((player) => ({
    name: player.name,
    Goals: player.stats.goals,
    Assists: player.stats.assists,
    Passes: player.stats.passesCompleted
  }));

  return (
    <div className="min-h-screen bg-background text-foreground px-6 py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-extrabold tracking-tight">Player Dashboard</h1>
        <Input
          type="text"
          placeholder="Search players..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm bg-white text-black"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-10">
        {filteredPlayers.map((player) => (
          <Link
            key={player.id}
            href={{
              pathname: `/player/${player.id}`,
              query: {
                ...player,
                goals: player.stats.goals,
                assists: player.stats.assists,
                distance: player.stats.distanceCoveredKm,
                speed: player.stats.topSpeedKmH,
                passes: player.stats.passesCompleted,
                tackles: player.stats.tacklesWon,
                minutes: player.stats.minutesPlayed
              }
            }}
          >
            <Card className="bg-card border border-border cursor-pointer hover:scale-105 transition-transform">
              <CardContent className="flex flex-col items-center p-6">
                <Avatar className="w-24 h-24 mb-3">
                  <img src={player.photo} alt={player.name} className="rounded-full object-cover" />
                </Avatar>
                <div className="text-center">
                  <h2 className="text-xl font-semibold text-primary">{player.name}</h2>
                  <p className="text-sm text-muted-foreground">{player.position} — {player.team}</p>
                  <p className="text-xs mt-2">🎯 Goals: {player.stats.goals} | 🎯 Assists: {player.stats.assists}</p>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="bg-card p-6 rounded-lg border border-border">
        <h2 className="text-xl font-semibold mb-4 text-primary">Performance Comparison</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <XAxis dataKey="name" stroke="#ccc" />
            <YAxis stroke="#ccc" />
            <Tooltip />
            <Bar dataKey="Goals" fill="#facc15" />
            <Bar dataKey="Assists" fill="#60a5fa" />
            <Bar dataKey="Passes" fill="#34d399" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
