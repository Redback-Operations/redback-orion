import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import MobileNavigation from "@/components/MobileNavigation";

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <MobileNavigation />

      <div className="lg:ml-64 p-6 space-y-6 max-w-5xl">
        {/* Title */}
        <h1 className="text-3xl font-bold">About the Project</h1>

        {/* Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Project Overview</CardTitle>
          </CardHeader>
          <CardContent className="text-gray-600 leading-relaxed space-y-3">
            <p>
              Project 4, RedBack Orion is one of our company's initiatives aimed
              at redefining sports engagement.
            </p>
            <p>
              The system focuses on building an intelligent, real-time tracking
              platform for athletes across multiple sports—especially AFL
              (Footy), one of Australia’s most popular sports.
            </p>
            <p>
              It tracks player performance live while also monitoring crowd
              density in stadiums to ensure audience safety during peak times.
            </p>
          </CardContent>
        </Card>

          {/* Features */}
          <Card>
            <CardHeader>
              <CardTitle>Features</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6 text-gray-700">
              
          {/* Player Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Player Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                <li>Live stats: active players, goals, efficiency, disposals</li>
                <li>Player info: name, age, team, position</li>
                <li>Detailed stats: kicks, handballs, tackles</li>
                <li>Performance ratings</li>
                <li>Heatmaps and analytics</li>
                <li>Player comparison</li>
              </ul>
            </CardContent>
          </Card>

          {/* Crowd Monitoring */}
          <Card>
            <CardHeader>
              <CardTitle>Crowd Monitoring</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                <li>Total attendance and density tracking</li>
                <li>Real-time stadium heatmap</li>
                <li>Zone analytics (capacity, flow)</li>
                <li>Wait times and movement</li>
                <li>Safety alerts and risk detection</li>
              </ul>
            </CardContent>
          </Card>

          {/* Analytics */}
          <Card>
            <CardHeader>
              <CardTitle>Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                <li>Upload AFL or crowd footage</li>
                <li>Automated video analysis</li>
                <li>Generated reports</li>
                <li>Processing queue tracking</li>
              </ul>
            </CardContent>
          </Card>

          {/* Reports */}
          <Card>
            <CardHeader>
              <CardTitle>Reports</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                <li>Download reports</li>
                <li>Quick report generation</li>
                <li>Custom report builder</li>
              </ul>
            </CardContent>
          </Card>

          {/* API Diagnostics */}
          <Card>
            <CardHeader>
              <CardTitle>API Diagnostics</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600">
                Monitor system performance and debug API interactions in real-time.
              </p>
            </CardContent>
          </Card>

            </CardContent>
          </Card>
        </div>
      </div>
    );
  }