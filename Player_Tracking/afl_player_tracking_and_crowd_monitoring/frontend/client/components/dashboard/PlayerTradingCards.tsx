import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Activity } from "lucide-react";

export default function PlayerTradingCards({
  playerCards,
  showAllCards,
  setShowAllCards,
  selectedCardIndex,
  setSelectedCardIndex,
  expandedCardId,
  setExpandedCardId,
  onSelectCard,
}: {
  playerCards: any[];
  showAllCards: boolean;
  setShowAllCards: (v: boolean) => void;
  selectedCardIndex: number;
  setSelectedCardIndex: (i: number) => void;
  expandedCardId: number | null;
  setExpandedCardId: (id: number | null) => void;
  onSelectCard: (card: any) => void;
}) {
  const handleCardClick = (card: any, index: number) => {
    onSelectCard(card);
    setSelectedCardIndex(index);
    setExpandedCardId(expandedCardId === card.id ? null : card.id);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Player Profiles
          </div>
          <Button variant="outline" size="sm" onClick={() => setShowAllCards(!showAllCards)}>
            {showAllCards ? "Show One" : "View All"}
          </Button>
        </CardTitle>
        <CardDescription>View AFL player profiles with stats and performance data</CardDescription>
      </CardHeader>
      <CardContent>
        {showAllCards ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {playerCards.map((card, index) => {
              const isExpanded = expandedCardId === card.id;
              return (
                <div
                  key={card.id}
                  className={`relative w-full mx-auto cursor-pointer transform transition-all duration-500 hover:shadow-xl ${
                    isExpanded ? "col-span-full max-w-2xl scale-105 z-10" : "max-w-xs hover:scale-105"
                  }`}
                  onClick={() => handleCardClick(card, index)}
                >
                  <div className="absolute top-3 left-3 z-20">
                    <div className="bg-white rounded-full p-2 shadow-md">
                      <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-xs">AFL</span>
                      </div>
                    </div>
                  </div>
                  <div className="absolute top-3 right-3 z-20">
                    <div className="bg-black/70 text-white px-2 py-1 rounded text-sm font-bold">#{card.number}</div>
                  </div>
                  {isExpanded && (
                    <div className="absolute top-3 left-1/2 transform -translate-x-1/2 z-20">
                      <div className="bg-orange-600 text-white px-3 py-1 rounded-full text-xs font-bold animate-pulse">EXPANDED VIEW</div>
                    </div>
                  )}
                  <div className={`relative rounded-lg overflow-hidden shadow-lg border-2 bg-gradient-to-b ${card.background} transition-all duration-500 ${isExpanded ? "h-[500px] border-orange-400" : "h-80 border-gray-200"}`}>
                    <img src={card.image} alt={card.name} className={`w-full h-full object-cover transition-opacity duration-500 ${isExpanded ? "opacity-95" : "opacity-80"}`} />
                    <div className={`absolute inset-0 bg-gradient-to-b transition-opacity duration-500 ${isExpanded ? "from-transparent via-black/20 to-black/90" : "from-transparent via-transparent to-black/80"}`} />
                    <div className={`absolute left-3 right-3 z-10 transition-all duration-500 ${isExpanded ? "top-16" : "top-12"}`}>
                      <h3 className={`text-white font-bold leading-tight transition-all duration-500 ${isExpanded ? "text-2xl" : "text-lg"}`}>{card.name}</h3>
                      <p className={`text-white/80 transition-all duration-500 ${isExpanded ? "text-lg" : "text-sm"}`}>{card.team}</p>
                    </div>
                    <div className={`absolute left-3 right-3 z-10 transition-all duration-500 ${isExpanded ? "bottom-32" : "bottom-16"}`}>
                      <div className={`bg-black/80 backdrop-blur-sm rounded transition-all duration-500 ${isExpanded ? "p-4" : "p-3"}`}>
                        <div className={`text-white space-y-1 transition-all duration-500 ${isExpanded ? "text-sm" : "text-xs"}`}>
                          <div className="flex justify-between"><span>GOAL ACCURACY:</span><span className="font-bold">{card.stats.goalAccuracy}%</span></div>
                          <div className="flex justify-between"><span>HANDBALLS:</span><span className="font-bold">{card.stats.handballs}</span></div>
                          <div className="flex justify-between"><span>DISPOSALS:</span><span className="font-bold">{card.stats.disposals}</span></div>
                        </div>
                      </div>
                    </div>
                    <div className={`absolute bottom-0 left-0 right-0 bg-gradient-to-r from-red-600 to-red-700 z-10 transition-all duration-500 ${isExpanded ? "p-4" : "p-3"}`}>
                      <div className={`grid grid-cols-3 gap-2 text-white text-center transition-all duration-500 ${isExpanded ? "mb-2" : ""}`}>
                        <div><div className={`font-bold transition-all duration-500 ${isExpanded ? "text-xl" : "text-lg"}`}>{card.stats.kicks}</div><div className={`transition-all duration-500 ${isExpanded ? "text-sm" : "text-xs"}`}>KICKS</div></div>
                        <div><div className={`font-bold transition-all duration-500 ${isExpanded ? "text-xl" : "text-lg"}`}>{card.stats.marks}</div><div className={`transition-all duration-500 ${isExpanded ? "text-sm" : "text-xs"}`}>MARKS</div></div>
                        <div><div className={`font-bold transition-all duration-500 ${isExpanded ? "text-xl" : "text-lg"}`}>{card.stats.tackles}</div><div className={`transition-all duration-500 ${isExpanded ? "text-sm" : "text-xs"}`}>TACKLES</div></div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-col items-center space-y-4">
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm" onClick={() => setSelectedCardIndex(Math.max(0, selectedCardIndex - 1))} disabled={selectedCardIndex === 0}>← Previous</Button>
              <span className="text-sm text-gray-600">{selectedCardIndex + 1} of {playerCards.length}</span>
              <Button variant="outline" size="sm" onClick={() => setSelectedCardIndex(Math.min(playerCards.length - 1, selectedCardIndex + 1))} disabled={selectedCardIndex === playerCards.length - 1}>Next →</Button>
            </div>

            {(() => {
              const card = playerCards[selectedCardIndex];
              const isExpanded = expandedCardId === card.id;
              return (
                <div
                  className={`relative w-full mx-auto cursor-pointer transform transition-all duration-500 hover:shadow-xl ${
                    isExpanded ? "max-w-2xl scale-105" : "max-w-sm hover:scale-105"
                  }`}
                  onClick={() => handleCardClick(card, selectedCardIndex)}
                >
                  <div className="absolute top-3 left-3 z-20">
                    <div className="bg-white rounded-full p-2 shadow-md">
                      <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-xs">AFL</span>
                      </div>
                    </div>
                  </div>
                  <div className="absolute top-3 right-3 z-20">
                    <div className="bg-black/70 text-white px-2 py-1 rounded text-sm font-bold">#{card.number}</div>
                  </div>
                  {isExpanded && (
                    <div className="absolute top-3 left-1/2 transform -translate-x-1/2 z-20">
                      <div className="bg-orange-600 text-white px-3 py-1 rounded-full text-xs font-bold animate-pulse">EXPANDED VIEW</div>
                    </div>
                  )}
                  <div className={`relative rounded-lg overflow-hidden shadow-lg border-2 bg-gradient-to-b ${card.background} transition-all duration-500 ${isExpanded ? "h-[600px] border-orange-400" : "h-96 border-gray-200"}`}>
                    <img src={card.image} alt={card.name} className={`w-full h-full object-cover transition-opacity duration-500 ${isExpanded ? "opacity-95" : "opacity-80"}`} />
                    <div className={`absolute inset-0 bg-gradient-to-b transition-opacity duration-500 ${isExpanded ? "from-transparent via-black/20 to-black/90" : "from-transparent via-transparent to-black/80"}`} />
                    <div className={`absolute left-3 right-3 z-10 transition-all duration-500 ${isExpanded ? "top-16" : "top-12"}`}>
                      <h3 className={`text-white font-bold leading-tight transition-all duration-500 ${isExpanded ? "text-3xl" : "text-xl"}`}>{card.name}</h3>
                      <p className={`text-white/80 transition-all duration-500 ${isExpanded ? "text-xl" : "text-base"}`}>{card.team}</p>
                    </div>
                    <div className={`absolute left-3 right-3 z-10 transition-all duration-500 ${isExpanded ? "bottom-40" : "bottom-20"}`}>
                      <div className={`bg-black/80 backdrop-blur-sm rounded transition-all duration-500 ${isExpanded ? "p-6" : "p-4"}`}>
                        <div className={`text-white space-y-2 transition-all duration-500 ${isExpanded ? "text-base" : "text-sm"}`}>
                          <div className="flex justify-between"><span>GOAL ACCURACY:</span><span className="font-bold">{card.stats.goalAccuracy}%</span></div>
                          <div className="flex justify-between"><span>HANDBALLS:</span><span className="font-bold">{card.stats.handballs}</span></div>
                          <div className="flex justify-between"><span>DISPOSALS:</span><span className="font-bold">{card.stats.disposals}</span></div>
                        </div>
                      </div>
                    </div>
                    <div className={`absolute bottom-0 left-0 right-0 bg-gradient-to-r from-red-600 to-red-700 z-10 transition-all duration-500 ${isExpanded ? "p-6" : "p-4"}`}>
                      <div className={`grid grid-cols-3 gap-2 text-white text-center transition-all duration-500 ${isExpanded ? "mb-2" : ""}`}>
                        <div><div className={`font-bold transition-all duration-500 ${isExpanded ? "text-xl" : "text-lg"}`}>{card.stats.kicks}</div><div className={`transition-all duration-500 ${isExpanded ? "text-sm" : "text-xs"}`}>KICKS</div></div>
                        <div><div className={`font-bold transition-all duration-500 ${isExpanded ? "text-xl" : "text-lg"}`}>{card.stats.marks}</div><div className={`transition-all duration-500 ${isExpanded ? "text-sm" : "text-xs"}`}>MARKS</div></div>
                        <div><div className={`font-bold transition-all duration-500 ${isExpanded ? "text-xl" : "text-lg"}`}>{card.stats.tackles}</div><div className={`transition-all duration-500 ${isExpanded ? "text-sm" : "text-xs"}`}>TACKLES</div></div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
