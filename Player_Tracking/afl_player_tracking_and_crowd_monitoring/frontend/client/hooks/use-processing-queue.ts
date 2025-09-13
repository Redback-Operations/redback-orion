import { useEffect } from "react";
import type { QueueItem } from "@/types/dashboard";

export function useProcessingQueueSimulator(
  processingQueue: QueueItem[],
  setProcessingQueue: React.Dispatch<React.SetStateAction<QueueItem[]>>,
) {
  useEffect(() => {
    const interval = setInterval(() => {
      setProcessingQueue((prev) =>
        prev.map((item) => {
          if (
            (item.status === "analyzing" ||
              item.status === "processing" ||
              item.status === "uploading" ||
              item.status === "queued") &&
            !item.isUIControlled
          ) {
            const sizeMultiplier = parseFloat(item.size) > 1000 ? 0.5 : 1;
            const complexityMultiplier =
              item.analysisType === "Full Match Analysis"
                ? 0.3
                : item.analysisType === "Tactical Analysis"
                  ? 0.6
                  : 1;
            const progressIncrement =
              Math.random() * 3 * sizeMultiplier * complexityMultiplier + 0.5;
            const newProgress = Math.min(100, item.progress + progressIncrement);

            let newStage = item.processingStage;
            let newStatus: QueueItem["status"] = item.status;

            if (item.status === "uploading" && newProgress >= 100) {
              newStatus = "queued";
              newStage = "queue_waiting";
              return { ...item, status: newStatus, progress: 0, processingStage: newStage };
            }

            if (item.status === "queued" && Math.random() > 0.7) {
              newStatus = "processing";
              newStage = "preprocessing";
              return { ...item, status: newStatus, progress: 5, processingStage: newStage };
            }

            if (item.status === "processing" && item.progress > 30 && Math.random() > 0.8) {
              newStatus = "analyzing";
              newStage = "video_analysis";
            }

            if (newProgress >= 100) {
              newStatus = "completed";
              newStage = "analysis_complete";
              return {
                ...item,
                status: newStatus,
                progress: 100,
                processingStage: newStage,
                completedTime: new Date().toISOString(),
                estimatedCompletion: null,
              };
            }

            const failureChance =
              parseFloat(item.size) > 2000
                ? 0.005
                : item.analysisType === "Tactical Analysis"
                  ? 0.003
                  : item.retryCount > 0
                    ? 0.001
                    : 0.002;

            if (Math.random() < failureChance && item.errorCount < 2 && item.progress > 10) {
              const errorReasons = [
                "insufficient_memory",
                "corrupted_segment",
                "processing_timeout",
                "unsupported_codec",
                "server_overload",
              ];
              return {
                ...item,
                status: "failed",
                processingStage: errorReasons[Math.floor(Math.random() * errorReasons.length)],
                errorCount: item.errorCount + 1,
              };
            }

            return { ...item, progress: newProgress, status: newStatus, processingStage: newStage };
          }
          return item;
        }),
      );
    }, 2000);

    return () => clearInterval(interval);
  }, [setProcessingQueue, processingQueue]);
}
