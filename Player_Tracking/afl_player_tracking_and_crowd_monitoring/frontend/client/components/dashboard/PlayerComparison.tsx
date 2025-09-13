import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Target } from "lucide-react";
import { ResponsiveContainer as RC, LineChart as RL, CartesianGrid as RG, XAxis as RX, YAxis as RY, Tooltip as RT, Legend as RLg, Line as RLine } from "recharts";

export default function PlayerComparison({
  selectedPlayer,
  comparisonPlayer,
  setComparisonPlayer,
  mockPlayers,
  playerComparisonData,
}: {
  selectedPlayer: any;
  comparisonPlayer: any;
  setComparisonPlayer: (p: any) => void;
  mockPlayers: any[];
  playerComparisonData: any[];
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="w-5 h-5" />
          Player Comparison
        </CardTitle>
        <CardDescription>Compare {selectedPlayer.name} with another player</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6">
          <Select value={comparisonPlayer.name} onValueChange={(name) => {
            const player = mockPlayers.find((p) => p.name === name);
            if (player) setComparisonPlayer(player);
          }}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select player to compare" />
            </SelectTrigger>
            <SelectContent>
              {mockPlayers.filter((p) => p.id !== selectedPlayer.id).map((player) => (
                <SelectItem key={player.id} value={player.name}>
                  {player.name} ({player.team})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-gray-700">Statistical Comparison</h4>
            {["kicks", "handballs", "marks", "tackles", "goals"].map((stat) => (
              <div key={stat} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="capitalize">{stat}</span>
                  <span>
                    {selectedPlayer[stat]} vs {comparisonPlayer[stat]}
                  </span>
                </div>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <Progress value={(selectedPlayer[stat] / Math.max(selectedPlayer[stat], comparisonPlayer[stat])) * 100} className="h-2" />
                    <div className="text-xs text-gray-600 mt-1">{selectedPlayer.name}</div>
                  </div>
                  <div className="flex-1">
                    <Progress value={(comparisonPlayer[stat] / Math.max(selectedPlayer[stat], comparisonPlayer[stat])) * 100} className="h-2" />
                    <div className="text-xs text-gray-600 mt-1">{comparisonPlayer.name}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-gray-700">Performance Trend</h4>
            <div className="h-64 w-full">
              <RC width="100%" height="100%">
                <RL data={playerComparisonData}>
                  <RG strokeDasharray="3 3" />
                  <RX dataKey="stat" tick={{ fontSize: 12 }} angle={-45} textAnchor="end" height={80} />
                  <RY tick={{ fontSize: 12 }} />
                  <RT contentStyle={{ backgroundColor: "#f8f9fa", border: "1px solid #e9ecef", borderRadius: "6px" }} />
                  <RLg />
                  <RLine type="monotone" dataKey={selectedPlayer.name} stroke="#059669" strokeWidth={3} dot={{ fill: "#059669", strokeWidth: 2, r: 4 }} activeDot={{ r: 6, stroke: "#059669", strokeWidth: 2 }} />
                  <RLine type="monotone" dataKey={comparisonPlayer.name} stroke="#2563eb" strokeWidth={3} dot={{ fill: "#2563eb", strokeWidth: 2, r: 4 }} activeDot={{ r: 6, stroke: "#2563eb", strokeWidth: 2 }} />
                </RL>
              </RC>
            </div>
            <div className="text-xs text-gray-600 text-center">Performance metrics comparison between selected players</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
