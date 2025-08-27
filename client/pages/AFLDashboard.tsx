import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  Activity,
  Users,
  BarChart3,
  Download,
  Upload,
  Search,
  Filter,
  Play,
  Pause,
  TrendingUp,
  TrendingDown,
  Clock,
  MapPin,
  Video,
  Eye,
  Target,
  Zap,
  Calendar,
  FileText,
  Settings,
  LogOut,
} from "lucide-react";

// Mock data for the dashboard
const mockPlayers = [
  {
    id: 1,
    name: "Marcus Bontempelli",
    team: "Western Bulldogs",
    position: "Midfielder",
    kicks: 28,
    handballs: 12,
    marks: 8,
    tackles: 6,
    goals: 2,
    efficiency: 87,
  },
  {
    id: 2,
    name: "Dustin Martin",
    team: "Richmond",
    position: "Forward",
    kicks: 22,
    handballs: 8,
    marks: 6,
    tackles: 4,
    goals: 3,
    efficiency: 82,
  },
  {
    id: 3,
    name: "Patrick Dangerfield",
    team: "Geelong",
    position: "Midfielder",
    kicks: 25,
    handballs: 15,
    marks: 7,
    tackles: 8,
    goals: 1,
    efficiency: 84,
  },
  {
    id: 4,
    name: "Max Gawn",
    team: "Melbourne",
    position: "Ruckman",
    kicks: 18,
    handballs: 6,
    marks: 10,
    tackles: 3,
    goals: 1,
    efficiency: 78,
  },
];

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

export default function AFLDashboard() {
  const navigate = useNavigate();
  const [selectedPlayer, setSelectedPlayer] = useState(mockPlayers[0]);
  const [comparisonPlayer, setComparisonPlayer] = useState(mockPlayers[1]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");
  const [isLive, setIsLive] = useState(true);
  const [userEmail, setUserEmail] = useState("");

  // Video upload states
  const [selectedVideoFile, setSelectedVideoFile] = useState<File | null>(null);
  const [isVideoUploading, setIsVideoUploading] = useState(false);
  const [videoUploadProgress, setVideoUploadProgress] = useState(0);
  const [isVideoAnalyzing, setIsVideoAnalyzing] = useState(false);
  const [videoAnalysisProgress, setVideoAnalysisProgress] = useState(0);
  const [videoAnalysisComplete, setVideoAnalysisComplete] = useState(false);
  const [videoAnalysisError, setVideoAnalysisError] = useState<string | null>(
    null,
  );
  const [selectedAnalysisType, setSelectedAnalysisType] =
    useState("highlights");
  const [selectedFocusAreas, setSelectedFocusAreas] = useState<string[]>([]);

  // Check authentication on component mount
  useEffect(() => {
    const isAuthenticated = localStorage.getItem("isAuthenticated");
    const email = localStorage.getItem("userEmail");

    if (!isAuthenticated || isAuthenticated !== "true") {
      // Redirect to login if not authenticated
      navigate("/");
      return;
    }

    if (email) {
      setUserEmail(email);
    }
  }, [navigate]);

  // Logout function
  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
    navigate("/");
  };

  // Video upload handlers
  const handleVideoFileSelect = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = [
        "video/mp4",
        "video/mov",
        "video/avi",
        "video/quicktime",
      ];
      if (!validTypes.includes(file.type)) {
        setVideoAnalysisError(
          "Please select a valid video file (MP4, MOV, or AVI)",
        );
        return;
      }

      // Validate file size (max 500MB)
      const maxSize = 500 * 1024 * 1024; // 500MB in bytes
      if (file.size > maxSize) {
        setVideoAnalysisError("File size must be less than 500MB");
        return;
      }

      setSelectedVideoFile(file);
      setVideoAnalysisError(null);
      setVideoAnalysisComplete(false);
    }
  };

  const handleFocusAreaChange = (area: string, checked: boolean) => {
    if (checked) {
      setSelectedFocusAreas([...selectedFocusAreas, area]);
    } else {
      setSelectedFocusAreas(selectedFocusAreas.filter((a) => a !== area));
    }
  };

  const uploadAndAnalyzeVideo = async () => {
    if (!selectedVideoFile) {
      setVideoAnalysisError("Please select a video file first");
      return;
    }

    try {
      setVideoAnalysisError(null);
      setIsVideoUploading(true);
      setVideoUploadProgress(0);

      // Simulate file upload with real progress
      for (let i = 0; i <= 100; i += 5) {
        await new Promise((resolve) => setTimeout(resolve, 100));
        setVideoUploadProgress(i);
      }

      setIsVideoUploading(false);
      setIsVideoAnalyzing(true);
      setVideoAnalysisProgress(0);

      // Simulate video analysis with real progress
      for (let i = 0; i <= 100; i += 2) {
        await new Promise((resolve) => setTimeout(resolve, 200));
        setVideoAnalysisProgress(i);
      }

      setIsVideoAnalyzing(false);
      setVideoAnalysisComplete(true);

      // Store analysis results
      const analysisResults = {
        fileName: selectedVideoFile.name,
        analysisType: selectedAnalysisType,
        focusAreas: selectedFocusAreas,
        timestamp: new Date().toISOString(),
        fileSize: selectedVideoFile.size,
      };

      const existingAnalyses = JSON.parse(
        localStorage.getItem("videoAnalyses") || "[]",
      );
      localStorage.setItem(
        "videoAnalyses",
        JSON.stringify([...existingAnalyses, analysisResults]),
      );
    } catch (error) {
      setIsVideoUploading(false);
      setIsVideoAnalyzing(false);
      setVideoAnalysisError(
        error instanceof Error ? error.message : "Upload failed",
      );
    }
  };

  const filteredPlayers = mockPlayers.filter(
    (player) =>
      player.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedTeam === "all" || player.team === selectedTeam),
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                  AFL Analytics
                </h1>
                <p className="text-sm text-gray-600">
                  Real-time match insights & player analytics
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge
                variant={isLive ? "destructive" : "secondary"}
                className="animate-pulse"
              >
                <div className="w-2 h-2 rounded-full bg-red-500 mr-2" />
                {isLive ? "LIVE" : "OFFLINE"}
              </Badge>
              {userEmail && (
                <span className="text-sm text-gray-600 hidden sm:block">
                  Welcome, {userEmail}
                </span>
              )}
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="performance" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger
              value="performance"
              className="flex items-center gap-2"
            >
              <BarChart3 className="w-4 h-4" />
              Player Performance
            </TabsTrigger>
            <TabsTrigger value="match" className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Live Match
            </TabsTrigger>
            <TabsTrigger value="crowd" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Crowd Monitor
            </TabsTrigger>
            <TabsTrigger value="reports" className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              Reports
            </TabsTrigger>
            <TabsTrigger value="video" className="flex items-center gap-2">
              <Video className="w-4 h-4" />
              Video Analysis
            </TabsTrigger>
          </TabsList>

          {/* Player Performance Tracker */}
          <TabsContent value="performance" className="space-y-6">
            <div className="flex flex-col lg:flex-row gap-6">
              {/* Search and Filters */}
              <Card className="lg:w-1/3">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Search className="w-5 h-5" />
                    Player Search & Filters
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">
                      Search Players
                    </label>
                    <Input
                      placeholder="Search by name..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">
                      Filter by Team
                    </label>
                    <Select
                      value={selectedTeam}
                      onValueChange={setSelectedTeam}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select team" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Teams</SelectItem>
                        <SelectItem value="Western Bulldogs">
                          Western Bulldogs
                        </SelectItem>
                        <SelectItem value="Richmond">Richmond</SelectItem>
                        <SelectItem value="Geelong">Geelong</SelectItem>
                        <SelectItem value="Melbourne">Melbourne</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3 max-h-60 overflow-y-auto">
                    {filteredPlayers.map((player) => (
                      <div
                        key={player.id}
                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                          selectedPlayer.id === player.id
                            ? "border-blue-500 bg-blue-50"
                            : "border-gray-200 hover:border-gray-300"
                        }`}
                        onClick={() => setSelectedPlayer(player)}
                      >
                        <div className="font-medium">{player.name}</div>
                        <div className="text-sm text-gray-600">
                          {player.team} • {player.position}
                        </div>
                        <div className="text-xs text-green-600 mt-1">
                          Efficiency: {player.efficiency}%
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Player Statistics */}
              <div className="lg:w-2/3 space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>Player Statistics - {selectedPlayer.name}</span>
                      <Badge variant="outline">{selectedPlayer.team}</Badge>
                    </CardTitle>
                    <CardDescription>{selectedPlayer.position}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">
                          {selectedPlayer.kicks}
                        </div>
                        <div className="text-sm text-gray-600">Kicks</div>
                      </div>
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">
                          {selectedPlayer.handballs}
                        </div>
                        <div className="text-sm text-gray-600">Handballs</div>
                      </div>
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">
                          {selectedPlayer.marks}
                        </div>
                        <div className="text-sm text-gray-600">Marks</div>
                      </div>
                      <div className="text-center p-4 bg-orange-50 rounded-lg">
                        <div className="text-2xl font-bold text-orange-600">
                          {selectedPlayer.tackles}
                        </div>
                        <div className="text-sm text-gray-600">Tackles</div>
                      </div>
                      <div className="text-center p-4 bg-red-50 rounded-lg">
                        <div className="text-2xl font-bold text-red-600">
                          {selectedPlayer.goals}
                        </div>
                        <div className="text-sm text-gray-600">Goals</div>
                      </div>
                      <div className="text-center p-4 bg-yellow-50 rounded-lg">
                        <div className="text-2xl font-bold text-yellow-600">
                          {selectedPlayer.efficiency}%
                        </div>
                        <div className="text-sm text-gray-600">Efficiency</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Player Comparison */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="w-5 h-5" />
                      Player Comparison
                    </CardTitle>
                    <CardDescription>
                      Compare {selectedPlayer.name} with another player
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-4">
                      <Select
                        value={comparisonPlayer.name}
                        onValueChange={(name) => {
                          const player = mockPlayers.find(
                            (p) => p.name === name,
                          );
                          if (player) setComparisonPlayer(player);
                        }}
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="Select player to compare" />
                        </SelectTrigger>
                        <SelectContent>
                          {mockPlayers
                            .filter((p) => p.id !== selectedPlayer.id)
                            .map((player) => (
                              <SelectItem key={player.id} value={player.name}>
                                {player.name} ({player.team})
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-4">
                      {["kicks", "handballs", "marks", "tackles", "goals"].map(
                        (stat) => (
                          <div key={stat} className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="capitalize">{stat}</span>
                              <span>
                                {
                                  selectedPlayer[
                                    stat as keyof typeof selectedPlayer
                                  ]
                                }{" "}
                                vs{" "}
                                {
                                  comparisonPlayer[
                                    stat as keyof typeof comparisonPlayer
                                  ]
                                }
                              </span>
                            </div>
                            <div className="flex gap-2">
                              <div className="flex-1">
                                <Progress
                                  value={
                                    ((selectedPlayer[
                                      stat as keyof typeof selectedPlayer
                                    ] as number) /
                                      Math.max(
                                        selectedPlayer[
                                          stat as keyof typeof selectedPlayer
                                        ] as number,
                                        comparisonPlayer[
                                          stat as keyof typeof comparisonPlayer
                                        ] as number,
                                      )) *
                                    100
                                  }
                                  className="h-2"
                                />
                                <div className="text-xs text-gray-600 mt-1">
                                  {selectedPlayer.name}
                                </div>
                              </div>
                              <div className="flex-1">
                                <Progress
                                  value={
                                    ((comparisonPlayer[
                                      stat as keyof typeof comparisonPlayer
                                    ] as number) /
                                      Math.max(
                                        selectedPlayer[
                                          stat as keyof typeof selectedPlayer
                                        ] as number,
                                        comparisonPlayer[
                                          stat as keyof typeof comparisonPlayer
                                        ] as number,
                                      )) *
                                    100
                                  }
                                  className="h-2"
                                />
                                <div className="text-xs text-gray-600 mt-1">
                                  {comparisonPlayer.name}
                                </div>
                              </div>
                            </div>
                          </div>
                        ),
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Current Match Insights */}
          <TabsContent value="match" className="space-y-6">
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
                        <div className="text-4xl font-bold text-blue-600">
                          72
                        </div>
                        <div className="text-lg">Carlton</div>
                      </div>
                      <div className="text-2xl text-gray-400">vs</div>
                      <div className="text-center">
                        <div className="text-4xl font-bold text-red-600">
                          68
                        </div>
                        <div className="text-lg">Adelaide</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mt-6">
                      <div className="text-center p-3 bg-gray-50 rounded">
                        <div className="text-lg font-semibold">324</div>
                        <div className="text-sm text-gray-600">
                          Total Disposals
                        </div>
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
          </TabsContent>

          {/* Crowd Monitoring Dashboard */}
          <TabsContent value="crowd" className="space-y-6">
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
                    <div className="text-2xl font-bold text-blue-600">
                      47,326
                    </div>
                    <div className="text-sm text-gray-600">
                      Average Attendance
                    </div>
                    <div className="text-xs text-green-600 mt-1">
                      +3.2% vs last season
                    </div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">89%</div>
                    <div className="text-sm text-gray-600">
                      Average Capacity
                    </div>
                    <div className="text-xs text-green-600 mt-1">
                      +5.1% vs last season
                    </div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      2:45 PM
                    </div>
                    <div className="text-sm text-gray-600">Peak Entry Time</div>
                    <div className="text-xs text-gray-600 mt-1">
                      15 min before bounce
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Report Download */}
          <TabsContent value="reports" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Player Performance Reports
                  </CardTitle>
                  <CardDescription>
                    Generate detailed analytics reports for players and teams
                  </CardDescription>
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
                          <SelectItem value="individual">
                            Individual Player Report
                          </SelectItem>
                          <SelectItem value="team">
                            Team Performance Report
                          </SelectItem>
                          <SelectItem value="comparison">
                            Player Comparison Report
                          </SelectItem>
                          <SelectItem value="season">
                            Season Summary Report
                          </SelectItem>
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
                          <SelectItem value="excel">
                            Excel Spreadsheet
                          </SelectItem>
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
                      {[
                        "Performance Statistics",
                        "Match Highlights",
                        "Trend Analysis",
                        "Comparison Charts",
                        "Heat Maps",
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

                  <Button className="w-full bg-gradient-to-r from-green-600 to-blue-600">
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
                  <CardDescription>
                    Generate crowd movement and density reports
                  </CardDescription>
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
                          <SelectItem value="density">
                            Crowd Density Report
                          </SelectItem>
                          <SelectItem value="movement">
                            Movement Pattern Report
                          </SelectItem>
                          <SelectItem value="capacity">
                            Capacity Utilization Report
                          </SelectItem>
                          <SelectItem value="safety">
                            Safety Analytics Report
                          </SelectItem>
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
                          <SelectItem value="season">
                            Season Analysis
                          </SelectItem>
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
                          <SelectItem value="northern">
                            Northern Stand
                          </SelectItem>
                          <SelectItem value="southern">
                            Southern Stand
                          </SelectItem>
                          <SelectItem value="eastern">Eastern Wing</SelectItem>
                          <SelectItem value="western">Western Wing</SelectItem>
                          <SelectItem value="premium">
                            Premium Seating
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <h4 className="font-medium">Analytics Features</h4>
                    <div className="space-y-2">
                      {[
                        "Heat Map Visualization",
                        "Peak Hour Analysis",
                        "Entry/Exit Patterns",
                        "Safety Compliance",
                        "Revenue Optimization",
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

                  <Button className="w-full bg-gradient-to-r from-green-600 to-blue-600">
                    <Download className="w-4 h-4 mr-2" />
                    Generate Crowd Report
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Recent Reports */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Reports</CardTitle>
                <CardDescription>
                  Download previously generated reports
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    {
                      name: "Weekly Player Performance - Round 15",
                      date: "2024-01-15",
                      size: "2.4 MB",
                      format: "PDF",
                    },
                    {
                      name: "Crowd Density Analysis - MCG",
                      date: "2024-01-14",
                      size: "1.8 MB",
                      format: "Excel",
                    },
                    {
                      name: "Season Summary Report",
                      date: "2024-01-12",
                      size: "5.2 MB",
                      format: "PDF",
                    },
                    {
                      name: "Player Comparison - Top 50",
                      date: "2024-01-10",
                      size: "3.1 MB",
                      format: "Excel",
                    },
                  ].map((report, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                    >
                      <div className="flex-1">
                        <div className="font-medium">{report.name}</div>
                        <div className="text-sm text-gray-600">
                          {report.date} • {report.size} • {report.format}
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Video Analytics Input */}
          <TabsContent value="video" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Upload className="w-5 h-5" />
                    Video Upload & Analysis
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
                      onChange={handleVideoFileSelect}
                      className="hidden"
                      id="video-upload-dashboard"
                    />
                    <label
                      htmlFor="video-upload-dashboard"
                      className="cursor-pointer"
                    >
                      <Video className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                      <div className="text-lg font-medium text-gray-700">
                        {selectedVideoFile
                          ? selectedVideoFile.name
                          : "Drop video files here"}
                      </div>
                      <div className="text-sm text-gray-500">
                        or click to browse
                      </div>
                      <div className="text-xs text-gray-400 mt-2">
                        Supports MP4, MOV, AVI • Max 500MB
                      </div>
                    </label>
                  </div>

                  {selectedVideoFile && (
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Video className="w-4 h-4 text-blue-600" />
                        <span className="font-medium">
                          {selectedVideoFile.name}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        Size:{" "}
                        {(selectedVideoFile.size / 1024 / 1024).toFixed(1)} MB
                      </div>
                    </div>
                  )}

                  {videoAnalysisError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="text-sm text-red-700">
                        {videoAnalysisError}
                      </div>
                    </div>
                  )}

                  {isVideoUploading && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Uploading video...</span>
                        <span>{videoUploadProgress}%</span>
                      </div>
                      <Progress value={videoUploadProgress} className="h-2" />
                    </div>
                  )}

                  {isVideoAnalyzing && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Analyzing video...</span>
                        <span>{videoAnalysisProgress}%</span>
                      </div>
                      <Progress value={videoAnalysisProgress} className="h-2" />
                    </div>
                  )}

                  {videoAnalysisComplete && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full" />
                        <span className="text-sm text-green-700 font-medium">
                          Analysis completed successfully!
                        </span>
                      </div>
                    </div>
                  )}

                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium">
                        Analysis Type
                      </label>
                      <Select
                        value={selectedAnalysisType}
                        onValueChange={setSelectedAnalysisType}
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
                          <SelectItem value="tactics">
                            Tactical Analysis
                          </SelectItem>
                          <SelectItem value="performance">
                            Performance Metrics
                          </SelectItem>
                          <SelectItem value="crowd">Crowd Reactions</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Focus Areas</label>
                      <div className="grid grid-cols-2 gap-2 mt-2">
                        {[
                          "Goals & Scoring",
                          "Defensive Actions",
                          "Player Movement",
                          "Ball Possession",
                          "Set Pieces",
                          "Injuries",
                        ].map((area) => (
                          <label
                            key={area}
                            className="flex items-center space-x-2"
                          >
                            <input
                              type="checkbox"
                              className="rounded"
                              checked={selectedFocusAreas.includes(area)}
                              onChange={(e) =>
                                handleFocusAreaChange(area, e.target.checked)
                              }
                            />
                            <span className="text-sm">{area}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>

                  <Button
                    className="w-full bg-gradient-to-r from-green-600 to-blue-600"
                    onClick={uploadAndAnalyzeVideo}
                    disabled={
                      !selectedVideoFile || isVideoUploading || isVideoAnalyzing
                    }
                  >
                    <Zap className="w-4 h-4 mr-2" />
                    {isVideoUploading
                      ? "Uploading..."
                      : isVideoAnalyzing
                        ? "Analyzing..."
                        : "Start Analysis"}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="w-5 h-5" />
                    Analysis Results
                  </CardTitle>
                  <CardDescription>
                    AI-generated insights from uploaded videos
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {!videoAnalysisComplete ? (
                    <div className="text-center py-8">
                      <Video className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        No Analysis Results Yet
                      </h3>
                      <p className="text-gray-600">
                        Upload and analyze a video to see detailed insights here
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">
                            Analysis Type:{" "}
                            {selectedAnalysisType === "highlights"
                              ? "Match Highlights"
                              : selectedAnalysisType === "player"
                                ? "Player Tracking"
                                : selectedAnalysisType === "tactics"
                                  ? "Tactical Analysis"
                                  : selectedAnalysisType === "performance"
                                    ? "Performance Metrics"
                                    : "Crowd Reactions"}
                          </span>
                          <Badge variant="secondary">Complete</Badge>
                        </div>
                        <div className="text-sm text-gray-600">
                          Video: {selectedVideoFile?.name}
                        </div>
                      </div>

                      {selectedFocusAreas.length > 0 && (
                        <div className="p-4 bg-green-50 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">
                              Focus Areas Analyzed
                            </span>
                            <Badge variant="secondary">
                              {selectedFocusAreas.length} areas
                            </Badge>
                          </div>
                          <div className="text-sm text-gray-600">
                            {selectedFocusAreas.join(", ")}
                          </div>
                        </div>
                      )}

                      <div className="p-4 bg-purple-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">
                            AI Insights Generated
                          </span>
                          <Badge variant="secondary">Ready</Badge>
                        </div>
                        <div className="text-sm text-gray-600">
                          {selectedAnalysisType === "highlights" &&
                            "Key moments and highlights identified"}
                          {selectedAnalysisType === "player" &&
                            "Player movements and performance tracked"}
                          {selectedAnalysisType === "tactics" &&
                            "Tactical patterns and strategies analyzed"}
                          {selectedAnalysisType === "performance" &&
                            "Performance metrics calculated"}
                          {selectedAnalysisType === "crowd" &&
                            "Crowd reactions and engagement measured"}
                        </div>
                      </div>
                    </div>
                  )}

                  <Separator />

                  <div className="space-y-3">
                    <h4 className="font-medium">Export Analysis</h4>
                    <div className="grid grid-cols-2 gap-2">
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-2" />
                        Video Clips
                      </Button>
                      <Button variant="outline" size="sm">
                        <FileText className="w-4 h-4 mr-2" />
                        Report
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Processing Queue */}
            <Card>
              <CardHeader>
                <CardTitle>Processing Queue</CardTitle>
                <CardDescription>
                  Track the status of your video analysis requests
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    {
                      name: "Round_15_Carlton_vs_Adelaide.mp4",
                      status: "Completed",
                      progress: 100,
                      time: "2 min ago",
                    },
                    {
                      name: "Training_Session_January_14.mov",
                      status: "Processing",
                      progress: 67,
                      time: "5 min remaining",
                    },
                    {
                      name: "Match_Highlights_Compilation.mp4",
                      status: "Queued",
                      progress: 0,
                      time: "Waiting",
                    },
                  ].map((item, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="font-medium">{item.name}</div>
                        <div className="text-sm text-gray-600">{item.time}</div>
                        {item.progress > 0 && item.progress < 100 && (
                          <Progress
                            value={item.progress}
                            className="mt-2 h-2"
                          />
                        )}
                      </div>
                      <Badge
                        variant={
                          item.status === "Completed"
                            ? "default"
                            : item.status === "Processing"
                              ? "secondary"
                              : "outline"
                        }
                      >
                        {item.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
