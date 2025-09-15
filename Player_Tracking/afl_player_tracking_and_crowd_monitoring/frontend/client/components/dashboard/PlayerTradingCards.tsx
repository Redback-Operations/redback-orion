import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Star } from "lucide-react";

export default function PlayerTradingCards({
  selectedPlayer,
  onPlayerSelect,
}: {
  selectedPlayer: any;
  onPlayerSelect: (player: any) => void;
}) {
  // Mock data for trading cards - this should eventually come from the backend
  const playerCards = [
    {
      id: 1,
      name: "Dayne Zorko",
      team: "Brisbane Lions",
      jerseyNumber: 7,
      position: "Midfielder",
      goalAccuracy: 67,
      handballs: 16,
      disposals: 34,
      kicks: 18,
      marks: 8,
      tackles: 6,
      teamColor: "from-red-800 to-red-900",
    },
    {
      id: 2,
      name: "Marcus Bontempelli",
      team: "Western Bulldogs",
      jerseyNumber: 4,
      position: "Midfielder",
      goalAccuracy: 60,
      handballs: 18,
      disposals: 42,
      kicks: 24,
      marks: 10,
      tackles: 8,
      teamColor: "from-orange-600 to-orange-700",
    },
    {
      id: 3,
      name: "Patrick Cripps",
      team: "Carlton",
      jerseyNumber: 9,
      position: "Midfielder",
      goalAccuracy: 100,
      handballs: 12,
      disposals: 38,
      kicks: 26,
      marks: 7,
      tackles: 9,
      teamColor: "from-blue-800 to-blue-900",
    },
    {
      id: 4,
      name: "Dustin Martin",
      team: "Richmond",
      jerseyNumber: 4,
      position: "Forward",
      goalAccuracy: 80,
      handballs: 8,
      disposals: 28,
      kicks: 20,
      marks: 6,
      tackles: 4,
      teamColor: "from-yellow-500 to-yellow-600",
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Player Trading Cards</CardTitle>
        <CardDescription>
          AFL player cards with photos and jersey numbers
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {playerCards.map((card) => (
            <div key={card.id} className="relative w-full max-w-xs mx-auto">
              <div className="absolute top-3 left-3 z-20">
                <div className="bg-white rounded-full p-2 shadow-md">
                  <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-xs">AFL</span>
                  </div>
                </div>
              </div>
              <div className="absolute top-3 right-3 z-20">
                <div className="bg-black/70 text-white px-2 py-1 rounded text-sm font-bold">
                  #{card.jerseyNumber}
                </div>
              </div>
              <div className={`relative h-80 rounded-lg overflow-hidden shadow-lg border-2 border-gray-200 bg-gradient-to-b from-${card.teamColor.split(' ')[1]} to-${card.teamColor.split(' ')[3]}`}>
                <img
                  src="https://cdn.builder.io/api/v1/image/assets%2Faf9aef6647464a4bb798d09aa34aaa76%2F97158aa81af244ddb0f0180f747a397e?format=webp&width=800"
                  alt={card.name}
                  className="w-full h-full object-cover opacity-30"
                />
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/80" />
                <div className="absolute top-12 left-3 right-3 z-10">
                  <h3 className="text-white font-bold text-lg leading-tight">
                    {card.name.toUpperCase()}
                  </h3>
                  <p className="text-white/80 text-sm">{card.team}</p>
                </div>
                <div className="absolute bottom-16 left-3 right-3 z-10">
                  <div className="bg-black/80 backdrop-blur-sm rounded p-3">
                    <div className="text-white text-xs space-y-1">
                      <div className="flex justify-between">
                        <span>GOAL ACCURACY:</span>
                        <span className="font-bold">{card.goalAccuracy}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>HANDBALLS:</span>
                        <span className="font-bold">{card.handballs}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>DISPOSALS:</span>
                        <span className="font-bold">{card.disposals}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-r from-red-600 to-red-700 p-3 z-10">
                  <div className="grid grid-cols-3 gap-2 text-white text-center">
                    <div>
                      <div className="font-bold text-lg">{card.kicks}</div>
                      <div className="text-xs">KICKS</div>
                    </div>
                    <div>
                      <div className="font-bold text-lg">{card.marks}</div>
                      <div className="text-xs">MARKS</div>
                    </div>
                    <div>
                      <div className="font-bold text-lg">{card.tackles}</div>
                      <div className="text-xs">TACKLES</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}