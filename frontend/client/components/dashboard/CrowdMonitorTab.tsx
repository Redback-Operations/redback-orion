import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  TrendingUp,
  TrendingDown,
  MapPin,
  Eye,
  Calendar,
  Shield,
} from "lucide-react";

// Placeholder data until crowd zones come from the backend.
const crowdZones = [
  {
    zone: "Northern Stand",
    capacity: 15000,
    current: 13200,
    density: 88,
    trend: "up",
  },
  {
    zone: "Southern Stand",
    capacity: 12000,
    current: 11400,
    density: 95,
    trend: "stable",
  },
  {
    zone: "Eastern Wing",
    capacity: 8000,
    current: 6800,
    density: 85,
    trend: "down",
  },
  {
    zone: "Western Wing",
    capacity: 8000,
    current: 7600,
    density: 95,
    trend: "up",
  },
  {
    zone: "Premium Seating",
    capacity: 3000,
    current: 2850,
    density: 95,
    trend: "stable",
  },
];
const safestZone = crowdZones.reduce(
  (min, zone) => (zone.density < min.density ? zone : min),
  crowdZones[0],
);
export default function CrowdMonitorTab() {
  return (
    <>
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              Stadium Zone Density
            </CardTitle>
            <CardDescription>
              Real-time crowd distribution across stadium zones
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {crowdZones.map((zone, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{zone.zone}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">
                        {zone.current.toLocaleString()} /{" "}
                        {zone.capacity.toLocaleString()}
                      </span>
                      {zone.trend === "up" && (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      )}
                      {zone.trend === "down" && (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      {zone.trend === "stable" && (
                        <div className="w-4 h-4 rounded-full bg-gray-400" />
                      )}
                    </div>
                  </div>
                  <Progress value={zone.density} className="h-3" />
                  <div className="text-xs text-gray-600 text-right">
                    {zone.density}% capacity
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Visual Stadium Map
            </CardTitle>
            <CardDescription>
              Interactive crowd density visualization
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative bg-green-100 rounded-lg p-6 min-h-64">
              {/* Stadium representation */}
              <div className="absolute inset-4 border-2 border-green-600 rounded-lg">
                <div className="absolute inset-2 border border-green-400 rounded-lg bg-green-200">
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-xs font-medium text-green-800">
                    FIELD
                  </div>
                </div>
              </div>

              {/* Zone overlays */}
              <div className="absolute top-2 left-1/2 transform -translate-x-1/2 bg-red-500 bg-opacity-80 text-white text-xs px-2 py-1 rounded">
                Northern (95%)
              </div>
              <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 bg-yellow-500 bg-opacity-80 text-white text-xs px-2 py-1 rounded">
                Southern (95%)
              </div>
              <div className="absolute left-2 top-1/2 transform -translate-y-1/2 rotate-90 bg-green-500 bg-opacity-80 text-white text-xs px-2 py-1 rounded">
                Eastern (85%)
              </div>
              <div className="absolute right-2 top-1/2 transform -translate-y-1/2 -rotate-90 bg-red-500 bg-opacity-80 text-white text-xs px-2 py-1 rounded">
                Western (95%)
              </div>
            </div>

            <div className="mt-4 flex justify-between items-center text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded"></div>
                <span>Low Density</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                <span>Medium Density</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded"></div>
                <span>High Density</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Historical Crowd Data
          </CardTitle>
          <CardDescription>
            Crowd patterns from previous matches
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">47,326</div>
              <div className="text-sm text-gray-600">Average Attendance</div>
              <div className="text-xs text-green-600 mt-1">
                +3.2% vs last season
              </div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">89%</div>
              <div className="text-sm text-gray-600">Average Capacity</div>
              <div className="text-xs text-green-600 mt-1">
                +5.1% vs last season
              </div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">2:45 PM</div>
              <div className="text-sm text-gray-600">Peak Entry Time</div>
              <div className="text-xs text-gray-600 mt-1">
                15 min before bounce
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Safest Zone</p>
              <p className="text-lg font-bold text-green-600 leading-tight">
                {safestZone.zone}
              </p>
              <p className="text-xs text-gray-500">
                {safestZone.density}% full ·{" "}
                {safestZone.current.toLocaleString()} people
              </p>
            </div>
            <Shield className="w-8 h-8 text-green-500" />
          </div>
        </CardContent>
      </Card>
    </>
  );
}
