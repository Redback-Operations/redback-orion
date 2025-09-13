import React from "react";
import { Card, CardContent } from "@/components/ui/card";

export default function TeamSummaryCards({ teamSummary }: { teamSummary: { games: number; goals: number; disposals: number; inside50: number } }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-4">
          <div className="text-sm text-gray-600">Matches</div>
          <div className="text-2xl font-semibold">{teamSummary.games}</div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="text-sm text-gray-600">Total Goals</div>
          <div className="text-2xl font-semibold">{teamSummary.goals}</div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="text-sm text-gray-600">Total Disposals</div>
          <div className="text-2xl font-semibold">{teamSummary.disposals.toLocaleString()}</div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="text-sm text-gray-600">Inside 50s</div>
          <div className="text-2xl font-semibold">{teamSummary.inside50}</div>
        </CardContent>
      </Card>
    </div>
  );
}
