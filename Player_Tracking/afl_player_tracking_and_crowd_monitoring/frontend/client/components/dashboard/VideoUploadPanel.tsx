import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Video, Upload, Zap } from "lucide-react";

export default function VideoUploadPanel({
  selectedVideoFile,
  videoAnalysisError,
  isVideoUploading,
  videoUploadProgress,
  isVideoAnalyzing,
  videoAnalysisProgress,
  selectedAnalysisType,
  setSelectedAnalysisType,
  selectedFocusAreas,
  onFocusAreaChange,
  onFileSelect,
  onStart,
  disabledStart,
}: {
  selectedVideoFile: File | null;
  videoAnalysisError: string | null;
  isVideoUploading: boolean;
  videoUploadProgress: number;
  isVideoAnalyzing: boolean;
  videoAnalysisProgress: number;
  selectedAnalysisType: string;
  setSelectedAnalysisType: (v: string) => void;
  selectedFocusAreas: string[];
  onFocusAreaChange: (area: string, checked: boolean) => void;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onStart: () => void;
  disabledStart: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="w-5 h-5" />
          Video Upload & Analysis
        </CardTitle>
        <CardDescription>Upload match videos for AI-powered analysis</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
          <input type="file" accept="video/*" onChange={onFileSelect} className="hidden" id="video-upload-dashboard" />
          <label htmlFor="video-upload-dashboard" className="cursor-pointer">
            <Video className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <div className="text-lg font-medium text-gray-700">
              {selectedVideoFile ? selectedVideoFile.name : "Drop video files here"}
            </div>
            <div className="text-sm text-gray-500">or click to browse</div>
            <div className="text-xs text-gray-400 mt-2">Supports MP4, MOV, AVI • Max 500MB</div>
          </label>
        </div>

        {selectedVideoFile && (
          <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center gap-2">
              <Video className="w-4 h-4 text-purple-600" />
              <span className="font-medium">{selectedVideoFile.name}</span>
            </div>
            <div className="text-sm text-gray-600 mt-1">Size: {(selectedVideoFile.size / 1024 / 1024).toFixed(1)} MB</div>
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

        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium">Analysis Type</label>
            <Select value={selectedAnalysisType} onValueChange={setSelectedAnalysisType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="highlights">Match Highlights</SelectItem>
                <SelectItem value="player">Player Tracking</SelectItem>
                <SelectItem value="tactics">Tactical Analysis</SelectItem>
                <SelectItem value="performance">Performance Metrics</SelectItem>
                <SelectItem value="crowd">Crowd Reactions</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium">Focus Areas</label>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {["Goals & Scoring", "Defensive Actions", "Player Movement", "Ball Possession", "Set Pieces", "Injuries"].map(
                (area) => (
                  <label key={area} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      className="rounded"
                      checked={selectedFocusAreas.includes(area)}
                      onChange={(e) => onFocusAreaChange(area, e.target.checked)}
                    />
                    <span className="text-sm">{area}</span>
                  </label>
                ),
              )}
            </div>
          </div>
        </div>

        <Button className="w-full bg-gradient-to-r from-purple-600 to-orange-600" onClick={onStart} disabled={disabledStart}>
          <Zap className="w-4 h-4 mr-2" />
          {isVideoUploading ? "Uploading..." : isVideoAnalyzing ? "Analyzing..." : "Start Analysis"}
        </Button>
      </CardContent>
    </Card>
  );
}
