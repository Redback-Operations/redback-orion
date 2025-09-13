import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { FileText, Users, Download } from "lucide-react";
import { downloadText } from "@/lib/download";

export default function ReportsPanel() {
  const recentReports = [
    { name: "Weekly Player Performance - Round 15", date: "2024-01-15", size: "2.4 MB", format: "PDF" },
    { name: "Crowd Density Analysis - MCG", date: "2024-01-14", size: "1.8 MB", format: "Excel" },
    { name: "Season Summary Report", date: "2024-01-12", size: "5.2 MB", format: "PDF" },
    { name: "Player Comparison - Top 50", date: "2024-01-10", size: "3.1 MB", format: "Excel" },
  ];

  const handleDownloadRecent = (report: (typeof recentReports)[number]) => {
    const content = `AFL Analytics Report: ${report.name}\n\nGenerated: ${report.date}\nFormat: ${report.format}\nSize: ${report.size}\n\nThis is a sample report from AFL Analytics Platform.\nReport details and analysis data would be included here in a real implementation.\n\nGenerated on: ${new Date().toLocaleString()}\n`;
    downloadText(content, `${report.name.replace(/[^a-z0-9]/gi, "_")}_${Date.now()}`);
  };

  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Player Performance Reports
            </CardTitle>
            <CardDescription>Generate detailed analytics reports for players and teams</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium">Report Type</label>
                <Select defaultValue="individual">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="individual">Individual Player Report</SelectItem>
                    <SelectItem value="team">Team Performance Report</SelectItem>
                    <SelectItem value="comparison">Player Comparison Report</SelectItem>
                    <SelectItem value="season">Season Summary Report</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Date Range</label>
                <Select defaultValue="last7">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="last7">Last 7 days</SelectItem>
                    <SelectItem value="last30">Last 30 days</SelectItem>
                    <SelectItem value="season">Current Season</SelectItem>
                    <SelectItem value="custom">Custom Range</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Format</label>
                <Select defaultValue="pdf">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pdf">PDF Report</SelectItem>
                    <SelectItem value="excel">Excel Spreadsheet</SelectItem>
                    <SelectItem value="csv">CSV Data</SelectItem>
                    <SelectItem value="json">JSON Data</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Separator />

            <div className="space-y-3">
              <h4 className="font-medium">Include Sections</h4>
              <div className="space-y-2">
                {["Performance Statistics", "Match Highlights", "Trend Analysis", "Comparison Charts", "Heat Maps"].map(
                  (section) => (
                    <label key={section} className="flex items-center space-x-2">
                      <input type="checkbox" defaultChecked className="rounded" />
                      <span className="text-sm">{section}</span>
                    </label>
                  ),
                )}
              </div>
            </div>

            <Button className="w-full bg-gradient-to-r from-purple-600 to-orange-600">
              <Download className="w-4 h-4 mr-2" />
              Generate Report
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              Crowd Analytics Reports
            </CardTitle>
            <CardDescription>Generate crowd movement and density reports</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium">Report Type</label>
                <Select defaultValue="density">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="density">Crowd Density Report</SelectItem>
                    <SelectItem value="movement">Movement Pattern Report</SelectItem>
                    <SelectItem value="capacity">Capacity Utilization Report</SelectItem>
                    <SelectItem value="safety">Safety Analytics Report</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Time Period</label>
                <Select defaultValue="match">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="match">Current Match</SelectItem>
                    <SelectItem value="gameday">Full Game Day</SelectItem>
                    <SelectItem value="season">Season Analysis</SelectItem>
                    <SelectItem value="custom">Custom Period</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Zone Focus</label>
                <Select defaultValue="all">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Zones</SelectItem>
                    <SelectItem value="northern">Northern Stand</SelectItem>
                    <SelectItem value="southern">Southern Stand</SelectItem>
                    <SelectItem value="eastern">Eastern Wing</SelectItem>
                    <SelectItem value="western">Western Wing</SelectItem>
                    <SelectItem value="premium">Premium Seating</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Separator />

            <div className="space-y-3">
              <h4 className="font-medium">Analytics Features</h4>
              <div className="space-y-2">
                {["Heat Map Visualization", "Peak Hour Analysis", "Entry/Exit Patterns", "Safety Compliance", "Revenue Optimization"].map(
                  (feature) => (
                    <label key={feature} className="flex items-center space-x-2">
                      <input type="checkbox" defaultChecked className="rounded" />
                      <span className="text-sm">{feature}</span>
                    </label>
                  ),
                )}
              </div>
            </div>

            <Button className="w-full bg-gradient-to-r from-purple-600 to-orange-600">
              <Download className="w-4 h-4 mr-2" />
              Generate Crowd Report
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Reports</CardTitle>
          <CardDescription>Download previously generated reports</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentReports.map((report, i) => (
              <div key={i} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                <div className="flex-1">
                  <div className="font-medium">{report.name}</div>
                  <div className="text-sm text-gray-600">
                    {report.date} • {report.size} • {report.format}
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={() => handleDownloadRecent(report)}>
                  <Download className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
