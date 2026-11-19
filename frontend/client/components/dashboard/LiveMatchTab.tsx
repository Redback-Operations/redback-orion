import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Activity, BarChart3, Clock } from "lucide-react";

// Placeholder data until a live match feed is wired up.
const matchEvents = [
  {
    time: "1:32",
    event: "GOAL",
    player: "Charlie Curnow",
    team: "Carlton",
    description: "Beautiful mark and goal from 30m out",
  },
  {
    time: "3:45",
    event: "BEHIND",
    player: "Taylor Walker",
    team: "Adelaide",
    description: "Shot from the boundary line",
  },
  {
    time: "5:12",
    event: "MARK",
    player: "Jeremy McGovern",
    team: "West Coast",
    description: "Spectacular defensive mark",
  },
  {
    time: "7:22",
    event: "TACKLE",
    player: "Clayton Oliver",
    team: "Melbourne",
    description: "Crucial tackle in defensive 50",
  },
];
export default function LiveMatchTab() {
  return (
    <>
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Live Score */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Live Match - Carlton vs Adelaide
              </span>
              <Badge variant="destructive" className="animate-pulse">
                LIVE
              </Badge>
            </CardTitle>
            <CardDescription>Quarter 2 - 15:23 remaining</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center space-y-4">
              <div className="flex justify-center items-center space-x-8">
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-600">72</div>
                  <div className="text-lg">Carlton</div>
                </div>
                <div className="text-2xl text-gray-400">vs</div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-red-600">68</div>
                  <div className="text-lg">Adelaide</div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mt-6">
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="text-lg font-semibold">324</div>
                  <div className="text-sm text-gray-600">Total Disposals</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="text-lg font-semibold">42</div>
                  <div className="text-sm text-gray-600">Marks</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="text-lg font-semibold">28</div>
                  <div className="text-sm text-gray-600">Tackles</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Match Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Match Statistics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Possession %</span>
                  <span>Carlton 52%</span>
                </div>
                <Progress value={52} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Inside 50s</span>
                  <span>28 - 24</span>
                </div>
                <Progress value={54} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Contested Marks</span>
                  <span>8 - 6</span>
                </div>
                <Progress value={57} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Live Events Timeline */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Live Events Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {matchEvents.map((event, index) => (
              <div
                key={index}
                className="flex items-start space-x-4 p-3 bg-gray-50 rounded-lg"
              >
                <div className="text-sm font-mono bg-gray-200 px-2 py-1 rounded">
                  {event.time}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        event.event === "GOAL"
                          ? "default"
                          : event.event === "BEHIND"
                            ? "secondary"
                            : "outline"
                      }
                    >
                      {event.event}
                    </Badge>
                    <span className="font-medium">{event.player}</span>
                    <span className="text-sm text-gray-600">
                      ({event.team})
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {event.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </>
  );
}
