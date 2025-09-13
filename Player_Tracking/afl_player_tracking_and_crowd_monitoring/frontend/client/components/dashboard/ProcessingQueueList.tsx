import React from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Clock, Download, Eye, ChevronDown, FileText, Zap } from "lucide-react";
import QueueStatusIcon from "@/components/dashboard/QueueStatusIcon";
import type { QueueItem } from "@/types/dashboard";

export function ProcessingQueueList({
  items,
  onRetry,
  onRemove,
  onView,
  onDownload,
  formatTimeAgo,
  formatETA,
}: {
  items: QueueItem[];
  onRetry: (id: string) => void;
  onRemove: (id: string) => void;
  onView: (item: QueueItem) => void;
  onDownload: (item: QueueItem, format: "pdf" | "json" | "txt") => void;
  formatTimeAgo: (ts: string) => string;
  formatETA: (ts: string | null) => string;
}) {
  return (
    <div className="space-y-4">
      {items.map((item) => (
        <div key={item.id} className="p-4 border rounded-lg bg-gradient-to-r from-white via-gray-50 to-white">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <QueueStatusIcon status={item.status} />
              <div className="flex-1">
                <div className="font-medium text-gray-900">{item.name}</div>
                <div className="text-sm text-gray-600 flex items-center gap-2">
                  <span>{item.analysisType}</span>
                  <span>•</span>
                  <span>{item.duration}</span>
                  <span>•</span>
                  <span>{item.size}</span>
                  {item.priority === "high" && (
                    <>
                      <span>•</span>
                      <Badge variant="destructive" className="text-xs py-0 px-1">HIGH PRIORITY</Badge>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge
                variant={
                  item.status === "completed"
                    ? "default"
                    : item.status === "analyzing" || item.status === "processing"
                    ? "secondary"
                    : item.status === "uploading"
                    ? "outline"
                    : item.status === "failed"
                    ? "destructive"
                    : "outline"
                }
                className="capitalize"
              >
                {item.status}
              </Badge>
              {item.retryCount > 0 && (
                <Badge variant="outline" className="text-xs">Retry #{item.retryCount}</Badge>
              )}
            </div>
          </div>

          {item.progress > 0 && item.progress < 100 && (
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">
                  {item.status === "uploading"
                    ? "Uploading file..."
                    : item.status === "processing"
                    ? "Pre-processing video..."
                    : item.status === "analyzing"
                    ? "Analyzing video content..."
                    : "Processing..."}
                </span>
                <span className="font-medium">{Math.round(item.progress)}%</span>
              </div>
              <Progress value={item.progress} className="h-2" />
              <div className="text-xs text-gray-500">
                Stage: {item.processingStage.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
              </div>
            </div>
          )}

          {item.status === "failed" && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 text-red-800 text-sm">
                <div className="w-4 h-4 rounded-full bg-red-500 flex-shrink-0" />
                <span>
                  Processing failed after {item.errorCount} attempt{item.errorCount > 1 ? "s" : ""}
                </span>
              </div>
              <div className="text-xs text-red-600 mt-1">
                Common causes: Unsupported format, corrupted file, or insufficient server resources
              </div>
            </div>
          )}

          <div className="flex justify-between items-center mt-3">
            <div className="flex flex-col text-sm text-gray-500">
              <span>Uploaded: {formatTimeAgo(item.uploadTime)}</span>
              {item.status === "completed" && item.completedTime && (
                <span>Completed: {formatTimeAgo(item.completedTime)}</span>
              )}
              {item.estimatedCompletion && item.status !== "completed" && (
                <span>ETA: {formatETA(item.estimatedCompletion)}</span>
              )}
            </div>
            <div className="flex gap-2">
              {item.status === "completed" && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onView(item)}
                    className="text-purple-600 border-blue-600 hover:bg-purple-50"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    View
                  </Button>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" size="sm" className="text-orange-600 border-orange-600 hover:bg-orange-50">
                        <Download className="w-4 h-4 mr-1" />
                        Download
                        <ChevronDown className="w-3 h-3 ml-1" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => onDownload(item, "pdf")}>
                        <FileText className="w-4 h-4 mr-2" /> PDF Report
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => onDownload(item, "json")}>
                        <Download className="w-4 h-4 mr-2" /> JSON Data
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => onDownload(item, "txt")}>
                        <FileText className="w-4 h-4 mr-2" /> Text Summary
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </>
              )}

              {item.status === "failed" && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onRetry(item.id)}
                    className="text-purple-600 border-blue-600 hover:bg-purple-50"
                  >
                    <Zap className="w-4 h-4 mr-1" />
                    Retry
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onRemove(item.id)}
                    className="text-red-600 border-red-600 hover:bg-red-50"
                  >
                    Remove
                  </Button>
                </>
              )}

              {(item.status === "queued" || item.status === "uploading") && (
                <Button variant="outline" size="sm" onClick={() => onRemove(item.id)} className="text-gray-600">
                  Cancel
                </Button>
              )}
            </div>
          </div>
        </div>
      ))}

      {items.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No items in processing queue</p>
          <p className="text-sm">Upload a video to start analysis</p>
        </div>
      )}
    </div>
  );
}

export default ProcessingQueueList;
