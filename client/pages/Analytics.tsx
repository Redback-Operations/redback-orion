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
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import MobileNavigation from "@/components/MobileNavigation";
import LiveClock from "@/components/LiveClock";
import {
  Upload,
  Video,
  Download,
  FileText,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Eye,
  Zap,
  Target,
  Activity,
  BarChart3,
  PieChart,
  TrendingUp,
  Clock,
  User,
  Trophy,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader,
  Camera,
  Film,
  Settings,
  Filter,
} from "lucide-react";

// Mock data for video analysis
const generateAnalysisData = () => ({
  keyMoments: [
    {
      time: "02:15",
      type: "GOAL",
      player: "Marcus Bontempelli",
      confidence: 0.95,
      description: "Long range goal from 45m",
    },
    {
      time: "05:42",
      type: "MARK",
      player: "Charlie Curnow",
      confidence: 0.89,
      description: "Spectacular mark in forward 50",
    },
    {
      time: "08:31",
      type: "TACKLE",
      player: "Clayton Oliver",
      confidence: 0.92,
      description: "Crucial defensive tackle",
    },
    {
      time: "12:04",
      type: "GOAL",
      player: "Taylor Walker",
      confidence: 0.88,
      description: "Set shot from 20m angle",
    },
    {
      time: "15:17",
      type: "BEHIND",
      player: "Jeremy Cameron",
      confidence: 0.85,
      description: "Shot from boundary line",
    },
    {
      time: "18:55",
      type: "MARK",
      player: "Max Gawn",
      confidence: 0.91,
      description: "Strong contested mark",
    },
  ],
  playerStats: {
    "Marcus Bontempelli": {
      possessions: 28,
      efficiency: 87,
      goals: 2,
      timeOnScreen: "12:45",
    },
    "Charlie Curnow": {
      possessions: 18,
      efficiency: 82,
      goals: 3,
      timeOnScreen: "8:32",
    },
    "Clayton Oliver": {
      possessions: 32,
      efficiency: 85,
      goals: 0,
      timeOnScreen: "15:23",
    },
    "Taylor Walker": {
      possessions: 22,
      efficiency: 79,
      goals: 2,
      timeOnScreen: "10:15",
    },
  },
  teamStats: {
    disposalEfficiency: 78,
    contested: 45,
    uncontested: 55,
    inside50s: 24,
    forwardPressure: 82,
  },
  heatMap: [
    { zone: "Forward 50", activity: 85, events: 12 },
    { zone: "Midfield", activity: 92, events: 28 },
    { zone: "Defensive 50", activity: 73, events: 8 },
  ],
});

export default function Analytics() {
  const [isLive, setIsLive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [analysisData, setAnalysisData] = useState(generateAnalysisData());
  const [selectedAnalysis, setSelectedAnalysis] = useState("highlights");
  const [customReportFormat, setCustomReportFormat] = useState("pdf");
  const [videoMetadata, setVideoMetadata] = useState({
    title: "",
    description: "",
    teams: "",
    venue: "",
    date: "",
    round: "",
  });

  const processingQueue = [
    {
      id: 1,
      name: "Round_15_Carlton_vs_Adelaide.mp4",
      status: "completed",
      progress: 100,
      uploadTime: "2 min ago",
      analysisType: "Full Match Analysis",
      duration: "2:45:12",
      size: "1.2 GB",
    },
    {
      id: 2,
      name: "Training_Session_January_14.mov",
      status: "analyzing",
      progress: 67,
      uploadTime: "8 min ago",
      analysisType: "Player Performance",
      duration: "1:23:45",
      size: "850 MB",
    },
    {
      id: 3,
      name: "Match_Highlights_Compilation.mp4",
      status: "queued",
      progress: 0,
      uploadTime: "12 min ago",
      analysisType: "Highlight Detection",
      duration: "0:18:32",
      size: "450 MB",
    },
    {
      id: 4,
      name: "Tactical_Review_Session.avi",
      status: "uploading",
      progress: 34,
      uploadTime: "15 min ago",
      analysisType: "Tactical Analysis",
      duration: "0:45:18",
      size: "1.8 GB",
    },
  ];

  const availableReports = [
    {
      id: 1,
      name: "Match Performance Report - Round 15",
      type: "Match Analysis",
      date: "2024-01-15",
      size: "2.4 MB",
      format: "PDF",
      teams: "Carlton vs Adelaide",
      status: "ready",
    },
    {
      id: 2,
      name: "Player Tracking Analysis - Bontempelli",
      type: "Player Analysis",
      date: "2024-01-14",
      size: "1.8 MB",
      format: "Excel",
      teams: "Western Bulldogs",
      status: "ready",
    },
    {
      id: 3,
      name: "Tactical Patterns Report",
      type: "Tactical Analysis",
      date: "2024-01-12",
      size: "3.1 MB",
      format: "PDF",
      teams: "Multi-team Analysis",
      status: "ready",
    },
    {
      id: 4,
      name: "Video Highlights Package",
      type: "Video Export",
      date: "2024-01-10",
      size: "156 MB",
      format: "MP4",
      teams: "Season Highlights",
      status: "processing",
    },
  ];

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const simulateUpload = async () => {
    setIsUploading(true);
    setUploadProgress(0);

    for (let i = 0; i <= 100; i += 5) {
      await new Promise((resolve) => setTimeout(resolve, 100));
      setUploadProgress(i);
    }

    setIsUploading(false);
    startAnalysis();
  };

  const startAnalysis = async () => {
    setIsAnalyzing(true);
    setAnalysisProgress(0);

    for (let i = 0; i <= 100; i += 2) {
      await new Promise((resolve) => setTimeout(resolve, 150));
      setAnalysisProgress(i);
    }

    setIsAnalyzing(false);
    setAnalysisComplete(true);
  };

  const handleUploadAndAnalyze = () => {
    if (selectedFile) {
      simulateUpload();
    }
  };

  const generateReport = async (reportType: string, format: string = "txt") => {
    // Simulate report generation
    await new Promise((resolve) => setTimeout(resolve, 2000));

    let content: string;
    let mimeType: string;
    let extension: string;

    switch (format.toLowerCase()) {
      case "json":
        content = JSON.stringify({
          reportType,
          generatedOn: new Date().toISOString(),
          data: {
            matchAnalysis: analysisData,
            playerStats: analysisData.playerStats,
            teamStats: analysisData.teamStats,
            keyMoments: analysisData.keyMoments,
          },
          summary: {
            totalEvents: analysisData.keyMoments.length,
            analysisComplete: analysisComplete,
            videoMetadata,
          },
        }, null, 2);
        mimeType = "application/json";
        extension = "json";
        break;

      case "csv":
        const csvHeader = "Player,Possessions,Efficiency,Goals,Screen Time\n";
        const csvData = Object.entries(analysisData.playerStats)
          .map(([player, stats]) =>
            `"${player}",${stats.possessions},${stats.efficiency},${stats.goals},"${stats.timeOnScreen}"`
          ).join("\n");
        content = csvHeader + csvData;
        mimeType = "text/csv";
        extension = "csv";
        break;

      case "pdf":
        // For PDF, we'll create a simple text content that represents what would be in a PDF
        content = `AFL Analytics Report - ${reportType}

Generated on: ${new Date().toLocaleString()}

MATCH ANALYSIS SUMMARY
=====================

Key Moments Detected: ${analysisData.keyMoments.length}
${analysisData.keyMoments.map(moment =>
  `- ${moment.time}: ${moment.type} by ${moment.player} (${(moment.confidence * 100).toFixed(0)}% confidence)`
).join('\n')}

PLAYER PERFORMANCE
==================
${Object.entries(analysisData.playerStats).map(([player, stats]) =>
  `${player}:
  - Possessions: ${stats.possessions}
  - Efficiency: ${stats.efficiency}%
  - Goals: ${stats.goals}
  - Screen Time: ${stats.timeOnScreen}`
).join('\n\n')}

TEAM STATISTICS
===============
- Disposal Efficiency: ${analysisData.teamStats.disposalEfficiency}%
- Contested Possession: ${analysisData.teamStats.contested}%
- Uncontested Possession: ${analysisData.teamStats.uncontested}%
- Inside 50s: ${analysisData.teamStats.inside50s}
- Forward Pressure: ${analysisData.teamStats.forwardPressure}%

This report was generated by AFL Analytics Platform.`;
        mimeType = "application/pdf";
        extension = "txt"; // We'll save as txt since we're not generating actual PDF
        break;

      default:
        content = `AFL Analytics Report - ${reportType}\n\nGenerated on: ${new Date().toLocaleString()}\n\nThis is a sample report generated by AFL Analytics Platform.\n\nAnalysis Data:\n${JSON.stringify(analysisData, null, 2)}`;
        mimeType = "text/plain";
        extension = "txt";
    }

    // Create and download the file
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `AFL_Analytics_${reportType}_${Date.now()}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadReport = (reportId: number, format: string) => {
    const report = availableReports.find(r => r.id === reportId);
    if (report) {
      generateReport(report.type.replace(' ', '_'), format);
    }
  };

  const StatusIcon = ({ status }: { status: string }) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "analyzing":
      case "uploading":
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      case "queued":
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case "error":
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

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

          <Tabs defaultValue="upload" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="upload" className="flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Upload
              </TabsTrigger>
              <TabsTrigger value="analysis" className="flex items-center gap-2">
                <Eye className="w-4 h-4" />
                Analysis
              </TabsTrigger>
              <TabsTrigger value="reports" className="flex items-center gap-2">
                <Download className="w-4 h-4" />
                Reports
              </TabsTrigger>
              <TabsTrigger value="queue" className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Queue
              </TabsTrigger>
            </TabsList>

            {/* Video Upload Tab */}
            <TabsContent value="upload" className="space-y-4">
              <div className="grid lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Upload className="w-5 h-5" />
                      Video Upload
                    </CardTitle>
                    <CardDescription>
                      Upload match videos for AI-powered analysis
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                      <input
                        type="file"
                        accept="video/*"
                        onChange={handleFileSelect}
                        className="hidden"
                        id="video-upload"
                      />
                      <label htmlFor="video-upload" className="cursor-pointer">
                        <Video className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                        <div className="text-lg font-medium text-gray-700">
                          {selectedFile
                            ? selectedFile.name
                            : "Drop video files here"}
                        </div>
                        <div className="text-sm text-gray-500">
                          or click to browse
                        </div>
                        <div className="text-xs text-gray-400 mt-2">
                          Supports MP4, MOV, AVI • Max 2GB
                        </div>
                      </label>
                    </div>

                    {selectedFile && (
                      <div className="space-y-3">
                        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                          <div className="flex items-center gap-2">
                            <Film className="w-4 h-4 text-blue-600" />
                            <span className="font-medium">
                              {selectedFile.name}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600 mt-1">
                            Size: {(selectedFile.size / 1024 / 1024).toFixed(1)}{" "}
                            MB
                          </div>
                        </div>

                        {isUploading && (
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>Uploading...</span>
                              <span>{uploadProgress}%</span>
                            </div>
                            <Progress value={uploadProgress} className="h-2" />
                          </div>
                        )}

                        {isAnalyzing && (
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>Analyzing video...</span>
                              <span>{analysisProgress}%</span>
                            </div>
                            <Progress
                              value={analysisProgress}
                              className="h-2"
                            />
                          </div>
                        )}

                        {!isUploading && !isAnalyzing && !analysisComplete && (
                          <Button
                            onClick={handleUploadAndAnalyze}
                            className="w-full bg-gradient-to-r from-green-600 to-blue-600"
                          >
                            <Zap className="w-4 h-4 mr-2" />
                            Upload & Analyze
                          </Button>
                        )}

                        {analysisComplete && (
                          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                            <div className="flex items-center gap-2">
                              <CheckCircle className="w-4 h-4 text-green-600" />
                              <span className="font-medium text-green-700">
                                Analysis Complete!
                              </span>
                            </div>
                            <p className="text-sm text-green-600 mt-1">
                              Click on the Analysis tab to view results
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="w-5 h-5" />
                      Analysis Settings
                    </CardTitle>
                    <CardDescription>
                      Configure analysis parameters and metadata
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div>
                        <Label htmlFor="analysis-type">Analysis Type</Label>
                        <Select
                          value={selectedAnalysis}
                          onValueChange={setSelectedAnalysis}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="highlights">
                              Match Highlights
                            </SelectItem>
                            <SelectItem value="player">
                              Player Tracking
                            </SelectItem>
                            <SelectItem value="tactical">
                              Tactical Analysis
                            </SelectItem>
                            <SelectItem value="performance">
                              Performance Metrics
                            </SelectItem>
                            <SelectItem value="crowd">
                              Crowd Reactions
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label htmlFor="title">Video Title</Label>
                        <Input
                          id="title"
                          placeholder="e.g., Round 15 - Carlton vs Adelaide"
                          value={videoMetadata.title}
                          onChange={(e) =>
                            setVideoMetadata({
                              ...videoMetadata,
                              title: e.target.value,
                            })
                          }
                        />
                      </div>

                      <div>
                        <Label htmlFor="teams">Teams</Label>
                        <Input
                          id="teams"
                          placeholder="e.g., Carlton vs Adelaide"
                          value={videoMetadata.teams}
                          onChange={(e) =>
                            setVideoMetadata({
                              ...videoMetadata,
                              teams: e.target.value,
                            })
                          }
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label htmlFor="venue">Venue</Label>
                          <Input
                            id="venue"
                            placeholder="MCG"
                            value={videoMetadata.venue}
                            onChange={(e) =>
                              setVideoMetadata({
                                ...videoMetadata,
                                venue: e.target.value,
                              })
                            }
                          />
                        </div>
                        <div>
                          <Label htmlFor="round">Round</Label>
                          <Input
                            id="round"
                            placeholder="15"
                            value={videoMetadata.round}
                            onChange={(e) =>
                              setVideoMetadata({
                                ...videoMetadata,
                                round: e.target.value,
                              })
                            }
                          />
                        </div>
                      </div>

                      <div>
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                          id="description"
                          placeholder="Additional details about the match..."
                          value={videoMetadata.description}
                          onChange={(e) =>
                            setVideoMetadata({
                              ...videoMetadata,
                              description: e.target.value,
                            })
                          }
                          rows={3}
                        />
                      </div>
                    </div>

                    <Separator />

                    <div className="space-y-2">
                      <h4 className="font-medium">Analysis Features</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {[
                          "Goal Detection",
                          "Player Tracking",
                          "Ball Possession",
                          "Tactical Patterns",
                          "Crowd Reactions",
                          "Match Statistics",
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
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Analysis Results Tab */}
            <TabsContent value="analysis" className="space-y-4">
              {analysisComplete ? (
                <div className="grid lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="w-5 h-5" />
                        Key Moments Detected
                      </CardTitle>
                      <CardDescription>
                        AI-identified significant events in the match
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {analysisData.keyMoments.map((moment, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer"
                          >
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge
                                  variant={
                                    moment.type === "GOAL"
                                      ? "default"
                                      : moment.type === "MARK"
                                        ? "secondary"
                                        : "outline"
                                  }
                                >
                                  {moment.type}
                                </Badge>
                                <span className="font-medium">
                                  {moment.player}
                                </span>
                                <span className="text-sm text-gray-600">
                                  {moment.time}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600">
                                {moment.description}
                              </p>
                              <div className="text-xs text-green-600 mt-1">
                                Confidence:{" "}
                                {(moment.confidence * 100).toFixed(0)}%
                              </div>
                            </div>
                            <Button variant="outline" size="sm">
                              <Play className="w-4 h-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <User className="w-5 h-5" />
                        Player Performance
                      </CardTitle>
                      <CardDescription>
                        Individual player statistics from video analysis
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {Object.entries(analysisData.playerStats).map(
                          ([player, stats]) => (
                            <div key={player} className="p-3 border rounded-lg">
                              <div className="font-medium mb-2">{player}</div>
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                <div className="flex justify-between">
                                  <span>Possessions:</span>
                                  <span className="font-medium">
                                    {stats.possessions}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Efficiency:</span>
                                  <span className="font-medium">
                                    {stats.efficiency}%
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Goals:</span>
                                  <span className="font-medium">
                                    {stats.goals}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Screen Time:</span>
                                  <span className="font-medium">
                                    {stats.timeOnScreen}
                                  </span>
                                </div>
                              </div>
                            </div>
                          ),
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="w-5 h-5" />
                        Team Statistics
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 gap-3">
                          <div className="flex justify-between items-center">
                            <span>Disposal Efficiency</span>
                            <span className="font-medium">
                              {analysisData.teamStats.disposalEfficiency}%
                            </span>
                          </div>
                          <Progress
                            value={analysisData.teamStats.disposalEfficiency}
                            className="h-2"
                          />

                          <div className="flex justify-between items-center">
                            <span>Forward Pressure</span>
                            <span className="font-medium">
                              {analysisData.teamStats.forwardPressure}%
                            </span>
                          </div>
                          <Progress
                            value={analysisData.teamStats.forwardPressure}
                            className="h-2"
                          />
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-center">
                          <div className="p-3 bg-blue-50 rounded">
                            <div className="text-lg font-bold text-blue-600">
                              {analysisData.teamStats.contested}%
                            </div>
                            <div className="text-sm text-gray-600">
                              Contested
                            </div>
                          </div>
                          <div className="p-3 bg-green-50 rounded">
                            <div className="text-lg font-bold text-green-600">
                              {analysisData.teamStats.uncontested}%
                            </div>
                            <div className="text-sm text-gray-600">
                              Uncontested
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Activity className="w-5 h-5" />
                        Field Heat Map
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {analysisData.heatMap.map((zone, index) => (
                          <div key={index} className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>{zone.zone}</span>
                              <span>
                                {zone.events} events • {zone.activity}% activity
                              </span>
                            </div>
                            <Progress value={zone.activity} className="h-3" />
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <Card>
                  <CardContent className="p-8 text-center">
                    <Video className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No Analysis Available
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Upload a video file to start the analysis process
                    </p>
                    <Button variant="outline">Go to Upload Tab</Button>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Reports Tab */}
            <TabsContent value="reports" className="space-y-4">
              <div className="grid lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="w-5 h-5" />
                      Generate New Report
                    </CardTitle>
                    <CardDescription>
                      Create custom analysis reports from processed videos
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-3">
                      <Button
                        onClick={() => generateReport("Match_Summary", "pdf")}
                        className="flex items-center gap-2"
                      >
                        <Trophy className="w-4 h-4" />
                        Match Summary (PDF)
                      </Button>
                      <Button
                        onClick={() => generateReport("Player_Analysis", "csv")}
                        variant="outline"
                        className="flex items-center gap-2"
                      >
                        <User className="w-4 h-4" />
                        Player Analysis (CSV)
                      </Button>
                      <Button
                        onClick={() => generateReport("Tactical_Report", "json")}
                        variant="outline"
                        className="flex items-center gap-2"
                      >
                        <Target className="w-4 h-4" />
                        Tactical Report (JSON)
                      </Button>
                      <Button
                        onClick={() => generateReport("Video_Highlights", "pdf")}
                        variant="outline"
                        className="flex items-center gap-2"
                      >
                        <Video className="w-4 h-4" />
                        Video Highlights (PDF)
                      </Button>
                    </div>

                    <Separator />

                    <div className="space-y-3">
                      <h4 className="font-medium">Custom Report Builder</h4>
                      <div className="space-y-2">
                        <Label>Report Format</Label>
                        <Select
                          value={customReportFormat}
                          onValueChange={setCustomReportFormat}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="pdf">PDF Report</SelectItem>
                            <SelectItem value="csv">
                              CSV Spreadsheet
                            </SelectItem>
                            <SelectItem value="json">
                              Raw Data (JSON)
                            </SelectItem>
                            <SelectItem value="txt">Text Report</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label>Include Sections</Label>
                        <div className="grid grid-cols-2 gap-2">
                          {[
                            "Match Statistics",
                            "Player Performance",
                            "Key Moments",
                            "Tactical Analysis",
                            "Heat Maps",
                            "Video Clips",
                          ].map((section) => (
                            <label
                              key={section}
                              className="flex items-center space-x-2"
                            >
                              <input
                                type="checkbox"
                                defaultChecked
                                className="rounded"
                              />
                              <span className="text-sm">{section}</span>
                            </label>
                          ))}
                        </div>
                      </div>

                      <Button
                        onClick={() => generateReport("Custom_Report", customReportFormat)}
                        className="w-full bg-gradient-to-r from-green-600 to-blue-600"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Generate Custom Report ({customReportFormat.toUpperCase()})
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Download className="w-5 h-5" />
                      Available Reports
                    </CardTitle>
                    <CardDescription>
                      Download previously generated reports
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {availableReports.map((report) => (
                        <div
                          key={report.id}
                          className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                        >
                          <div className="flex-1">
                            <div className="font-medium">{report.name}</div>
                            <div className="text-sm text-gray-600">
                              {report.teams} • {report.date} • {report.size} •{" "}
                              {report.format}
                            </div>
                            <Badge variant="outline" className="mt-1">
                              {report.type}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2">
                            {report.status === "processing" ? (
                              <Badge variant="secondary">Processing</Badge>
                            ) : (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => downloadReport(report.id, report.format.toLowerCase())}
                              >
                                <Download className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Processing Queue Tab */}
            <TabsContent value="queue" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5" />
                    Processing Queue
                  </CardTitle>
                  <CardDescription>
                    Track the status of your video analysis requests
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {processingQueue.map((item) => (
                      <div key={item.id} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <StatusIcon status={item.status} />
                            <div>
                              <div className="font-medium">{item.name}</div>
                              <div className="text-sm text-gray-600">
                                {item.analysisType} • {item.duration} •{" "}
                                {item.size}
                              </div>
                            </div>
                          </div>
                          <Badge
                            variant={
                              item.status === "completed"
                                ? "default"
                                : item.status === "analyzing" ||
                                    item.status === "uploading"
                                  ? "secondary"
                                  : "outline"
                            }
                            className="capitalize"
                          >
                            {item.status}
                          </Badge>
                        </div>

                        {item.progress > 0 && item.progress < 100 && (
                          <div className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span>
                                {item.status === "uploading"
                                  ? "Uploading"
                                  : "Analyzing"}
                                ...
                              </span>
                              <span>{item.progress}%</span>
                            </div>
                            <Progress value={item.progress} className="h-2" />
                          </div>
                        )}

                        <div className="flex justify-between items-center mt-3">
                          <span className="text-sm text-gray-500">
                            {item.uploadTime}
                          </span>
                          <div className="flex gap-2">
                            {item.status === "completed" && (
                              <>
                                <Button variant="outline" size="sm">
                                  <Eye className="w-4 h-4" />
                                </Button>
                                <Button variant="outline" size="sm">
                                  <Download className="w-4 h-4" />
                                </Button>
                              </>
                            )}
                            {(item.status === "queued" ||
                              item.status === "uploading") && (
                              <Button variant="outline" size="sm">
                                <XCircle className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
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
