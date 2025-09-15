import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Video, Upload, Zap, FileText, Download } from "lucide-react";
import VideoUploadPanel from "../VideoUploadPanel";
import AnalysisResultsPanel from "../AnalysisResultsPanel";
import ProcessingQueueList from "../ProcessingQueueList";
import QueueStatusIcon from "../QueueStatusIcon";

interface VideoAnalysisTabProps {
  selectedVideoFile: File | null;
  videoAnalysisError: string | null;
  isVideoUploading: boolean;
  videoUploadProgress: number;
  isVideoAnalyzing: boolean;
  videoAnalysisProgress: number;
  selectedAnalysisType: string;
  setSelectedAnalysisType: (type: string) => void;
  selectedFocusAreas: string[];
  onFocusAreaChange: (area: string, checked: boolean) => void;
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onStart: () => void;
  disabledStart: boolean;
  videoAnalysisComplete: boolean;
  selectedVideoFileName: string;
  onDownloadVideoClips: () => void;
  onDownloadReport: () => void;
  processingQueue: any[];
  onRetryProcessing: (id: string) => void;
  onCancelProcessing: (id: string) => void;
}

export default function VideoAnalysisTab({
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
  videoAnalysisComplete,
  selectedVideoFileName,
  onDownloadVideoClips,
  onDownloadReport,
  processingQueue,
  onRetryProcessing,
  onCancelProcessing,
}: VideoAnalysisTabProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Video className="w-6 h-6" />
            Video Analysis
          </h2>
          <p className="text-gray-600">AI-powered video analysis and insights generation</p>
        </div>
        <div className="flex items-center gap-2">
          <QueueStatusIcon queue={processingQueue} />
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
            <Zap className="w-3 h-3 mr-1" />
            AI Powered
          </Badge>
        </div>
      </div>

      {/* Processing Queue */}
      {processingQueue.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Processing Queue
            </CardTitle>
            <CardDescription>
              Current video analysis tasks
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ProcessingQueueList
              queue={processingQueue}
              onRetry={onRetryProcessing}
              onCancel={onCancelProcessing}
            />
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Video Upload Panel */}
        <div className="space-y-6">
          <VideoUploadPanel
            selectedVideoFile={selectedVideoFile}
            videoAnalysisError={videoAnalysisError}
            isVideoUploading={isVideoUploading}
            videoUploadProgress={videoUploadProgress}
            isVideoAnalyzing={isVideoAnalyzing}
            videoAnalysisProgress={videoAnalysisProgress}
            selectedAnalysisType={selectedAnalysisType}
            setSelectedAnalysisType={setSelectedAnalysisType}
            selectedFocusAreas={selectedFocusAreas}
            onFocusAreaChange={onFocusAreaChange}
            onFileSelect={onFileSelect}
            onStart={onStart}
            disabledStart={disabledStart}
          />

          {/* Analysis Types Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Analysis Types</CardTitle>
              <CardDescription>
                Choose the type of analysis you want to perform
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2" />
                  <div>
                    <h4 className="font-medium text-blue-900">Highlights</h4>
                    <p className="text-sm text-blue-700">Extract key moments and highlights from the video</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2" />
                  <div>
                    <h4 className="font-medium text-green-900">Player Tracking</h4>
                    <p className="text-sm text-green-700">Track individual player movements and statistics</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                  <div className="w-2 h-2 bg-purple-500 rounded-full mt-2" />
                  <div>
                    <h4 className="font-medium text-purple-900">Crowd Analysis</h4>
                    <p className="text-sm text-purple-700">Analyze crowd behavior and density patterns</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg">
                  <div className="w-2 h-2 bg-orange-500 rounded-full mt-2" />
                  <div>
                    <h4 className="font-medium text-orange-900">Tactical Analysis</h4>
                    <p className="text-sm text-orange-700">Analyze team formations and tactical patterns</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Analysis Results */}
        <div className="space-y-6">
          <AnalysisResultsPanel
            videoAnalysisComplete={videoAnalysisComplete}
            selectedAnalysisType={selectedAnalysisType}
            selectedVideoFileName={selectedVideoFileName}
            selectedFocusAreas={selectedFocusAreas}
            onDownloadVideoClips={onDownloadVideoClips}
            onDownloadReport={onDownloadReport}
          />

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
              <CardDescription>
                Common video analysis tasks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <button className="p-3 text-left border rounded-lg hover:bg-gray-50 transition-colors">
                  <Upload className="w-5 h-5 text-blue-600 mb-2" />
                  <h4 className="font-medium text-sm">Upload New Video</h4>
                  <p className="text-xs text-gray-500">Start a new analysis</p>
                </button>
                <button className="p-3 text-left border rounded-lg hover:bg-gray-50 transition-colors">
                  <Download className="w-5 h-5 text-green-600 mb-2" />
                  <h4 className="font-medium text-sm">Download Results</h4>
                  <p className="text-xs text-gray-500">Get analysis reports</p>
                </button>
                <button className="p-3 text-left border rounded-lg hover:bg-gray-50 transition-colors">
                  <FileText className="w-5 h-5 text-purple-600 mb-2" />
                  <h4 className="font-medium text-sm">View History</h4>
                  <p className="text-xs text-gray-500">Previous analyses</p>
                </button>
                <button className="p-3 text-left border rounded-lg hover:bg-gray-50 transition-colors">
                  <Zap className="w-5 h-5 text-orange-600 mb-2" />
                  <h4 className="font-medium text-sm">Batch Process</h4>
                  <p className="text-xs text-gray-500">Multiple videos</p>
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
