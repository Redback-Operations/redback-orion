import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart3, Users, Download, Target, Video } from "lucide-react";
import DashboardHeader from "@/components/dashboard/DashboardHeader";
import PlayerPerformanceTab from "@/components/dashboard/tabs/PlayerPerformanceTab";
import CrowdMonitorTab from "@/components/dashboard/tabs/CrowdMonitorTab";
import VideoAnalysisTab from "@/components/dashboard/tabs/VideoAnalysisTab";
import TeamMatchTab from "@/components/dashboard/tabs/TeamMatchTab";
import ReportsTab from "@/components/dashboard/tabs/ReportsTab";
import { useDashboardState } from "@/hooks/useDashboardState";
import { listUploads } from "@/lib/video";

export default function AFLDashboard() {
  const navigate = useNavigate();
  const dashboardState = useDashboardState();

  // 🔹 Track active tab
  const [activeTab, setActiveTab] = useState("video");

  // 🔹 Track which upload is selected
  const [selectedUploadId, setSelectedUploadId] = useState<string | null>(null);

  // 🔹 Derived: full selected upload object
  const selectedUpload =
    dashboardState.completedAnalyses.find((u) => u.id === selectedUploadId) ||
    null;

  // -------------------------------
  // Fetch past uploads → mark as completed
  // -------------------------------
  useEffect(() => {
    async function fetchUploads() {
      try {
        const uploads = await listUploads();
        dashboardState.setCompletedAnalyses(
          uploads.map((u: any) => ({
            id: u.id,
            original_filename: u.original_filename,
            created_at: u.created_at,
            status: "Completed",
          }))
        );

        // Auto-select the first upload if exists
        if (uploads.length > 0 && !selectedUploadId) {
          setSelectedUploadId(uploads[0].id);
        }
      } catch (err) {
        console.error("⚠️ Failed to fetch uploads:", err);
      }
    }
    fetchUploads();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userEmail");
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-orange-50">
      <DashboardHeader
        isLive={dashboardState.isLive}
        userEmail={dashboardState.userEmail}
        onLogout={handleLogout}
      />

      <div className="container mx-auto px-4 py-6">
        {/* 🔹 Controlled Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="performance" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Player Performance
            </TabsTrigger>
            <TabsTrigger value="crowd" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Crowd Monitor
            </TabsTrigger>
            <TabsTrigger value="reports" className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              Reports
            </TabsTrigger>
            <TabsTrigger value="team" className="flex items-center gap-2 hidden">
              <Target className="w-4 h-4" />
              Team Match
            </TabsTrigger>
            <TabsTrigger value="video" className="flex items-center gap-2">
              <Video className="w-4 h-4" />
              Video Analysis
            </TabsTrigger>
          </TabsList>

          <TabsContent value="performance">
            <PlayerPerformanceTab upload={selectedUpload} />
          </TabsContent>

          <TabsContent value="crowd">
            <CrowdMonitorTab upload={selectedUpload} />
          </TabsContent>

          <TabsContent value="reports">
            <ReportsTab />
          </TabsContent>

          <TabsContent value="team" className="hidden">
            <TeamMatchTab
              teamA={dashboardState.teamA}
              setTeamA={dashboardState.setTeamA}
              teamB={dashboardState.teamB}
              setTeamB={dashboardState.setTeamB}
              teamCompare={dashboardState.teamCompare}
              teamTeams={dashboardState.availableTeams}
            />
          </TabsContent>

          <TabsContent value="video">
            <VideoAnalysisTab
              selectedVideoFile={dashboardState.selectedVideoFile}
              videoAnalysisError={dashboardState.videoAnalysisError}
              isVideoUploading={dashboardState.isVideoUploading}
              videoUploadProgress={dashboardState.videoUploadProgress}
              isVideoAnalyzing={dashboardState.isVideoAnalyzing}
              onFileSelect={(e) => {
                const file = e.target.files?.[0];
                if (file) dashboardState.setSelectedVideoFile(file);
              }}
              onAnalyze={(file, runPlayer, runCrowd) =>
                dashboardState.handleAnalyze(file, runPlayer, runCrowd)
              }

              completedAnalyses={dashboardState.completedAnalyses}
              setCompletedAnalyses={dashboardState.setCompletedAnalyses}
              setActiveTab={setActiveTab} // ✅ switch tab
              setSelectedUploadId={setSelectedUploadId} // ✅ choose video
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
