import type { VideoAnalysisState } from "@/hooks/useVideoAnalysis";
import ProcessingQueue from "./ProcessingQueue";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Download, Upload, Video, Eye, Zap, FileText } from "lucide-react";

export default function VideoAnalysisTab({
  video,
}: {
  video: VideoAnalysisState;
}) {
  const {
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
  } = video;

  return (
    <>
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
                <div className="text-sm text-gray-500">or click to browse</div>
                <div className="text-xs text-gray-400 mt-2">
                  Supports MP4, MOV, AVI • Max 500MB
                </div>
              </label>
            </div>

            {selectedVideoFile && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <Video className="w-4 h-4 text-blue-600" />
                  <span className="font-medium">{selectedVideoFile.name}</span>
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  Size: {(selectedVideoFile.size / 1024 / 1024).toFixed(1)} MB
                </div>
              </div>
            )}

            {videoAnalysisError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="text-sm text-red-700">{videoAnalysisError}</div>
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
                <label className="text-sm font-medium">Analysis Type</label>
                <Select
                  value={selectedAnalysisType}
                  onValueChange={setSelectedAnalysisType}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="highlights">Match Highlights</SelectItem>
                    <SelectItem value="player">Player Tracking</SelectItem>
                    <SelectItem value="tactics">Tactical Analysis</SelectItem>
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
                    <label key={area} className="flex items-center space-x-2">
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
                      <span className="font-medium">Focus Areas Analyzed</span>
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
                    <span className="font-medium">AI Insights Generated</span>
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
              <p className="text-sm text-gray-600">
                Download analysis data from backend in different formats
              </p>
              <div className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownloadVideoClips}
                  disabled={!videoAnalysisComplete}
                  className="w-full"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Video Clips
                </Button>
                <div className="grid grid-cols-3 gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownloadReport("pdf")}
                    disabled={!videoAnalysisComplete}
                  >
                    <FileText className="w-4 h-4 mr-1" />
                    PDF
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownloadReport("json")}
                    disabled={!videoAnalysisComplete}
                  >
                    <Download className="w-4 h-4 mr-1" />
                    JSON
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownloadReport("txt")}
                    disabled={!videoAnalysisComplete}
                  >
                    <FileText className="w-4 h-4 mr-1" />
                    TXT
                  </Button>
                </div>
                <div className="text-xs text-gray-500 mt-2 space-y-1">
                  <div>
                    <strong>PDF:</strong> Formatted report for printing/sharing
                  </div>
                  <div>
                    <strong>JSON:</strong> Raw backend data for developers
                  </div>
                  <div>
                    <strong>TXT:</strong> Plain text summary for analysis
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <ProcessingQueue video={video} />
    </>
  );
}
