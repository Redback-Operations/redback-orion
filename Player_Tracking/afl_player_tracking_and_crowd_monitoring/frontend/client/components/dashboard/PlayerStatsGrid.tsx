import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function PlayerStatsGrid({ selectedPlayer }: { selectedPlayer: any }) {
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
      </CardContent>
    </Card>
  );
}
