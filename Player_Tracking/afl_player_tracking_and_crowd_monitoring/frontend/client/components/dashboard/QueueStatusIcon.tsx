import React from "react";

export type QueueStatus =
  | "uploading"
  | "queued"
  | "processing"
  | "analyzing"
  | "completed"
  | "failed";

export function QueueStatusIcon({ status }: { status: QueueStatus }) {
  switch (status) {
    case "completed":
      return <div className="w-3 h-3 rounded-full bg-orange-500" />;
    case "analyzing":
    case "processing":
      return <div className="w-3 h-3 rounded-full bg-purple-500 animate-pulse" />;
    case "uploading":
      return <div className="w-3 h-3 rounded-full bg-yellow-500 animate-pulse" />;
    case "queued":
      return <div className="w-3 h-3 rounded-full bg-gray-400" />;
    case "failed":
      return <div className="w-3 h-3 rounded-full bg-red-500" />;
    default:
      return <div className="w-3 h-3 rounded-full bg-gray-300" />;
  }
}

export default QueueStatusIcon;
