import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  Activity,
  Users,
  BarChart3,
  Download,
  Video,
  Settings,
  LogOut,
} from "lucide-react";
import MobileNavigation from "@/components/MobileNavigation";
import { getCurrentUser, logout } from "@/lib/auth";
import { useDashboardPlayers } from "@/hooks/useDashboardPlayers";
import { useVideoAnalysis } from "@/hooks/useVideoAnalysis";
import PlayerPerformanceTab from "@/components/dashboard/PlayerPerformanceTab";
import LiveMatchTab from "@/components/dashboard/LiveMatchTab";
import CrowdMonitorTab from "@/components/dashboard/CrowdMonitorTab";
import ReportsTab from "@/components/dashboard/ReportsTab";
import VideoAnalysisTab from "@/components/dashboard/VideoAnalysisTab";
import AnalysisResultsDialog from "@/components/dashboard/AnalysisResultsDialog";
import BackToTopButton from "@/components/dashboard/BackToTopButton";

// Feature flag to disable live match features
const ENABLE_LIVE_FEATURES = false;

/**
 * Home page. Each tab lives in client/components/dashboard/; state that must survive
 * tab switches (player selection, video uploads/queue) lives in the hooks above.
 */
export default function AFLDashboard() {
  const navigate = useNavigate();
  const [isLive, setIsLive] = useState(true);
  const [userEmail, setUserEmail] = useState("");
  const playersState = useDashboardPlayers();
  const video = useVideoAnalysis();

  // Load current user info for the welcome message.
  // Access control itself is handled by ProtectedRoute in App.tsx,
  // so this component no longer needs its own auth gate.
  useEffect(() => {
    const user = getCurrentUser();
    if (user) {
      setUserEmail(user.email);
    }
  }, []);

  // Logout function - clears the real auth session (accessToken + user)
  // and sends the user to /login via a full page reload.
  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <MobileNavigation />

      <div className="lg:ml-64 pb-16 lg:pb-0">
        <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-30">
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
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate("/settings")}
                >
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
          <Tabs defaultValue="video" className="space-y-6">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger
                value="performance"
                className="flex items-center gap-2"
              >
                <BarChart3 className="w-4 h-4" />
                Player Performance
              </TabsTrigger>
              {ENABLE_LIVE_FEATURES && (
                <TabsTrigger value="match" className="flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  Live Match
                </TabsTrigger>
              )}
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

            <TabsContent value="performance" className="space-y-6">
              <PlayerPerformanceTab playersState={playersState} />
            </TabsContent>

            {ENABLE_LIVE_FEATURES && (
              <TabsContent value="match" className="space-y-6">
                <LiveMatchTab />
              </TabsContent>
            )}

            <TabsContent value="crowd" className="space-y-6">
              <CrowdMonitorTab />
            </TabsContent>

            <TabsContent value="reports" className="space-y-6">
              <ReportsTab />
            </TabsContent>

            <TabsContent value="video" className="space-y-6">
              <VideoAnalysisTab video={video} />
            </TabsContent>
          </Tabs>
        </div>

        <AnalysisResultsDialog video={video} />
      </div>
      <BackToTopButton />
    </div>
  );
}
