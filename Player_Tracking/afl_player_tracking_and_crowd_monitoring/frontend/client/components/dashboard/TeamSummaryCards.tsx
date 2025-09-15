import React from "react";
import { Card, CardContent } from "@/components/ui/card";

export default function TeamSummaryCards({ teamCompare, teamA, teamB }: { teamCompare: any; teamA: string; teamB: string }) {
  // Create summary data from teamCompare
  const teamASummary = {
    games: 3, // Mock data - should come from backend
    goals: teamCompare?.a?.goals || 0,
    disposals: teamCompare?.a?.disposals || 0,
    inside50: teamCompare?.a?.inside50 || 0,
  };

  const teamBSummary = {
    games: 3, // Mock data - should come from backend
    goals: teamCompare?.b?.goals || 0,
    disposals: teamCompare?.b?.disposals || 0,
    inside50: teamCompare?.b?.inside50 || 0,
  };

  return (
    <div className="space-y-6">
      {/* Team A Summary */}
      <div>
        <h3 className="text-lg font-semibold mb-4">{teamA}</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-gray-600">Matches</div>
              <div className="text-2xl font-semibold">{teamASummary.games}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-gray-600">Total Goals</div>
              <div className="text-2xl font-semibold">{teamASummary.goals}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-gray-600">Disposals</div>
              <div className="text-2xl font-semibold">{teamASummary.disposals}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-gray-600">Inside 50s</div>
              <div className="text-2xl font-semibold">{teamASummary.inside50}</div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Team B Summary */}
      <div>
        <h3 className="text-lg font-semibold mb-4">{teamB}</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-gray-600">Matches</div>
              <div className="text-2xl font-semibold">{teamBSummary.games}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-gray-600">Total Goals</div>
              <div className="text-2xl font-semibold">{teamBSummary.goals}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-gray-600">Disposals</div>
              <div className="text-2xl font-semibold">{teamBSummary.disposals}</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-sm text-gray-600">Inside 50s</div>
              <div className="text-2xl font-semibold">{teamBSummary.inside50}</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}