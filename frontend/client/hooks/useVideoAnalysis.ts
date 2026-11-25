import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { downloadText } from "@/lib/download";
import { BACKEND_URL } from "@/lib/config";
import { getAccessToken, isDemoToken } from "@/lib/auth";
import type {
  BackendStatusResponse,
  ProcessingQueueItem,
} from "@/components/dashboard/types";
import {
  convertBackendDataToHTML,
  convertBackendDataToText,
  generateDashboardInsights,
  generateDashboardPDF,
} from "@/components/dashboard/reportUtils";

/**
 * Upload, backend polling, processing queue and export logic for the Video Analysis tab.
 * Lives above the tabs so uploads keep progressing while the user is on another tab.
 */
export function useVideoAnalysis() {
  const navigate = useNavigate();
  const [activeQueueItemId, setActiveQueueItemId] = useState<string | null>(
    null,
  );

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
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [selectedAnalysisType, setSelectedAnalysisType] =
    useState("highlights");
  const [selectedFocusAreas, setSelectedFocusAreas] = useState<string[]>([]);

  // Analysis view modal state
  const [viewModalOpen, setViewModalOpen] = useState(false);
  const [selectedAnalysisItem, setSelectedAnalysisItem] = useState<any>(null);

  // Processing Queue state - starts empty, only shows actual uploads
  const [processingQueue, setProcessingQueue] = useState<ProcessingQueueItem[]>(
    [],
  );

  const retryProcessing = (itemId: string) => {
    setProcessingQueue((prev) =>
      prev.map((item) =>
        item.id === itemId
          ? {
              ...item,
              status: "queued",
              progress: 0,
              processingStage: "queue_waiting",
              retryCount: item.retryCount + 1,
              estimatedCompletion: new Date(
                Date.now() + Math.random() * 3600000 + 1800000,
              ).toISOString(),
              // If this was a UI-controlled item, it should remain so after retry
              isUIControlled: item.isUIControlled || false,
            }
          : item,
      ),
    );
  };

  const removeFromQueue = (itemId: string) => {
    setProcessingQueue((prev) => prev.filter((item) => item.id !== itemId));
  };
  useEffect(() => {
    if (!currentJobId) return;

    const interval = setInterval(async () => {
      try {
        const token = getAccessToken();
        if (!token) {
          throw new Error("Missing login token");
        }

        const response = await fetch(`${BACKEND_URL}/status/${currentJobId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        const data: BackendStatusResponse = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || data.error || "Status check failed");
        }

        setVideoAnalysisProgress((prev) =>
          data.status === "processing" ? Math.min(prev + 10, 90) : 100,
        );
        setProcessingQueue((prev) =>
          prev.map((item) =>
            item.id === currentJobId || item.id === activeQueueItemId
              ? {
                  ...item,
                  id: currentJobId,
                  status:
                    data.status === "processing"
                      ? "analyzing"
                      : data.status === "failed"
                        ? "failed"
                        : "completed",
                  progress:
                    data.status === "processing"
                      ? Math.min(item.progress + 10, 90)
                      : 100,
                  processingStage:
                    data.status === "processing"
                      ? "video_analysis"
                      : "analysis_complete",
                  completedTime:
                    data.status === "processing"
                      ? item.completedTime
                      : new Date().toISOString(),
                  estimatedCompletion:
                    data.status === "processing"
                      ? item.estimatedCompletion
                      : null,
                }
              : item,
          ),
        );

        if (data.status !== "processing") {
          clearInterval(interval);
          setCurrentJobId(null);
          setIsVideoAnalyzing(false);
          setVideoAnalysisComplete(
            data.status === "done" || data.status === "partial",
          );
          if (data.error) {
            setVideoAnalysisError(data.error);
          }
          if (data.results?.crowd) {
            navigate(`/crowd-monitor?jobId=${encodeURIComponent(data.job_id)}`);
          }
        }
      } catch (error) {
        console.error("Polling error:", error);
        clearInterval(interval);
        setIsVideoAnalyzing(false);
        setVideoAnalysisError(
          error instanceof Error ? error.message : "Polling failed",
        );
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [activeQueueItemId, currentJobId, navigate]);

  // View analysis results for a queue item
  const handleViewAnalysis = (item: any) => {
    setSelectedAnalysisItem(item);
    setViewModalOpen(true);
  };

  // Download analysis report for a queue item
  const handleDownloadFromQueue = async (
    item: any,
    format: "pdf" | "json" | "txt" = "pdf",
  ) => {
    try {
      // Generate analysis data for this specific item
      const analysisId = item.id;
      const backendData = {
        analysisId,
        timestamp: item.completedTime || item.uploadTime,
        videoFile: {
          name: item.name,
          duration: item.duration,
          size: item.size,
          resolution: "1920x1080",
          framerate: "30fps",
        },
        analysisType: item.analysisType,
        focusAreas: [], // Queue items don't have focus areas stored
        processingTime: Math.floor(Math.random() * 300 + 120),
        results: {
          playerPerformance: [
            {
              playerId: "p001",
              name: "Marcus Bontempelli",
              team: "Western Bulldogs",
              position: "Midfielder",
              statistics: {
                speed: { max: 32.4, average: 24.8, unit: "km/h" },
                distance: { total: 12.8, sprints: 2.3, unit: "km" },
                touches: { total: 28, effective: 24, efficiency: 85.7 },
                goals: 2,
                assists: 3,
                tackles: 6,
                marks: 8,
                disposals: 31,
                timeOnGround: 87.5,
              },
            },
            {
              playerId: "p002",
              name: "Patrick Cripps",
              team: "Carlton",
              position: "Midfielder",
              statistics: {
                speed: { max: 29.8, average: 22.1, unit: "km/h" },
                distance: { total: 13.2, sprints: 1.8, unit: "km" },
                touches: { total: 35, effective: 31, efficiency: 88.6 },
                goals: 1,
                assists: 5,
                tackles: 9,
                marks: 6,
                disposals: 34,
                timeOnGround: 92.3,
              },
            },
          ],
          crowdAnalysis: {
            totalAttendance: 47832,
            capacity: 50000,
            utilizationRate: 95.7,
            sections: [
              {
                sectionId: "north_stand",
                name: "Northern Stand",
                attendance: 14250,
                capacity: 15000,
                density: 95.0,
                noiseLevel: { peak: 95.2, average: 78.4, unit: "dB" },
              },
              {
                sectionId: "south_stand",
                name: "Southern Stand",
                attendance: 11680,
                capacity: 12000,
                density: 97.3,
                noiseLevel: { peak: 92.8, average: 76.9, unit: "dB" },
              },
            ],
          },
          highlights: [
            {
              timestamp: "00:03:45",
              duration: 15,
              type: "goal",
              description: "Opening goal with crowd eruption",
              players: ["Marcus Bontempelli"],
              confidence: 0.94,
            },
          ],
          metadata: {
            confidence: 0.923,
            processingVersion: "2.1.3",
            qualityScore: 8.7,
          },
        },
      };

      if (format === "json") {
        // Download raw JSON data
        const jsonContent = JSON.stringify(backendData, null, 2);
        const blob = new Blob([jsonContent], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${item.name.replace(/\.[^/.]+$/, "")}_Analysis.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else if (format === "pdf") {
        // Generate PDF from backend data
        const htmlContent = convertBackendDataToHTML(backendData);
        generateDashboardPDF(
          htmlContent,
          `${item.name.replace(/\.[^/.]+$/, "")}_Analysis`,
        );
      } else {
        // Generate TXT from backend data
        const textContent = convertBackendDataToText(backendData);
        downloadText(
          textContent,
          `${item.name.replace(/\.[^/.]+$/, "")}_Analysis`,
        );
      }
    } catch (error) {
      console.error("Error downloading analysis:", error);
      alert("Failed to download analysis. Please try again.");
    }
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

    const token = getAccessToken();
    if (!token || isDemoToken(token)) {
      setVideoAnalysisError("Please sign in before uploading");
      navigate("/login");
      return;
    }

    try {
      setVideoAnalysisError(null);
      setVideoAnalysisComplete(false);
      setIsVideoUploading(true);
      setIsVideoAnalyzing(false);
      setVideoUploadProgress(10);

      // Create queue item immediately when upload starts
      const newQueueItem = {
        id: `pq_${Date.now()}`,
        name: selectedVideoFile.name,
        analysisType:
          selectedAnalysisType === "highlights"
            ? "Highlight Generation"
            : selectedAnalysisType === "player"
              ? "Player Tracking"
              : selectedAnalysisType === "tactics"
                ? "Tactical Analysis"
                : selectedAnalysisType === "performance"
                  ? "Performance Analysis"
                  : "Crowd Analysis",
        status: "uploading" as const,
        progress: 0,
        duration: `${Math.floor(Math.random() * 60 + 30)}:${Math.floor(
          Math.random() * 60,
        )
          .toString()
          .padStart(2, "0")}`,
        size: `${(selectedVideoFile.size / (1024 * 1024)).toFixed(1)} MB`,
        uploadTime: new Date().toISOString(),
        completedTime: null,
        estimatedCompletion: new Date(
          Date.now() + Math.random() * 600000 + 300000,
        ).toISOString(), // 5-15 minutes
        priority: (selectedFocusAreas.length > 2
          ? "high"
          : Math.random() > 0.5
            ? "medium"
            : "low") as "low" | "medium" | "high",
        userId: "current_user",
        processingStage: "file_upload",
        errorCount: 0,
        retryCount: 0,
        isUIControlled: true, // Flag to indicate this item is controlled by UI flow
      };

      // Add to processing queue immediately
      setProcessingQueue((prev) => [newQueueItem, ...prev]);
      setActiveQueueItemId(newQueueItem.id);

      const formData = new FormData();
      formData.append("file", selectedVideoFile);

      const response = await fetch(`${BACKEND_URL}/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setCurrentJobId(data.job_id);
      setIsVideoUploading(false);
      setIsVideoAnalyzing(true);
      setVideoUploadProgress(100);
      setVideoAnalysisProgress(15);

      setProcessingQueue((prev) =>
        prev.map((item) =>
          item.id === newQueueItem.id
            ? {
                ...item,
                id: data.job_id,
                status: "analyzing",
                progress: 15,
                processingStage: "video_analysis",
              }
            : item,
        ),
      );
    } catch (error) {
      setIsVideoUploading(false);
      setIsVideoAnalyzing(false);
      setVideoAnalysisError(
        error instanceof Error ? error.message : "Upload failed",
      );

      // Mark the queue item as failed if there was an error
      setProcessingQueue((prev) =>
        prev.map((item) =>
          item.id === activeQueueItemId ||
          (item.name === selectedVideoFile?.name && item.status === "uploading")
            ? {
                ...item,
                status: "failed",
                processingStage: "upload_error",
                errorCount: 1,
              }
            : item,
        ),
      );
    }
  };

  // Simulate getting JSON data from backend
  const fetchBackendAnalysisData = async (analysisId: string) => {
    // Simulate backend JSON response
    return {
      analysisId,
      timestamp: new Date().toISOString(),
      videoFile: {
        name: selectedVideoFile?.name || "sample_video.mp4",
        duration: "02:15:30",
        size: "1.8 GB",
        resolution: "1920x1080",
        framerate: "30fps",
      },
      analysisType: selectedAnalysisType,
      focusAreas: selectedFocusAreas,
      processingTime: Math.floor(Math.random() * 300 + 120),
      results: {
        playerPerformance: [
          {
            playerId: "p001",
            name: "Marcus Bontempelli",
            team: "Western Bulldogs",
            position: "Midfielder",
            statistics: {
              speed: { max: 32.4, average: 24.8, unit: "km/h" },
              distance: { total: 12.8, sprints: 2.3, unit: "km" },
              touches: { total: 28, effective: 24, efficiency: 85.7 },
              goals: 2,
              assists: 3,
              tackles: 6,
              marks: 8,
              disposals: 31,
              timeOnGround: 87.5,
            },
          },
          {
            playerId: "p002",
            name: "Patrick Cripps",
            team: "Carlton",
            position: "Midfielder",
            statistics: {
              speed: { max: 29.8, average: 22.1, unit: "km/h" },
              distance: { total: 13.2, sprints: 1.8, unit: "km" },
              touches: { total: 35, effective: 31, efficiency: 88.6 },
              goals: 1,
              assists: 5,
              tackles: 9,
              marks: 6,
              disposals: 34,
              timeOnGround: 92.3,
            },
          },
        ],
        crowdAnalysis: {
          totalAttendance: 47832,
          capacity: 50000,
          utilizationRate: 95.7,
          sections: [
            {
              sectionId: "north_stand",
              name: "Northern Stand",
              attendance: 14250,
              capacity: 15000,
              density: 95.0,
              noiseLevel: { peak: 95.2, average: 78.4, unit: "dB" },
            },
            {
              sectionId: "south_stand",
              name: "Southern Stand",
              attendance: 11680,
              capacity: 12000,
              density: 97.3,
              noiseLevel: { peak: 92.8, average: 76.9, unit: "dB" },
            },
          ],
        },
        highlights: [
          {
            timestamp: "00:03:45",
            duration: 15,
            type: "goal",
            description: "Opening goal with crowd eruption",
            players: ["Marcus Bontempelli"],
            confidence: 0.94,
          },
        ],
        metadata: {
          confidence: 0.923,
          processingVersion: "2.1.3",
          qualityScore: 8.7,
        },
      },
    };
  };

  // Download handlers for reports with backend JSON processing
  const handleDownloadReport = async (
    format: "pdf" | "json" | "txt" = "txt",
  ) => {
    if (!videoAnalysisComplete || !selectedVideoFile) {
      alert("Please complete video analysis first");
      return;
    }

    try {
      // Fetch JSON data from backend
      const analysisId = `analysis_${Date.now()}`;
      const backendData = await fetchBackendAnalysisData(analysisId);

      if (format === "json") {
        // Download raw JSON data
        const jsonContent = JSON.stringify(backendData, null, 2);
        const blob = new Blob([jsonContent], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `AFL_Analysis_${analysisId}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else if (format === "pdf") {
        // Generate PDF from backend data
        const htmlContent = convertBackendDataToHTML(backendData);
        generateDashboardPDF(htmlContent, `AFL_Analysis_${analysisId}`);
      } else {
        // Generate TXT from backend data
        const textContent = convertBackendDataToText(backendData);
        downloadText(textContent, `AFL_Analysis_${analysisId}`);
      }
    } catch (error) {
      console.error("Error generating report:", error);
      alert("Failed to generate report. Please try again.");
    }
  };

  const handleDownloadVideoClips = () => {
    if (!videoAnalysisComplete) {
      alert("Please complete video analysis first");
      return;
    }

    const insights = generateDashboardInsights();
    const clipEvents = [
      {
        time: "00:03:45",
        event: "Opening Goal",
        player: insights.playerStats[0].name,
        speed: insights.playerStats[0].speed,
        crowd: "Explosive reaction",
      },
      {
        time: "00:18:23",
        event: "Spectacular Mark",
        player: insights.playerStats[1].name,
        speed: insights.playerStats[1].speed,
        crowd: "Standing ovation",
      },
      {
        time: "00:34:56",
        event: "Crucial Tackle",
        player: insights.playerStats[2].name,
        speed: insights.playerStats[2].speed,
        crowd: "Defensive roar",
      },
      {
        time: "00:52:12",
        event: "Assist Play",
        player: insights.playerStats[3].name,
        speed: insights.playerStats[3].speed,
        crowd: "Building excitement",
      },
      {
        time: "01:08:34",
        event: "Match Winner",
        player: insights.playerStats[4].name,
        speed: insights.playerStats[4].speed,
        crowd: "Stadium eruption",
      },
      {
        time: "01:15:45",
        event: "Final Siren",
        player: "Multiple Players",
        speed: "N/A",
        crowd: "Celebration frenzy",
      },
    ];

    const clipsData = `AFL ANALYTICS VIDEO CLIPS EXPORT

Generated: ${new Date().toLocaleString()}
Source Video: ${selectedVideoFile?.name}
Analysis Type: ${
      selectedAnalysisType === "highlights"
        ? "Match Highlights"
        : selectedAnalysisType === "player"
          ? "Player Tracking"
          : selectedAnalysisType === "tactics"
            ? "Tactical Analysis"
            : selectedAnalysisType === "performance"
              ? "Performance Metrics"
              : "Crowd Reactions"
    }

════════════════════���══════════════════════════════��═══════

EXTRACTED VIDEO CLIPS WITH INSIGHTS
===================================
${clipEvents
  .map(
    (clip, index) => `
Clip ${index + 1}: ${clip.event}
  • Timestamp: ${clip.time}
  • Featured Player: ${clip.player}
  • Player Speed: ${clip.speed} km/h
  • Duration: ${Math.floor(Math.random() * 25 + 10)}s
  • Crowd Reaction: ${clip.crowd}
  • Stands Most Active: ${insights.crowdDensity[Math.floor(Math.random() * insights.crowdDensity.length)].section}
  • Noise Level: ${(85 + Math.random() * 15).toFixed(1)} dB
`,
  )
  .join("")}

CLIP ANALYSIS SUMMARY
====================
• Total clips identified: ${clipEvents.length}
• Total duration: ${clipEvents.reduce((sum, _, index) => sum + Math.floor(Math.random() * 25 + 10), 0)} seconds
• Average crowd noise: ${(80 + Math.random() * 20).toFixed(1)} dB
• Most active stand: ${
      insights.crowdDensity.reduce((max, section) =>
        parseFloat(section.density) > parseFloat(max.density) ? section : max,
      ).section
    }
• Player tracking accuracy: 97.2%

CROWD RESPONSE CORRELATION
==========================
${clipEvents
  .map(
    (clip, index) => `
${clip.event} (${clip.time}):
  Crowd Response Intensity: ${(7 + Math.random() * 3).toFixed(1)}/10
  Stands Reacting: ${Math.floor(Math.random() * 3 + 3)} of ${insights.crowdDensity.length}
  Duration of Reaction: ${Math.floor(Math.random() * 15 + 5)}s
`,
  )
  .join("")}

EXPORT DETAILS
==============
• Export Format: Metadata Analysis (TXT)
• Processing Time: ${Math.floor(Math.random() * 3 + 1)} minutes
• Clips Ready for Download: ${clipEvents.length}
• Analysis Confidence: 94.8%

NOTE: In a production environment, this would package actual video clip files.
Currently providing comprehensive metadata and analysis for demonstration.

Generated by AFL Analytics Platform - Advanced Video Intelligence
Export ID: ${Date.now()}-${Math.random().toString(36).substr(2, 9)}
`;

    downloadText(clipsData, `AFL_Video_Clips_${Date.now()}`);
  };

  return {
    selectedVideoFile,
    isVideoUploading,
    videoUploadProgress,
    isVideoAnalyzing,
    videoAnalysisProgress,
    videoAnalysisComplete,
    videoAnalysisError,
    selectedAnalysisType,
    setSelectedAnalysisType,
    selectedFocusAreas,
    handleVideoFileSelect,
    handleFocusAreaChange,
    uploadAndAnalyzeVideo,
    handleDownloadReport,
    handleDownloadVideoClips,
    processingQueue,
    retryProcessing,
    removeFromQueue,
    handleViewAnalysis,
    handleDownloadFromQueue,
    viewModalOpen,
    setViewModalOpen,
    selectedAnalysisItem,
  };
}

export type VideoAnalysisState = ReturnType<typeof useVideoAnalysis>;
