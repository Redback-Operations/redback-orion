export type BackendStatusResponse = {
  job_id: string;
  status: string;
  results?: {
    player?: any;
    crowd?: any;
  };
  error?: string;
  detail?: string;
};

export type DashboardPlayer = {
  id: number;
  name: string;
  team: string;
  position: string;
  number: number;
  fieldX: number;
  fieldY: number;
  kicks: number;
  handballs: number;
  marks: number;
  tackles: number;
  goals: number;
  efficiency: number;
};

export type QueueItemStatus =
  | "uploading"
  | "queued"
  | "processing"
  | "analyzing"
  | "completed"
  | "failed";

export type ProcessingQueueItem = {
  id: string;
  name: string;
  analysisType: string;
  status: QueueItemStatus;
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
