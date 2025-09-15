import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Users, MapPin, AlertTriangle, TrendingUp, Eye, Shield } from "lucide-react";
import { generateTimelineFromStadiumData, getStaticAFLCrowdZones } from "@/lib/crowd";

export default function CrowdMonitorTab() {
  // Get crowd zones data
  const crowdZones = getStaticAFLCrowdZones();
  
  // Mock crowd data - this should come from the backend
  const crowdData = {
    totalAttendance: 45230,
    capacity: 50000,
    occupancyRate: 90.5,
    safetyStatus: 'safe' as const,
    alerts: [
      {
        id: '1',
        type: 'density',
        severity: 'low',
        message: 'High density in Zone A - North Stand',
        zoneId: 'zone-a',
        timestamp: new Date().toISOString(),
      }
    ],
    zones: crowdZones.map(zone => ({
      ...zone,
      density: Math.floor(Math.random() * 100),
      capacity: Math.floor(Math.random() * 5000) + 2000,
      occupancy: Math.floor(Math.random() * 100),
      status: Math.random() > 0.8 ? 'warning' : 'safe' as const,
    }))
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'safe': return 'Safe';
      case 'warning': return 'Warning';
      case 'critical': return 'Critical';
      default: return 'Unknown';
    }
  };

  // Mock stadium zones data matching the image
  const stadiumZones = [
    { name: "Northern Stand", current: 14250, capacity: 15000, percentage: 95 },
    { name: "Southern Stand", current: 10800, capacity: 12000, percentage: 90 },
    { name: "Eastern Wing", current: 3200, capacity: 8000, percentage: 40 },
    { name: "Western Wing", current: 7200, capacity: 8000, percentage: 90 },
    { name: "Northeast Corner", current: 2750, capacity: 5000, percentage: 55 },
    { name: "Northwest Corner", current: 4750, capacity: 5000, percentage: 95 },
    { name: "Southeast Corner", current: 3750, capacity: 5000, percentage: 75 },
    { name: "Southwest Corner", current: 1500, capacity: 5000, percentage: 30 },
  ];

  const totalAttendance = stadiumZones.reduce((sum, zone) => sum + zone.current, 0);
  const totalCapacity = stadiumZones.reduce((sum, zone) => sum + zone.capacity, 0);
  const avgDensity = Math.round((totalAttendance / totalCapacity) * 100);
  const criticalZones = stadiumZones.filter(zone => zone.percentage >= 95).length;

  const getZoneColor = (percentage: number) => {
    if (percentage >= 95) return "bg-red-500";
    if (percentage >= 85) return "bg-orange-500";
    if (percentage >= 50) return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="w-6 h-6" />
            Crowd Monitor
          </h2>
          <p className="text-gray-600">Real-time stadium crowd analytics and safety monitoring</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
            <Eye className="w-3 h-3 mr-1" />
            LIVE
          </Badge>
        </div>
      </div>

      {/* Main Content Grid - Stadium Zone Density and Visual Map */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stadium Zone Density */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              Stadium Zone Density
            </CardTitle>
            <CardDescription>Real-time crowd distribution across stadium zones</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {stadiumZones.map((zone) => (
              <div key={zone.name} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">{zone.name}</span>
                  <span className="text-gray-600">{zone.current.toLocaleString()} / {zone.capacity.toLocaleString()}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className={`h-3 rounded-full ${getZoneColor(zone.percentage)}`}
                    style={{ width: `${zone.percentage}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500">{zone.percentage}% capacity</div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Visual Stadium Map */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              Visual Stadium Map
            </CardTitle>
            <CardDescription>Interactive crowd density visualization</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Stadium Map Visualization */}
              <div className="relative w-full h-64 bg-gray-100 rounded-lg border-2 border-gray-300 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-700 mb-2">AFL GROUND</div>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    {stadiumZones.map((zone) => (
                      <div 
                        key={zone.name}
                        className={`p-2 rounded text-white font-medium ${getZoneColor(zone.percentage)}`}
                      >
                        <div className="font-bold">{zone.name.split(' ')[0]}</div>
                        <div>{zone.percentage}%</div>
                        <div>{zone.current.toLocaleString()}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Legend */}
              <div className="space-y-2">
                <h4 className="text-sm font-semibold">Density Legend:</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded"></div>
                    <span>Low (0-49%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                    <span>Medium (50-84%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-orange-500 rounded"></div>
                    <span>High (85-94%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-500 rounded"></div>
                    <span>Critical (95%+)</span>
                  </div>
                </div>
              </div>

              {/* Summary Stats */}
              <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{totalAttendance.toLocaleString()}</div>
                  <div className="text-xs text-gray-500">Total Attendance</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{avgDensity}%</div>
                  <div className="text-xs text-gray-500">Avg Density</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{criticalZones}</div>
                  <div className="text-xs text-gray-500">Critical Zones</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Historical Crowd Data */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Historical Crowd Data
          </CardTitle>
          <CardDescription>Crowd patterns from previous matches</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-blue-50 rounded-lg">
              <div className="text-3xl font-bold text-blue-600 mb-2">{totalAttendance.toLocaleString()}</div>
              <div className="text-sm font-medium text-gray-700 mb-1">Current Attendance</div>
              <div className="text-xs text-blue-600 underline cursor-pointer">Live Stadium Data</div>
            </div>
            <div className="text-center p-6 bg-green-50 rounded-lg">
              <div className="text-3xl font-bold text-green-600 mb-2">{avgDensity}%</div>
              <div className="text-sm font-medium text-gray-700 mb-1">Average Density</div>
              <div className="text-xs text-green-600 underline cursor-pointer">Across 8 zones</div>
            </div>
            <div className="text-center p-6 bg-purple-50 rounded-lg">
              <div className="text-3xl font-bold text-purple-600 mb-2">{totalCapacity.toLocaleString()}</div>
              <div className="text-sm font-medium text-gray-700 mb-1">Total Capacity</div>
              <div className="text-xs text-purple-600 underline cursor-pointer">Stadium Maximum</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Stadium Map Placeholder */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Stadium Overview
                </CardTitle>
                <CardDescription>
                  Real-time crowd density visualization
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">Interactive stadium map</p>
                    <p className="text-sm text-gray-400">Coming soon</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Recent Activity
                </CardTitle>
                <CardDescription>
                  Latest crowd movement and alerts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {crowdData.alerts.map((alert) => (
                    <div key={alert.id} className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg">
                      <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Density Distribution Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Density Distribution Pie Chart
                </CardTitle>
                <CardDescription>Visual breakdown of zones by density levels</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Pie Chart Placeholder */}
                  <div className="h-64 flex items-center justify-center">
                    <div className="relative w-48 h-48">
                      {/* Donut Chart */}
                      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                        {/* Low Density - Green (2 zones) */}
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="#10b981"
                          strokeWidth="8"
                          strokeDasharray="62.83 188.5"
                          strokeDashoffset="0"
                        />
                        {/* Medium Density - Orange (2 zones) */}
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="#f59e0b"
                          strokeWidth="8"
                          strokeDasharray="62.83 188.5"
                          strokeDashoffset="-62.83"
                        />
                        {/* High Density - Yellow (2 zones) */}
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="#eab308"
                          strokeWidth="8"
                          strokeDasharray="62.83 188.5"
                          strokeDashoffset="-125.66"
                        />
                        {/* Critical Density - Red (2 zones) */}
                        <circle
                          cx="50"
                          cy="50"
                          r="40"
                          fill="none"
                          stroke="#ef4444"
                          strokeWidth="8"
                          strokeDasharray="62.83 188.5"
                          strokeDashoffset="-188.49"
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-gray-700">8</div>
                          <div className="text-xs text-gray-500">Total Zones</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Legend */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span className="text-sm">Low (0-49%) - 2 zones (25%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                      <span className="text-sm">Medium (50-84%) - 2 zones (25%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                      <span className="text-sm">High (85-94%) - 2 zones (25%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                      <span className="text-sm">Critical (95%+) - 2 zones (25%)</span>
                    </div>
                  </div>

                  {/* Summary Stats */}
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-900">8</div>
                      <div className="text-xs text-gray-500">Total Zones</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-green-600">4</div>
                      <div className="text-xs text-gray-500">Safe Zones</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-yellow-600">2</div>
                      <div className="text-xs text-gray-500">Alert Zones</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-red-600">2</div>
                      <div className="text-xs text-gray-500">Critical Zones</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Zone Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Zone Analysis
                </CardTitle>
                <CardDescription>Detailed breakdown of each stadium zone</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {stadiumZones.map((zone, index) => {
                    const getStatus = (percentage: number) => {
                      if (percentage >= 95) return { text: "Critical", color: "text-red-600" };
                      if (percentage >= 85) return { text: "High", color: "text-yellow-600" };
                      if (percentage >= 50) return { text: "Medium", color: "text-orange-600" };
                      return { text: "Low", color: "text-green-600" };
                    };
                    const status = getStatus(zone.percentage);
                    
                    return (
                      <div key={index} className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="font-medium text-sm">{zone.name}</span>
                          <span className={`text-xs font-medium ${status.color}`}>{status.text}</span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-600 mb-1">
                          <span>{zone.current.toLocaleString()} / {zone.capacity.toLocaleString()}</span>
                          <span>({zone.percentage}%)</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getZoneColor(zone.percentage)}`}
                            style={{ width: `${zone.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="timeline" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Crowd Density Timeline
              </CardTitle>
              <CardDescription>
                Historical crowd data and density trends over time
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Timeline Chart Placeholder */}
                <div className="h-80 bg-gray-50 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
                  <div className="text-center">
                    <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">Crowd Density Timeline Chart</p>
                    <p className="text-sm text-gray-400">Attendance and density trends from 12:00 to 18:00</p>
                    <div className="mt-4 flex justify-center gap-4 text-xs">
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-2 bg-blue-500"></div>
                        <span>Total Attendance</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-2 bg-green-500"></div>
                        <span>Average Density %</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-2 bg-orange-500"></div>
                        <span>Critical Zones</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <div className="w-3 h-2 bg-red-500"></div>
                        <span>High Density Zones</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Data Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Peak Hours Card */}
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">Peak Hours</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">16:00</span>
                        <div className="text-right">
                          <div className="text-sm font-bold">48,200</div>
                          <div className="text-xs text-gray-500">(71% density)</div>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">17:00</span>
                        <div className="text-right">
                          <div className="text-sm font-bold">45,790</div>
                          <div className="text-xs text-gray-500">(67% density)</div>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">15:00</span>
                        <div className="text-right">
                          <div className="text-sm font-bold">43,380</div>
                          <div className="text-xs text-gray-500">(64% density)</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Density Trends Card */}
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">Density Trends</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">71%</div>
                        <div className="text-sm text-gray-600">Current Average Density</div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Critical Zones</span>
                        <span className="text-lg font-bold text-red-600">2</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">High Density Zones</span>
                        <span className="text-lg font-bold text-orange-600">2</span>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Capacity Insights Card */}
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">Capacity Insights</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">77%</div>
                        <div className="text-sm text-gray-600">Current Stadium Fill</div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Current Attendance</span>
                        <span className="text-lg font-bold text-gray-900">48,200</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Available Capacity</span>
                        <span className="text-lg font-bold text-green-600">14,800</span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
