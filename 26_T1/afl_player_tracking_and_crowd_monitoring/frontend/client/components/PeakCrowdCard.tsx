import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Clock } from "lucide-react";
import { BACKEND_URL } from "@/lib/config";
import { getAccessToken, isDemoToken } from "@/lib/auth";

interface PeakCrowdData {
  peakCount: number | null;
  timestamp: number | null;
  frameId: number | null;
  crowdState: string | null;
  riskZone: string | null;
  jobId: string | null;
}

interface PastJob {
  job_id: string;
  status: string;
  created_at: string;
}

type Status =
  | "loading"
  | "ready"
  | "empty"
  | "error"
  | "signed-out"
  | "demo";

const formatTimestamp = (seconds: number | null) => {
  if (seconds === null || Number.isNaN(seconds)) return "N/A";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
};

const formatLabel = (value: string | null) =>
  value ? value.replace(/_/g, " ") : null;

const formatJobDate = (value: string) =>
  new Date(value).toLocaleString("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });

/**
 * Stat card showing the busiest moment (peak crowd) from a crowd-monitoring
 * analysis. Shows the latest analysis by default, or the one chosen with the
 * picker / the ?jobId= URL parameter.
 */
export default function PeakCrowdCard() {
  const [searchParams, setSearchParams] = useSearchParams();
  const jobId = searchParams.get("jobId");

  const [status, setStatus] = useState<Status>("loading");
  const [data, setData] = useState<PeakCrowdData | null>(null);
  const [pastJobs, setPastJobs] = useState<PastJob[]>([]);

  // Past completed analyses for the picker
  useEffect(() => {
    const token = getAccessToken();
    if (!token || isDemoToken(token)) return;

    const controller = new AbortController();

    fetch(`${BACKEND_URL}/jobs?limit=20`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: controller.signal,
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((json) => {
        const jobs: PastJob[] = (json?.jobs ?? []).filter(
          (job: PastJob) => job.status === "done" || job.status === "partial",
        );
        setPastJobs(jobs);
      })
      .catch(() => {
        // The picker is optional - the card still works without it
      });

    return () => controller.abort();
  }, []);

  // Peak crowd for the chosen (or latest) analysis
  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setStatus("signed-out");
      return;
    }
    // The built-in demo login uses a placeholder token the backend rejects.
    if (isDemoToken(token)) {
      setStatus("demo");
      return;
    }

    setStatus("loading");

    const controller = new AbortController();
    const url = jobId
      ? `${BACKEND_URL}/jobs/${encodeURIComponent(jobId)}`
      : `${BACKEND_URL}/api/crowd/latest`;

    fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
      signal: controller.signal,
    })
      .then((res) => {
        if (res.status === 404) {
          setStatus("empty");
          return null;
        }
        if (res.status === 401 || res.status === 403) {
          setStatus("signed-out");
          return null;
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json) => {
        if (!json) return;

        // /jobs/{id} nests the crowd result under results; /api/crowd/latest
        // returns it under crowd.
        const crowd = jobId ? json.results?.crowd : json.crowd;
        const summary = crowd?.summary ?? {};
        const peak = crowd?.peak_crowd_frame ?? {};
        const count = peak.person_count ?? summary.peak_person_count ?? null;

        if (count === null || count === undefined) {
          setStatus("empty");
          return;
        }

        setData({
          peakCount: count,
          timestamp: peak.timestamp ?? null,
          frameId: peak.frame_id ?? null,
          crowdState: summary.crowd_state ?? null,
          riskZone: summary.highest_risk_zone ?? null,
          jobId: json.job_id ?? null,
        });
        setStatus("ready");
      })
      .catch((err) => {
        if (err?.name !== "AbortError") setStatus("error");
      });

    return () => controller.abort();
  }, [jobId]);

  const handlePick = (value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set("jobId", value);
    else next.delete("jobId");
    setSearchParams(next, { replace: true });
  };

  return (
    <Card data-testid="peak-crowd-card">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm text-gray-600">Peak Crowd</p>
              {pastJobs.length > 0 && (
                <select
                  aria-label="Choose a video analysis"
                  className="max-w-full rounded-md border border-gray-200 bg-white px-2 py-1 text-xs text-gray-700"
                  value={jobId ?? ""}
                  onChange={(e) => handlePick(e.target.value)}
                >
                  <option value="">Latest analysis</option>
                  {pastJobs.map((job) => (
                    <option key={job.job_id} value={job.job_id}>
                      {formatJobDate(job.created_at)}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {status === "loading" && (
              <p className="text-2xl font-bold text-gray-400">Loading...</p>
            )}

            {status === "ready" && data && (
              <>
                <p className="text-3xl font-bold text-gray-900">
                  {data.peakCount!.toLocaleString()}
                  <span className="ml-1 text-base font-medium text-gray-500">
                    people
                  </span>
                </p>
                <div className="mt-1 flex items-center gap-1 text-xs text-gray-500">
                  <Clock className="h-3 w-3" />
                  <span>
                    at {formatTimestamp(data.timestamp)}
                    {data.frameId !== null && ` (frame ${data.frameId})`}
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {data.crowdState && (
                    <Badge variant="secondary" className="capitalize">
                      {formatLabel(data.crowdState)}
                    </Badge>
                  )}
                  {data.riskZone && (
                    <Badge variant="outline">Risk zone {data.riskZone}</Badge>
                  )}
                </div>
              </>
            )}

            {status === "empty" && (
              <>
                <p className="text-2xl font-bold text-gray-400">--</p>
                <p className="text-xs text-gray-500">
                  {jobId
                    ? "No crowd results found for this video."
                    : "No crowd analysis yet. Upload a video to see the peak."}
                </p>
              </>
            )}

            {status === "signed-out" && (
              <>
                <p className="text-2xl font-bold text-gray-400">--</p>
                <p className="text-xs text-gray-500">
                  Session expired or signed out. Sign in again to see peak crowd
                  data.
                </p>
              </>
            )}

            {status === "demo" && (
              <>
                <p className="text-2xl font-bold text-gray-400">--</p>
                <p className="text-xs text-gray-500">
                  Demo account has no live data. Sign in with a registered
                  account to see peak crowd.
                </p>
              </>
            )}

            {status === "error" && (
              <>
                <p className="text-2xl font-bold text-gray-400">--</p>
                <p className="text-xs text-red-600">
                  Could not load peak crowd data. Check that the server is
                  running and try again.
                </p>
              </>
            )}
          </div>

          <Users className="h-8 w-8 text-blue-500" />
        </div>
      </CardContent>
    </Card>
  );
}
