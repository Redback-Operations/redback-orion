import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Eye, Download, FileText, Video } from "lucide-react";

export default function AnalysisResultsPanel({
  videoAnalysisComplete,
  selectedAnalysisType,
  selectedVideoFileName,
  selectedFocusAreas,
  onDownloadVideoClips,
  onDownloadReport,
}: {
  videoAnalysisComplete: boolean;
  selectedAnalysisType: string;
  selectedVideoFileName?: string;
  selectedFocusAreas: string[];
  onDownloadVideoClips: () => void;
  onDownloadReport: (format: "pdf" | "json" | "txt") => void;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Eye className="w-5 h-5" />
          Analysis Results
        </CardTitle>
        <CardDescription>AI-generated insights from uploaded videos</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!videoAnalysisComplete ? (
          <div className="text-center py-8">
            <Video className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Results Yet</h3>
            <p className="text-gray-600">Upload and analyze a video to see detailed insights here</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-purple-50 rounded-lg">
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
              <div className="text-sm text-gray-600">Video: {selectedVideoFileName}</div>
            </div>

            {selectedFocusAreas.length > 0 && (
              <div className="p-4 bg-orange-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Focus Areas Analyzed</span>
                  <Badge variant="secondary">{selectedFocusAreas.length} areas</Badge>
                </div>
                <div className="text-sm text-gray-600">{selectedFocusAreas.join(", ")}</div>
              </div>
            )}

            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">AI Insights Generated</span>
                <Badge variant="secondary">Ready</Badge>
              </div>
              <div className="text-sm text-gray-600">
                {selectedAnalysisType === "highlights" && "Key moments and highlights identified"}
                {selectedAnalysisType === "player" && "Player movements and performance tracked"}
                {selectedAnalysisType === "tactics" && "Tactical patterns and strategies analyzed"}
                {selectedAnalysisType === "performance" && "Performance metrics calculated"}
                {selectedAnalysisType === "crowd" && "Crowd reactions and engagement measured"}
              </div>
            </div>
          </div>
        )}

        <Separator />

        <div className="space-y-3">
          <h4 className="font-medium">Export Analysis</h4>
          <p className="text-sm text-gray-600">Download analysis data from backend in different formats</p>
          <div className="space-y-2">
            <Button variant="outline" size="sm" onClick={onDownloadVideoClips} disabled={!videoAnalysisComplete} className="w-full">
              <Download className="w-4 h-4 mr-2" /> Video Clips
            </Button>
            <div className="grid grid-cols-3 gap-1">
              <Button variant="outline" size="sm" onClick={() => onDownloadReport("pdf")} disabled={!videoAnalysisComplete}>
                <FileText className="w-4 h-4 mr-1" /> PDF
              </Button>
              <Button variant="outline" size="sm" onClick={() => onDownloadReport("json")} disabled={!videoAnalysisComplete}>
                <Download className="w-4 h-4 mr-1" /> JSON
              </Button>
              <Button variant="outline" size="sm" onClick={() => onDownloadReport("txt")} disabled={!videoAnalysisComplete}>
                <FileText className="w-4 h-4 mr-1" /> TXT
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
  );
}
