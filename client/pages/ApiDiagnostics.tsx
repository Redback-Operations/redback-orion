import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import MobileNavigation from "@/components/MobileNavigation";
import LiveClock from "@/components/LiveClock";
import {
  Activity,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Server,
  Database,
  Globe,
  Shield,
  Monitor,
  Terminal,
  Play,
  Pause,
  RotateCcw,
  Download,
  Upload,
  Wifi,
  WifiOff,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Settings,
  Eye,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";

// Mock API endpoints and their status
const generateApiStatus = () => [
  {
    id: 1,
    name: "Player Performance API",
    endpoint: "/api/v1/players/performance",
    status: "healthy",
    responseTime: 145,
    uptime: 99.8,
    lastCheck: "2 min ago",
    version: "v1.2.3",
    description: "Real-time player statistics and metrics",
  },
  {
    id: 2,
    name: "Crowd Monitoring API",
    endpoint: "/api/v1/crowd/monitor",
    status: "healthy",
    responseTime: 89,
    uptime: 99.9,
    lastCheck: "1 min ago",
    version: "v1.1.8",
    description: "Stadium crowd density and safety data",
  },
  {
    id: 3,
    name: "Video Analysis API",
    endpoint: "/api/v1/video/analyze",
    status: "warning",
    responseTime: 2340,
    uptime: 98.2,
    lastCheck: "5 min ago",
    version: "v2.0.1",
    description: "AI-powered video processing and analysis",
  },
  {
    id: 4,
    name: "Match Data API",
    endpoint: "/api/v1/matches/live",
    status: "healthy",
    responseTime: 67,
    uptime: 99.7,
    lastCheck: "30 sec ago",
    version: "v1.4.2",
    description: "Live match data and statistics",
  },
  {
    id: 5,
    name: "Report Generation API",
    endpoint: "/api/v1/reports/generate",
    status: "error",
    responseTime: 0,
    uptime: 87.3,
    lastCheck: "12 min ago",
    version: "v1.0.9",
    description: "Analytics report generation service",
  },
  {
    id: 6,
    name: "Authentication API",
    endpoint: "/api/v1/auth",
    status: "healthy",
    responseTime: 23,
    uptime: 99.95,
    lastCheck: "1 min ago",
    version: "v2.1.0",
    description: "User authentication and authorization",
  },
];

const generateSystemMetrics = () => ({
  cpu: Math.random() * 80 + 10,
  memory: Math.random() * 70 + 20,
  disk: Math.random() * 60 + 30,
  network: Math.random() * 90 + 5,
  activeConnections: Math.floor(Math.random() * 500) + 100,
  requestsPerMinute: Math.floor(Math.random() * 1000) + 200,
  errorRate: Math.random() * 5,
  avgResponseTime: Math.random() * 200 + 50,
});

const generateApiLogs = () => [
  {
    id: 1,
    timestamp: "2024-01-15 14:32:15",
    method: "GET",
    endpoint: "/api/v1/players/performance",
    status: 200,
    responseTime: 145,
    ip: "192.168.1.100",
    userAgent: "AFL-Analytics-Mobile/1.2.0",
  },
  {
    id: 2,
    timestamp: "2024-01-15 14:32:10",
    method: "POST",
    endpoint: "/api/v1/video/analyze",
    status: 500,
    responseTime: 5000,
    ip: "192.168.1.105",
    userAgent: "AFL-Analytics-Web/2.1.0",
    error: "Internal server error: Video processing timeout",
  },
  {
    id: 3,
    timestamp: "2024-01-15 14:32:05",
    method: "GET",
    endpoint: "/api/v1/crowd/monitor",
    status: 200,
    responseTime: 89,
    ip: "192.168.1.102",
    userAgent: "AFL-Analytics-Mobile/1.2.0",
  },
  {
    id: 4,
    timestamp: "2024-01-15 14:32:00",
    method: "DELETE",
    endpoint: "/api/v1/reports/123",
    status: 404,
    responseTime: 12,
    ip: "192.168.1.108",
    userAgent: "AFL-Analytics-Web/2.1.0",
    error: "Report not found",
  },
  {
    id: 5,
    timestamp: "2024-01-15 14:31:55",
    method: "PUT",
    endpoint: "/api/v1/players/456",
    status: 200,
    responseTime: 234,
    ip: "192.168.1.103",
    userAgent: "AFL-Analytics-Admin/1.0.0",
  },
];

export default function ApiDiagnostics() {
  const [isLive, setIsLive] = useState(true);
  const [apiStatus, setApiStatus] = useState(generateApiStatus());
  const [systemMetrics, setSystemMetrics] = useState(generateSystemMetrics());
  const [apiLogs, setApiLogs] = useState(generateApiLogs());
  const [testEndpoint, setTestEndpoint] = useState("");
  const [testMethod, setTestMethod] = useState("GET");
  const [testBody, setTestBody] = useState("");
  const [testHeaders, setTestHeaders] = useState("");
  const [testResult, setTestResult] = useState<any>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState("1h");

  // Simulate real-time updates
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      setSystemMetrics(generateSystemMetrics());
      setApiStatus((prevStatus) =>
        prevStatus.map((api) => ({
          ...api,
          responseTime: Math.max(
            10,
            api.responseTime + (Math.random() - 0.5) * 50,
          ),
          lastCheck: "Just now",
        })),
      );
    }, 5000);

    return () => clearInterval(interval);
  }, [isLive]);

  const runApiTest = async () => {
    setIsTesting(true);
    setTestResult(null);

    // Simulate API test
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const mockResult = {
      status: Math.random() > 0.8 ? 500 : 200,
      responseTime: Math.random() * 300 + 50,
      headers: {
        "content-type": "application/json",
        "x-response-time": "156ms",
        "x-request-id": "req_" + Math.random().toString(36).substr(2, 9),
      },
      body:
        testMethod === "GET"
          ? {
              data: [
                { id: 1, name: "Test Player", performance: 85 },
                { id: 2, name: "Another Player", performance: 92 },
              ],
              meta: { total: 2, page: 1 },
            }
          : { message: "Success", id: Math.floor(Math.random() * 1000) },
    };

    setTestResult(mockResult);
    setIsTesting(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-green-600 bg-green-100";
      case "warning":
        return "text-yellow-600 bg-yellow-100";
      case "error":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="w-4 h-4" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4" />;
      case "error":
        return <XCircle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getHttpStatusColor = (status: number) => {
    if (status >= 200 && status < 300) return "text-green-600";
    if (status >= 300 && status < 400) return "text-blue-600";
    if (status >= 400 && status < 500) return "text-yellow-600";
    return "text-red-600";
  };

  const healthyApis = apiStatus.filter(
    (api) => api.status === "healthy",
  ).length;
  const totalApis = apiStatus.length;
  const overallHealth = (healthyApis / totalApis) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <MobileNavigation />

      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-4">
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
                    <p className="text-sm text-gray-600">API Health</p>
                    <p className="text-2xl font-bold">
                      {healthyApis}/{totalApis}
                    </p>
                    <p className="text-xs text-gray-500">
                      {overallHealth.toFixed(1)}% healthy
                    </p>
                  </div>
                  <div
                    className={`p-2 rounded-full ${overallHealth > 80 ? "bg-green-100" : "bg-red-100"}`}
                  >
                    {overallHealth > 80 ? (
                      <CheckCircle className="w-6 h-6 text-green-500" />
                    ) : (
                      <XCircle className="w-6 h-6 text-red-500" />
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Avg Response</p>
                    <p className="text-2xl font-bold">
                      {systemMetrics.avgResponseTime.toFixed(0)}ms
                    </p>
                    <p className="text-xs text-gray-500">Last minute</p>
                  </div>
                  <Zap className="w-6 h-6 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Requests/min</p>
                    <p className="text-2xl font-bold">
                      {systemMetrics.requestsPerMinute}
                    </p>
                    <p className="text-xs text-gray-500">Current load</p>
                  </div>
                  <Activity className="w-6 h-6 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Error Rate</p>
                    <p className="text-2xl font-bold">
                      {systemMetrics.errorRate.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500">Last hour</p>
                  </div>
                  <AlertTriangle className="w-6 h-6 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          <Tabs defaultValue="status" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="status" className="flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Status
              </TabsTrigger>
              <TabsTrigger value="metrics" className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Metrics
              </TabsTrigger>
              <TabsTrigger value="logs" className="flex items-center gap-2">
                <Terminal className="w-4 h-4" />
                Logs
              </TabsTrigger>
              <TabsTrigger value="test" className="flex items-center gap-2">
                <Play className="w-4 h-4" />
                Test
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                Settings
              </TabsTrigger>
            </TabsList>

            {/* API Status Tab */}
            <TabsContent value="status" className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">API Endpoints Status</h3>
                <Button variant="outline" size="sm">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh All
                </Button>
              </div>

              <div className="grid gap-4">
                {apiStatus.map((api) => (
                  <Card
                    key={api.id}
                    className="hover:shadow-md transition-shadow"
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div
                            className={`p-1 rounded-full ${getStatusColor(api.status)}`}
                          >
                            {getStatusIcon(api.status)}
                          </div>
                          <div>
                            <h4 className="font-medium">{api.name}</h4>
                            <p className="text-sm text-gray-600">
                              {api.endpoint}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant="outline">{api.version}</Badge>
                          <p className="text-xs text-gray-500 mt-1">
                            {api.lastCheck}
                          </p>
                        </div>
                      </div>

                      <p className="text-sm text-gray-600 mb-3">
                        {api.description}
                      </p>

                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div className="text-center p-2 bg-gray-50 rounded">
                          <div className="font-medium">
                            {api.responseTime}ms
                          </div>
                          <div className="text-gray-600">Response Time</div>
                        </div>
                        <div className="text-center p-2 bg-gray-50 rounded">
                          <div className="font-medium">{api.uptime}%</div>
                          <div className="text-gray-600">Uptime</div>
                        </div>
                        <div className="text-center p-2 bg-gray-50 rounded">
                          <div
                            className={`font-medium ${api.status === "healthy" ? "text-green-600" : api.status === "warning" ? "text-yellow-600" : "text-red-600"}`}
                          >
                            {api.status.toUpperCase()}
                          </div>
                          <div className="text-gray-600">Status</div>
                        </div>
                      </div>

                      <div className="flex gap-2 mt-3">
                        <Button variant="outline" size="sm">
                          <Eye className="w-4 h-4 mr-1" />
                          Details
                        </Button>
                        <Button variant="outline" size="sm">
                          <Play className="w-4 h-4 mr-1" />
                          Test
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* System Metrics Tab */}
            <TabsContent value="metrics" className="space-y-4">
              <div className="grid lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Server className="w-5 h-5" />
                      System Resources
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>CPU Usage</span>
                          <span>{systemMetrics.cpu.toFixed(1)}%</span>
                        </div>
                        <Progress value={systemMetrics.cpu} className="h-2" />
                      </div>

                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Memory Usage</span>
                          <span>{systemMetrics.memory.toFixed(1)}%</span>
                        </div>
                        <Progress
                          value={systemMetrics.memory}
                          className="h-2"
                        />
                      </div>

                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Disk Usage</span>
                          <span>{systemMetrics.disk.toFixed(1)}%</span>
                        </div>
                        <Progress value={systemMetrics.disk} className="h-2" />
                      </div>

                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Network Utilization</span>
                          <span>{systemMetrics.network.toFixed(1)}%</span>
                        </div>
                        <Progress
                          value={systemMetrics.network}
                          className="h-2"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Monitor className="w-5 h-5" />
                      Performance Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {systemMetrics.activeConnections}
                        </div>
                        <div className="text-sm text-gray-600">
                          Active Connections
                        </div>
                      </div>
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {systemMetrics.requestsPerMinute}
                        </div>
                        <div className="text-sm text-gray-600">
                          Requests/min
                        </div>
                      </div>
                      <div className="text-center p-3 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {systemMetrics.avgResponseTime.toFixed(0)}ms
                        </div>
                        <div className="text-sm text-gray-600">
                          Avg Response
                        </div>
                      </div>
                      <div className="text-center p-3 bg-red-50 rounded-lg">
                        <div className="text-2xl font-bold text-red-600">
                          {systemMetrics.errorRate.toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-600">Error Rate</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Database className="w-5 h-5" />
                      Database Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 border rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="font-medium">Primary Database</span>
                        </div>
                        <div className="space-y-1 text-sm text-gray-600">
                          <div>Connection Pool: 45/100</div>
                          <div>Query Time: 23ms</div>
                          <div>Status: Online</div>
                        </div>
                      </div>
                      <div className="p-4 border rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="font-medium">Read Replica</span>
                        </div>
                        <div className="space-y-1 text-sm text-gray-600">
                          <div>Connection Pool: 12/50</div>
                          <div>Query Time: 18ms</div>
                          <div>Status: Online</div>
                        </div>
                      </div>
                      <div className="p-4 border rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <XCircle className="w-4 h-4 text-red-500" />
                          <span className="font-medium">Cache Redis</span>
                        </div>
                        <div className="space-y-1 text-sm text-gray-600">
                          <div>Memory Usage: 89%</div>
                          <div>Hit Rate: 94.2%</div>
                          <div>Status: Degraded</div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* API Logs Tab */}
            <TabsContent value="logs" className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold">API Request Logs</h3>
                <div className="flex gap-2">
                  <Select
                    value={selectedTimeRange}
                    onValueChange={setSelectedTimeRange}
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1h">Last Hour</SelectItem>
                      <SelectItem value="6h">Last 6 Hours</SelectItem>
                      <SelectItem value="24h">Last 24 Hours</SelectItem>
                      <SelectItem value="7d">Last 7 Days</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>

              <Card>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                            Timestamp
                          </th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                            Method
                          </th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                            Endpoint
                          </th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                            Status
                          </th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                            Response Time
                          </th>
                          <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">
                            IP Address
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {apiLogs.map((log) => (
                          <tr key={log.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {log.timestamp}
                            </td>
                            <td className="px-4 py-3">
                              <Badge variant="outline" className="text-xs">
                                {log.method}
                              </Badge>
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900 font-mono">
                              {log.endpoint}
                            </td>
                            <td className="px-4 py-3">
                              <span
                                className={`text-sm font-medium ${getHttpStatusColor(log.status)}`}
                              >
                                {log.status}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {log.responseTime}ms
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900 font-mono">
                              {log.ip}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* API Test Tab */}
            <TabsContent value="test" className="space-y-4">
              <div className="grid lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Play className="w-5 h-5" />
                      API Testing Tool
                    </CardTitle>
                    <CardDescription>
                      Test API endpoints manually with custom requests
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div>
                        <Label htmlFor="method">HTTP Method</Label>
                        <Select
                          value={testMethod}
                          onValueChange={setTestMethod}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="GET">GET</SelectItem>
                            <SelectItem value="POST">POST</SelectItem>
                            <SelectItem value="PUT">PUT</SelectItem>
                            <SelectItem value="DELETE">DELETE</SelectItem>
                            <SelectItem value="PATCH">PATCH</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label htmlFor="endpoint">Endpoint URL</Label>
                        <Input
                          id="endpoint"
                          placeholder="/api/v1/players/performance"
                          value={testEndpoint}
                          onChange={(e) => setTestEndpoint(e.target.value)}
                        />
                      </div>

                      <div>
                        <Label htmlFor="headers">Headers (JSON format)</Label>
                        <Textarea
                          id="headers"
                          placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}'
                          value={testHeaders}
                          onChange={(e) => setTestHeaders(e.target.value)}
                          rows={3}
                        />
                      </div>

                      {(testMethod === "POST" ||
                        testMethod === "PUT" ||
                        testMethod === "PATCH") && (
                        <div>
                          <Label htmlFor="body">
                            Request Body (JSON format)
                          </Label>
                          <Textarea
                            id="body"
                            placeholder='{"key": "value"}'
                            value={testBody}
                            onChange={(e) => setTestBody(e.target.value)}
                            rows={4}
                          />
                        </div>
                      )}

                      <Button
                        onClick={runApiTest}
                        disabled={!testEndpoint || isTesting}
                        className="w-full"
                      >
                        {isTesting ? (
                          <>
                            <Loader className="w-4 h-4 mr-2 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4 mr-2" />
                            Send Request
                          </>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Terminal className="w-5 h-5" />
                      Response
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {testResult ? (
                      <div className="space-y-4">
                        <div className="flex items-center gap-4">
                          <Badge
                            variant={
                              testResult.status >= 200 &&
                              testResult.status < 300
                                ? "default"
                                : "destructive"
                            }
                          >
                            {testResult.status}
                          </Badge>
                          <span className="text-sm text-gray-600">
                            {testResult.responseTime.toFixed(0)}ms
                          </span>
                        </div>

                        <div>
                          <h4 className="font-medium mb-2">Response Headers</h4>
                          <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto">
                            {JSON.stringify(testResult.headers, null, 2)}
                          </pre>
                        </div>

                        <div>
                          <h4 className="font-medium mb-2">Response Body</h4>
                          <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto">
                            {JSON.stringify(testResult.body, null, 2)}
                          </pre>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <Terminal className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>No response yet. Send a request to see results.</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Settings Tab */}
            <TabsContent value="settings" className="space-y-4">
              <div className="grid lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="w-5 h-5" />
                      Monitoring Settings
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div>
                        <Label>Health Check Interval</Label>
                        <Select defaultValue="30s">
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="10s">10 seconds</SelectItem>
                            <SelectItem value="30s">30 seconds</SelectItem>
                            <SelectItem value="1m">1 minute</SelectItem>
                            <SelectItem value="5m">5 minutes</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label>Alert Threshold (Response Time)</Label>
                        <Input placeholder="2000ms" />
                      </div>

                      <div>
                        <Label>Error Rate Threshold</Label>
                        <Input placeholder="5%" />
                      </div>

                      <div className="space-y-2">
                        <h4 className="font-medium">Email Notifications</h4>
                        <div className="space-y-2">
                          {[
                            "API Downtime",
                            "High Error Rate",
                            "Slow Response Times",
                            "System Resource Alerts",
                          ].map((alert) => (
                            <label
                              key={alert}
                              className="flex items-center space-x-2"
                            >
                              <input
                                type="checkbox"
                                defaultChecked
                                className="rounded"
                              />
                              <span className="text-sm">{alert}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="w-5 h-5" />
                      Security Settings
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div>
                        <Label>API Rate Limiting</Label>
                        <Select defaultValue="1000">
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="100">
                              100 requests/min
                            </SelectItem>
                            <SelectItem value="500">
                              500 requests/min
                            </SelectItem>
                            <SelectItem value="1000">
                              1000 requests/min
                            </SelectItem>
                            <SelectItem value="unlimited">Unlimited</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <h4 className="font-medium">Security Features</h4>
                        <div className="space-y-2">
                          {[
                            "IP Whitelisting",
                            "Request Logging",
                            "SSL/TLS Enforcement",
                            "DDoS Protection",
                          ].map((feature) => (
                            <label
                              key={feature}
                              className="flex items-center space-x-2"
                            >
                              <input
                                type="checkbox"
                                defaultChecked
                                className="rounded"
                              />
                              <span className="text-sm">{feature}</span>
                            </label>
                          ))}
                        </div>
                      </div>

                      <Button className="w-full">Save Settings</Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
