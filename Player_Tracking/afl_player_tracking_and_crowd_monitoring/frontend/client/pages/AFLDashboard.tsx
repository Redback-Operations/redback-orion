import React from "react";
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

export default function AFLDashboard() {
  const navigate = useNavigate();
  const dashboardState = useDashboardState();

  const handleLogout = () => {
    // Clear any stored authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('userEmail');
    navigate('/login');
  };

  // Video analysis handlers
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      dashboardState.setSelectedVideoFile(file);
    }
  };

  const handleFocusAreaChange = (area: string, checked: boolean) => {
    if (checked) {
      dashboardState.setSelectedFocusAreas([...dashboardState.selectedFocusAreas, area]);
    } else {
      dashboardState.setSelectedFocusAreas(
        dashboardState.selectedFocusAreas.filter(a => a !== area)
      );
    }
  };

  const handleStartAnalysis = () => {
    if (!dashboardState.selectedVideoFile) return;
    
    // Simulate video upload and analysis
    dashboardState.setIsVideoUploading(true);
    dashboardState.setVideoUploadProgress(0);
    
    const uploadInterval = setInterval(() => {
      dashboardState.setVideoUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(uploadInterval);
          dashboardState.setIsVideoUploading(false);
          dashboardState.setIsVideoAnalyzing(true);
          dashboardState.setVideoAnalysisProgress(0);
          
          // Start analysis simulation
          const analysisInterval = setInterval(() => {
            dashboardState.setVideoAnalysisProgress(prev => {
              if (prev >= 100) {
                clearInterval(analysisInterval);
                dashboardState.setIsVideoAnalyzing(false);
                dashboardState.setVideoAnalysisComplete(true);
                return 100;
              }
              return prev + 10;
            });
          }, 500);
          
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleDownloadVideoClips = () => {
    // Implement video clips download
    console.log('Downloading video clips...');
  };

  const handleDownloadReport = () => {
    // Implement report download
    console.log('Downloading report...');
  };

  const handleRetryProcessing = (id: string) => {
    // Implement retry logic
    console.log('Retrying processing for:', id);
  };

  const handleCancelProcessing = (id: string) => {
    // Implement cancel logic
    console.log('Cancelling processing for:', id);
  };

  const disabledStart = !dashboardState.selectedVideoFile || 
                       dashboardState.isVideoUploading || 
                       dashboardState.isVideoAnalyzing;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-orange-50">
      <DashboardHeader 
        isLive={dashboardState.isLive} 
        userEmail={dashboardState.userEmail} 
        onLogout={handleLogout} 
      />

      <div className="container mx-auto px-4 py-6">
        <Tabs defaultValue="performance" className="space-y-6">
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
            <TabsTrigger value="team" className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              Team Match
            </TabsTrigger>
            <TabsTrigger value="video" className="flex items-center gap-2">
              <Video className="w-4 h-4" />
              Video Analysis
            </TabsTrigger>
          </TabsList>

          <TabsContent value="performance">
            <PlayerPerformanceTab
              selectedPlayer={dashboardState.selectedPlayer}
              setSelectedPlayer={dashboardState.setSelectedPlayer}
              comparisonPlayer={dashboardState.comparisonPlayer}
              setComparisonPlayer={dashboardState.setComparisonPlayer}
              searchTerm={dashboardState.searchTerm}
              setSearchTerm={dashboardState.setSearchTerm}
              selectedTeam={dashboardState.selectedTeam}
              setSelectedTeam={dashboardState.setSelectedTeam}
              filteredPlayers={dashboardState.filteredPlayers}
              availableTeams={dashboardState.availableTeams}
              performanceTrendData={dashboardState.performanceTrendData}
              playerComparisonData={dashboardState.playerComparisonData}
            />
          </TabsContent>

          <TabsContent value="crowd">
            <CrowdMonitorTab />
          </TabsContent>

          <TabsContent value="reports">
            <ReportsTab />
          </TabsContent>

          <TabsContent value="team">
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
              videoAnalysisProgress={dashboardState.videoAnalysisProgress}
              selectedAnalysisType={dashboardState.selectedAnalysisType}
              setSelectedAnalysisType={dashboardState.setSelectedAnalysisType}
              selectedFocusAreas={dashboardState.selectedFocusAreas}
              onFocusAreaChange={handleFocusAreaChange}
              onFileSelect={handleFileSelect}
              onStart={handleStartAnalysis}
              disabledStart={disabledStart}
              videoAnalysisComplete={dashboardState.videoAnalysisComplete}
              selectedVideoFileName={dashboardState.selectedVideoFile?.name || ''}
              onDownloadVideoClips={handleDownloadVideoClips}
              onDownloadReport={handleDownloadReport}
              processingQueue={dashboardState.processingQueue}
              onRetryProcessing={handleRetryProcessing}
              onCancelProcessing={handleCancelProcessing}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}