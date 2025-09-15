import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Download, FileText, Calendar, Filter, Search, Clock, CheckCircle, AlertCircle } from "lucide-react";
import ReportsPanel from "../ReportsPanel";

export default function ReportsTab() {
  // Mock data for reports
  const reports = [
    {
      id: '1',
      name: 'Player Performance Report - Round 12',
      type: 'player_performance',
      format: 'pdf',
      status: 'completed',
      createdAt: '2025-01-15T10:30:00Z',
      downloadUrl: '#',
      size: '2.4 MB'
    },
    {
      id: '2',
      name: 'Team Analysis - Western Bulldogs vs Richmond',
      type: 'team_analysis',
      format: 'excel',
      status: 'completed',
      createdAt: '2025-01-14T15:45:00Z',
      downloadUrl: '#',
      size: '1.8 MB'
    },
    {
      id: '3',
      name: 'Video Analysis Report - Match Highlights',
      type: 'video_analysis',
      format: 'pdf',
      status: 'generating',
      createdAt: '2025-01-15T14:20:00Z',
      progress: 65,
      size: '3.2 MB'
    },
    {
      id: '4',
      name: 'Crowd Monitoring Summary - MCG',
      type: 'crowd_analysis',
      format: 'csv',
      status: 'completed',
      createdAt: '2025-01-13T09:15:00Z',
      downloadUrl: '#',
      size: '856 KB'
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'generating':
        return <Clock className="w-4 h-4 text-blue-600" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'generating':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'failed':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Download className="w-6 h-6" />
            Reports & Analytics
          </h2>
          <p className="text-gray-600">Generate and download comprehensive analysis reports</p>
        </div>
        <Button className="bg-gradient-to-r from-purple-600 to-orange-600">
          <FileText className="w-4 h-4 mr-2" />
          Generate New Report
        </Button>
      </div>

      {/* Report Generation Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Generate New Report
          </CardTitle>
          <CardDescription>
            Create custom reports with your preferred filters and format
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Report Type</label>
              <Select defaultValue="player_performance">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="player_performance">Player Performance</SelectItem>
                  <SelectItem value="team_analysis">Team Analysis</SelectItem>
                  <SelectItem value="match_summary">Match Summary</SelectItem>
                  <SelectItem value="video_analysis">Video Analysis</SelectItem>
                  <SelectItem value="crowd_analysis">Crowd Analysis</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Format</label>
              <Select defaultValue="pdf">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pdf">PDF</SelectItem>
                  <SelectItem value="excel">Excel</SelectItem>
                  <SelectItem value="csv">CSV</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Date Range</label>
              <Select defaultValue="last_week">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="last_week">Last Week</SelectItem>
                  <SelectItem value="last_month">Last Month</SelectItem>
                  <SelectItem value="last_quarter">Last Quarter</SelectItem>
                  <SelectItem value="custom">Custom Range</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-end">
              <Button className="w-full">
                <FileText className="w-4 h-4 mr-2" />
                Generate
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reports List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Download className="w-5 h-5" />
                Recent Reports
              </CardTitle>
              <CardDescription>
                Your generated reports and analysis documents
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input placeholder="Search reports..." className="pl-10 w-64" />
              </div>
              <Select defaultValue="all">
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="player_performance">Player</SelectItem>
                  <SelectItem value="team_analysis">Team</SelectItem>
                  <SelectItem value="video_analysis">Video</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {reports.map((report) => (
              <div key={report.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(report.status)}
                    <div>
                      <h4 className="font-medium text-gray-900">{report.name}</h4>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(report.createdAt).toLocaleDateString()}
                        </span>
                        <span>{report.size}</span>
                        <Badge variant="outline" className="text-xs">
                          {report.format.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant="outline" className={getStatusColor(report.status)}>
                    {report.status === 'generating' ? 'Generating...' : 
                     report.status === 'completed' ? 'Ready' : 
                     report.status === 'failed' ? 'Failed' : report.status}
                  </Badge>
                  {report.status === 'generating' && (
                    <div className="w-24">
                      <Progress value={report.progress} className="h-2" />
                    </div>
                  )}
                  {report.status === 'completed' && (
                    <Button variant="outline" size="sm">
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </Button>
                  )}
                  {report.status === 'failed' && (
                    <Button variant="outline" size="sm">
                      Retry
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Report Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Quick Report Templates
          </CardTitle>
          <CardDescription>
            Pre-configured report templates for common analysis needs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-medium">Weekly Player Report</h4>
                  <p className="text-sm text-gray-500">Individual performance summary</p>
                </div>
              </div>
              <Button variant="outline" size="sm" className="w-full">
                Generate
              </Button>
            </div>

            <div className="p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <Download className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h4 className="font-medium">Match Analysis</h4>
                  <p className="text-sm text-gray-500">Complete match breakdown</p>
                </div>
              </div>
              <Button variant="outline" size="sm" className="w-full">
                Generate
              </Button>
            </div>

            <div className="p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Calendar className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-medium">Season Summary</h4>
                  <p className="text-sm text-gray-500">Full season statistics</p>
                </div>
              </div>
              <Button variant="outline" size="sm" className="w-full">
                Generate
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reports Panel Component */}
      <ReportsPanel />
    </div>
  );
}
