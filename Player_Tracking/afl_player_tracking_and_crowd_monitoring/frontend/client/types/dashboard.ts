export type QueueItem = {
  id: string;
  name: string;
  analysisType: string;
  status:
    | "uploading"
    | "queued"
    | "processing"
    | "analyzing"
    | "completed"
    | "failed";
  progress: number;
  duration: string;
  size: string;
  uploadTime: string;
  completedTime: string | null;
  estimatedCompletion: string | null;
  priority: "low" | "medium" | "high";
  userId: string;
  processingStage: string;
  errorCount: number;
  retryCount: number;
  isUIControlled?: boolean;
};
