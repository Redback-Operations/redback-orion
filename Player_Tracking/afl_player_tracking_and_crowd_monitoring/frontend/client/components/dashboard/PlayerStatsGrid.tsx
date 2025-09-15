import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TrendingUp } from "lucide-react";

export default function PlayerStatsGrid({ selectedPlayer, performanceTrendData }: { selectedPlayer: any; performanceTrendData: any[] }) {
  if (!selectedPlayer) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Player Statistics</CardTitle>
          <CardDescription>No player selected</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">Please select a player to view statistics.</p>
        </CardContent>
      </Card>
    );
  }

  return (
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
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{selectedPlayer.kicks}</div>
            <div className="text-sm text-gray-600">Kicks</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">{selectedPlayer.handballs}</div>
            <div className="text-sm text-gray-600">Handballs</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{selectedPlayer.marks}</div>
            <div className="text-sm text-gray-600">Marks</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">{selectedPlayer.tackles}</div>
            <div className="text-sm text-gray-600">Tackles</div>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg">
            <div className="text-2xl font-bold text-red-600">{selectedPlayer.goals}</div>
            <div className="text-sm text-gray-600">Goals</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">{selectedPlayer.efficiency}%</div>
            <div className="text-sm text-gray-600">Efficiency</div>
          </div>
        </div>

        {/* Performance Trend Graph */}
        {performanceTrendData && performanceTrendData.length > 0 && (
          <div className="mt-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <h3 className="text-lg font-semibold">Performance Trend (Last 5 Weeks)</h3>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={performanceTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="kicks" 
                    stroke="#8b5cf6" 
                    strokeWidth={2} 
                    dot={{ fill: "#8b5cf6", strokeWidth: 2, r: 4 }} 
                    name="Kicks"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="handballs" 
                    stroke="#f59e0b" 
                    strokeWidth={2} 
                    dot={{ fill: "#f59e0b", strokeWidth: 2, r: 4 }} 
                    name="Handballs"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="marks" 
                    stroke="#10b981" 
                    strokeWidth={2} 
                    dot={{ fill: "#10b981", strokeWidth: 2, r: 4 }} 
                    name="Marks"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="tackles" 
                    stroke="#ef4444" 
                    strokeWidth={2} 
                    dot={{ fill: "#ef4444", strokeWidth: 2, r: 4 }} 
                    name="Tackles"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="goals" 
                    stroke="#dc2626" 
                    strokeWidth={2} 
                    dot={{ fill: "#dc2626", strokeWidth: 2, r: 4 }} 
                    name="Goals"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="efficiency" 
                    stroke="#eab308" 
                    strokeWidth={2} 
                    dot={{ fill: "#eab308", strokeWidth: 2, r: 4 }} 
                    name="Efficiency %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
