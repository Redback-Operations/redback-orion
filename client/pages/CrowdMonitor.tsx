import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import MobileNavigation from "@/components/MobileNavigation";
import LiveClock from "@/components/LiveClock";
import {
  Users,
  TrendingUp,
  TrendingDown,
  MapPin,
  AlertTriangle,
  CheckCircle,
  Eye,
  Activity,
  BarChart3,
  Clock,
  Shield,
  Navigation,
  PieChart,
  Timeline,
} from "lucide-react";
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

// Crowd zone data with real-time simulation
const generateCrowdData = () => {
  const zones = [
    {
      id: 1,
      name: "Northern Stand - Lower",
      capacity: 15000,
      current: 13200,
      color: "#ef4444", // red-500
      coordinates: { x: 50, y: 20, width: 40, height: 15 },
      entryPoints: ["Gate A", "Gate B"],
      facilities: ["Toilets", "Food Court", "Merchandise"],
      temperature: 24,
      safety: "normal",
    },
    {
      id: 2,
      name: "Northern Stand - Upper",
      capacity: 8000,
      current: 6800,
      color: "#f97316", // orange-500
      coordinates: { x: 50, y: 10, width: 40, height: 10 },
      entryPoints: ["Gate A-Upper"],
      facilities: ["Toilets", "Bar"],
      temperature: 26,
      safety: "normal",
    },
    {
      id: 3,
      name: "Southern Stand - Lower",
      capacity: 12000,
      current: 11400,
      color: "#dc2626", // red-600
      coordinates: { x: 50, y: 75, width: 40, height: 15 },
      entryPoints: ["Gate C", "Gate D"],
      facilities: ["Toilets", "Food Court", "First Aid"],
      temperature: 23,
      safety: "crowded",
    },
    {
      id: 4,
      name: "Southern Stand - Upper",
      capacity: 6000,
      current: 5700,
      color: "#dc2626", // red-600
      coordinates: { x: 50, y: 90, width: 40, height: 10 },
      entryPoints: ["Gate C-Upper"],
      facilities: ["Premium Bar"],
      temperature: 25,
      safety: "crowded",
    },
    {
      id: 5,
      name: "Eastern Wing",
      capacity: 8000,
      current: 6800,
      color: "#f59e0b", // amber-500
      coordinates: { x: 10, y: 35, width: 15, height: 30 },
      entryPoints: ["Gate E"],
      facilities: ["Toilets", "Snack Bar"],
      temperature: 22,
      safety: "normal",
    },
    {
      id: 6,
      name: "Western Wing",
      capacity: 8000,
      current: 7600,
      color: "#dc2626", // red-600
      coordinates: { x: 75, y: 35, width: 15, height: 30 },
      entryPoints: ["Gate F"],
      facilities: ["Toilets", "Restaurant"],
      temperature: 24,
      safety: "crowded",
    },
    {
      id: 7,
      name: "Premium Seating - North",
      capacity: 2000,
      current: 1850,
      color: "#dc2626", // red-600
      coordinates: { x: 50, y: 35, width: 30, height: 8 },
      entryPoints: ["Premium Entrance"],
      facilities: ["VIP Lounge", "Premium Dining"],
      temperature: 21,
      safety: "normal",
    },
    {
      id: 8,
      name: "Premium Seating - South",
      capacity: 1500,
      current: 1425,
      color: "#dc2626", // red-600
      coordinates: { x: 50, y: 57, width: 30, height: 8 },
      entryPoints: ["Premium Entrance"],
      facilities: ["VIP Lounge", "Premium Bar"],
      temperature: 21,
      safety: "normal",
    },
  ];

  return zones.map((zone) => ({
    ...zone,
    density: Math.round((zone.current / zone.capacity) * 100),
    trend: Math.random() > 0.5 ? "up" : Math.random() > 0.5 ? "down" : "stable",
    waitTime: Math.floor(Math.random() * 15) + 1,
    flow: Math.floor(Math.random() * 50) + 10,
  }));
};

const getDensityColor = (density: number) => {
  if (density >= 95) return "#dc2626"; // red-600 - Critical
  if (density >= 85) return "#f97316"; // orange-500 - High
  if (density >= 70) return "#f59e0b"; // amber-500 - Medium
  if (density >= 50) return "#eab308"; // yellow-500 - Low-Medium
  return "#22c55e"; // green-500 - Low
};

const getDensityLabel = (density: number) => {
  if (density >= 95) return "Critical";
  if (density >= 85) return "High";
  if (density >= 70) return "Medium";
  if (density >= 50) return "Low-Medium";
  return "Low";
};

// Generate historical timeline data
const generateTimelineData = () => {
  const now = new Date();
  const data = [];

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    const baseAttendance = 55000 + Math.sin((i / 24) * Math.PI * 2) * 10000;
    const variation = (Math.random() - 0.5) * 5000;

    data.push({
      time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      totalAttendance: Math.round(baseAttendance + variation),
      averageDensity: Math.round(((baseAttendance + variation) / 60000) * 100),
      criticalZones: Math.floor(Math.random() * 3),
      highDensityZones: Math.floor(Math.random() * 5) + 1,
    });
  }

  return data;
};

export default function CrowdMonitor() {
  const [isLive, setIsLive] = useState(true);
  const [crowdZones, setCrowdZones] = useState(generateCrowdData());
  const [selectedZone, setSelectedZone] = useState(crowdZones[0]);
  const [viewMode, setViewMode] = useState("heatmap");
  const [timeRange, setTimeRange] = useState("live");
  const [timelineData, setTimelineData] = useState(generateTimelineData());

  // Simulate real-time crowd updates
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      setCrowdZones((prevZones) =>
        prevZones.map((zone) => {
          const change = (Math.random() - 0.5) * 100;
          const newCurrent = Math.max(
            0,
            Math.min(zone.capacity, zone.current + change),
          );
          return {
            ...zone,
            current: Math.round(newCurrent),
            density: Math.round((newCurrent / zone.capacity) * 100),
            color: getDensityColor(
              Math.round((newCurrent / zone.capacity) * 100),
            ),
            flow: Math.floor(Math.random() * 50) + 10,
            waitTime: Math.floor(Math.random() * 15) + 1,
          };
        }),
      );

      // Update timeline data
      setTimelineData(prevData => {
        const newEntry = {
          time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          totalAttendance: prevData[prevData.length - 1]?.totalAttendance + (Math.random() - 0.5) * 500 || 55000,
          averageDensity: 0,
          criticalZones: 0,
          highDensityZones: 0,
        };

        // Calculate current metrics
        const total = crowdZones.reduce((sum, zone) => sum + zone.current, 0);
        const capacity = crowdZones.reduce((sum, zone) => sum + zone.capacity, 0);
        newEntry.totalAttendance = total;
        newEntry.averageDensity = Math.round((total / capacity) * 100);
        newEntry.criticalZones = crowdZones.filter(zone => zone.density >= 95).length;
        newEntry.highDensityZones = crowdZones.filter(zone => zone.density >= 85 && zone.density < 95).length;

        return [...prevData.slice(-23), newEntry];
      });
    }, 3000);

    return () => clearInterval(interval);
  }, [isLive, crowdZones]);

  const totalCapacity = crowdZones.reduce(
    (sum, zone) => sum + zone.capacity,
    0,
  );
  const totalCurrent = crowdZones.reduce((sum, zone) => sum + zone.current, 0);
  const averageDensity = Math.round((totalCurrent / totalCapacity) * 100);

  const criticalZones = crowdZones.filter((zone) => zone.density >= 95);
  const highDensityZones = crowdZones.filter(
    (zone) => zone.density >= 85 && zone.density < 95,
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <MobileNavigation />

      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-4">
          {/* Live Clock */}
          <LiveClock
            isLive={isLive}
            onToggleLive={setIsLive}
            matchTime={{ quarter: 2, timeRemaining: "15:23" }}
          />

          {/* Overview Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Attendance</p>
                    <p className="text-2xl font-bold">
                      {totalCurrent.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">
                      of {totalCapacity.toLocaleString()}
                    </p>
                  </div>
                  <Users className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Average Density</p>
                    <p className="text-2xl font-bold">{averageDensity}%</p>
                    <p className="text-xs text-gray-500">
                      {getDensityLabel(averageDensity)}
                    </p>
                  </div>
                  <Activity className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Critical Zones</p>
                    <p className="text-2xl font-bold text-red-600">
                      {criticalZones.length}
                    </p>
                    <p className="text-xs text-gray-500">95%+ capacity</p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">High Density</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {highDensityZones.length}
                    </p>
                    <p className="text-xs text-gray-500">85-94% capacity</p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Controls */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Select value={viewMode} onValueChange={setViewMode}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="heatmap">Heat Map View</SelectItem>
                <SelectItem value="list">List View</SelectItem>
                <SelectItem value="analytics">Analytics View</SelectItem>
              </SelectContent>
            </Select>

            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="live">Live Data</SelectItem>
                <SelectItem value="1hour">Last Hour</SelectItem>
                <SelectItem value="4hours">Last 4 Hours</SelectItem>
                <SelectItem value="today">Today</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Tabs value={viewMode} onValueChange={setViewMode} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="heatmap">Heat Map</TabsTrigger>
              <TabsTrigger value="list">Zone Details</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
            </TabsList>

            <TabsContent value="heatmap" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-5 h-5" />
                    Stadium Crowd Heat Map
                  </CardTitle>
                  <CardDescription>
                    Real-time crowd density across all stadium zones
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Stadium Heat Map */}
                  <div className="relative bg-green-100 rounded-lg p-4 min-h-80 overflow-hidden">
                    {/* Field */}
                    <div className="absolute inset-8 border-2 border-green-600 rounded-lg bg-green-200">
                      <div className="absolute inset-2 border border-green-400 rounded-lg">
                        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-sm font-medium text-green-800">
                          AFL FIELD
                        </div>
                        {/* Center Circle */}
                        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 border-2 border-green-600 rounded-full"></div>
                      </div>
                    </div>

                    {/* Zone overlays */}
                    {crowdZones.map((zone) => (
                      <button
                        key={zone.id}
                        onClick={() => setSelectedZone(zone)}
                        className={`absolute transition-all duration-300 hover:opacity-80 border-2 ${
                          selectedZone.id === zone.id
                            ? "border-white border-4"
                            : "border-transparent"
                        }`}
                        style={{
                          left: `${zone.coordinates.x}%`,
                          top: `${zone.coordinates.y}%`,
                          width: `${zone.coordinates.width}%`,
                          height: `${zone.coordinates.height}%`,
                          backgroundColor: zone.color,
                          opacity: (zone.density / 100) * 0.8 + 0.2,
                        }}
                      >
                        <div className="text-white text-xs font-medium p-1 text-center">
                          <div className="truncate">
                            {zone.name.split(" - ")[0]}
                          </div>
                          <div>{zone.density}%</div>
                        </div>
                      </button>
                    ))}
                  </div>

                  {/* Legend */}
                  <div className="flex flex-wrap justify-center gap-4 mt-4 text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-green-500 rounded"></div>
                      <span>Low (0-49%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-yellow-500 rounded"></div>
                      <span>Low-Med (50-69%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-amber-500 rounded"></div>
                      <span>Medium (70-84%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-orange-500 rounded"></div>
                      <span>High (85-94%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-red-600 rounded"></div>
                      <span>Critical (95%+)</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Selected Zone Details */}
              <Card>
                <CardHeader>
                  <CardTitle>{selectedZone.name}</CardTitle>
                  <CardDescription className="flex items-center gap-4">
                    <Badge
                      variant={
                        selectedZone.density >= 95
                          ? "destructive"
                          : selectedZone.density >= 85
                            ? "secondary"
                            : "default"
                      }
                    >
                      {getDensityLabel(selectedZone.density)}
                    </Badge>
                    <span>
                      {selectedZone.current.toLocaleString()} /{" "}
                      {selectedZone.capacity.toLocaleString()}
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Capacity</span>
                          <span>{selectedZone.density}%</span>
                        </div>
                        <Progress
                          value={selectedZone.density}
                          className="h-3"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="p-2 bg-gray-50 rounded">
                          <div className="font-medium">
                            {selectedZone.waitTime}min
                          </div>
                          <div className="text-gray-600">Wait Time</div>
                        </div>
                        <div className="p-2 bg-gray-50 rounded">
                          <div className="font-medium">
                            {selectedZone.flow}/min
                          </div>
                          <div className="text-gray-600">Flow Rate</div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <h5 className="font-medium text-sm">Entry Points</h5>
                      {selectedZone.entryPoints.map((entry, index) => (
                        <div key={index} className="text-sm text-gray-600">
                          {entry}
                        </div>
                      ))}
                    </div>

                    <div className="space-y-2">
                      <h5 className="font-medium text-sm">Facilities</h5>
                      {selectedZone.facilities.map((facility, index) => (
                        <div key={index} className="text-sm text-gray-600">
                          {facility}
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="list" className="space-y-4">
              <div className="space-y-3">
                {crowdZones.map((zone) => (
                  <Card
                    key={zone.id}
                    className={`cursor-pointer transition-colors ${
                      selectedZone.id === zone.id ? "ring-2 ring-blue-500" : ""
                    }`}
                    onClick={() => setSelectedZone(zone)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-medium">{zone.name}</h4>
                          <p className="text-sm text-gray-600">
                            {zone.current.toLocaleString()} /{" "}
                            {zone.capacity.toLocaleString()} people
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={
                              zone.density >= 95
                                ? "destructive"
                                : zone.density >= 85
                                  ? "secondary"
                                  : "default"
                            }
                          >
                            {getDensityLabel(zone.density)}
                          </Badge>
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

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm mb-1">
                          <span>Density</span>
                          <span>{zone.density}%</span>
                        </div>
                        <Progress value={zone.density} className="h-2" />
                      </div>

                      <div className="grid grid-cols-3 gap-2 mt-3 text-sm">
                        <div className="text-center p-2 bg-gray-50 rounded">
                          <div className="font-medium">{zone.waitTime}min</div>
                          <div className="text-gray-600">Wait</div>
                        </div>
                        <div className="text-center p-2 bg-gray-50 rounded">
                          <div className="font-medium">{zone.flow}/min</div>
                          <div className="text-gray-600">Flow</div>
                        </div>
                        <div className="text-center p-2 bg-gray-50 rounded">
                          <div className="font-medium">
                            {zone.temperature}°C
                          </div>
                          <div className="text-gray-600">Temp</div>
                        </div>
                      </div>

                      {zone.safety === "crowded" && (
                        <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-orange-500" />
                          <span className="text-sm text-orange-700">
                            High density - monitor closely
                          </span>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="analytics" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Density Distribution
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {["Low", "Low-Medium", "Medium", "High", "Critical"].map(
                        (level, index) => {
                          const ranges = [
                            { min: 0, max: 49, color: "bg-green-500" },
                            { min: 50, max: 69, color: "bg-yellow-500" },
                            { min: 70, max: 84, color: "bg-amber-500" },
                            { min: 85, max: 94, color: "bg-orange-500" },
                            { min: 95, max: 100, color: "bg-red-600" },
                          ];
                          const range = ranges[index];
                          const zonesInRange = crowdZones.filter(
                            (zone) =>
                              zone.density >= range.min &&
                              zone.density <= range.max,
                          ).length;
                          const percentage =
                            (zonesInRange / crowdZones.length) * 100;

                          return (
                            <div key={level} className="space-y-1">
                              <div className="flex justify-between text-sm">
                                <span>
                                  {level} ({range.min}-{range.max}%)
                                </span>
                                <span>{zonesInRange} zones</span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full ${range.color}`}
                                  style={{ width: `${percentage}%` }}
                                />
                              </div>
                            </div>
                          );
                        },
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="w-5 h-5" />
                      Wait Times & Flow
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h5 className="text-sm font-medium mb-2">
                          Average Wait Times
                        </h5>
                        <div className="text-2xl font-bold">
                          {Math.round(
                            crowdZones.reduce(
                              (sum, zone) => sum + zone.waitTime,
                              0,
                            ) / crowdZones.length,
                          )}{" "}
                          min
                        </div>
                        <p className="text-sm text-gray-600">
                          Across all zones
                        </p>
                      </div>

                      <div>
                        <h5 className="text-sm font-medium mb-2">
                          Total Flow Rate
                        </h5>
                        <div className="text-2xl font-bold">
                          {crowdZones.reduce((sum, zone) => sum + zone.flow, 0)}{" "}
                          people/min
                        </div>
                        <p className="text-sm text-gray-600">
                          Combined entry/exit rate
                        </p>
                      </div>

                      <div>
                        <h5 className="text-sm font-medium mb-2">
                          Zones by Wait Time
                        </h5>
                        <div className="space-y-2">
                          {crowdZones
                            .sort((a, b) => b.waitTime - a.waitTime)
                            .slice(0, 3)
                            .map((zone, index) => (
                              <div
                                key={zone.id}
                                className="flex justify-between items-center p-2 bg-gray-50 rounded"
                              >
                                <span className="text-sm truncate">
                                  {zone.name}
                                </span>
                                <Badge variant="outline">
                                  {zone.waitTime}min
                                </Badge>
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Safety Alerts */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5" />
                    Safety & Alerts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {criticalZones.length > 0 && (
                      <div className="p-3 bg-red-50 border border-red-200 rounded">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertTriangle className="w-5 h-5 text-red-500" />
                          <span className="font-medium text-red-700">
                            Critical Density Alert
                          </span>
                        </div>
                        <p className="text-sm text-red-600 mb-2">
                          {criticalZones.length} zone(s) at 95%+ capacity:
                        </p>
                        <div className="space-y-1">
                          {criticalZones.map((zone) => (
                            <div key={zone.id} className="text-sm">
                              • {zone.name} ({zone.density}%)
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {highDensityZones.length > 0 && (
                      <div className="p-3 bg-orange-50 border border-orange-200 rounded">
                        <div className="flex items-center gap-2 mb-2">
                          <Eye className="w-5 h-5 text-orange-500" />
                          <span className="font-medium text-orange-700">
                            High Density Warning
                          </span>
                        </div>
                        <p className="text-sm text-orange-600">
                          {highDensityZones.length} zone(s) require monitoring
                          (85-94% capacity)
                        </p>
                      </div>
                    )}

                    {criticalZones.length === 0 &&
                      highDensityZones.length === 0 && (
                        <div className="p-3 bg-green-50 border border-green-200 rounded">
                          <div className="flex items-center gap-2">
                            <CheckCircle className="w-5 h-5 text-green-500" />
                            <span className="font-medium text-green-700">
                              All zones operating normally
                            </span>
                          </div>
                          <p className="text-sm text-green-600">
                            No immediate safety concerns detected
                          </p>
                        </div>
                      )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
