import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, TrendingUp, Image as ImageIcon } from "lucide-react";
import { getCrowdAnalysis } from "@/lib/video";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface UploadMeta {
  id: string;
  original_filename: string;
  created_at: string;
  status: string;
}

interface CrowdMonitorTabProps {
  upload: UploadMeta | null;
}

export default function CrowdMonitorTab({ upload }: CrowdMonitorTabProps) {
  const [crowdData, setCrowdData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!upload?.id) return;

    setLoading(true);
    setError(null);

    getCrowdAnalysis(upload.id)
      .then((res) => {
        if (res?.status === "not_available" || res?.status === "no-heatmaps") {
          setError("⚠ Crowd analysis was not run for this video.");
        } else {
          setCrowdData(res);
        }
      })
      .catch((err) => {
        console.error("❌ Failed to fetch crowd analysis:", err);
        setError("⚠ Crowd analysis was not run for this video.");
      })
      .finally(() => setLoading(false));
  }, [upload?.id]);

  if (!upload) {
    return (
      <p className="text-sm text-gray-500">
        ⚠️ No video selected for analysis.
      </p>
    );
  }

  if (loading) {
    return (
      <p className="text-sm text-gray-500">
        ⏳ Loading crowd analysis...
      </p>
    );
  }

  if (error) {
    return <p className="text-sm text-red-500">{error}</p>;
  }

  if (!crowdData) {
    return (
      <p className="text-sm text-gray-500">
        No crowd analysis results yet.
      </p>
    );
  }

  const {
    avg_count = 0,
    peak_count = 0,
    min_count = 0,
    time_series = [],
    results = [],
  } = crowdData;

  return (
    <div className="space-y-6 md:space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-purple-700 dark:text-purple-400">
          Crowd Monitor – {upload.original_filename}
        </h2>
        <p className="text-sm text-gray-500">
          Uploaded: {new Date(upload.created_at).toLocaleString()}
        </p>
      </div>

      {/* Title + Status */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-2xl font-bold flex items-center gap-2 bg-gradient-to-r from-purple-600 to-orange-600 bg-clip-text text-transparent">
            <Users className="w-6 h-6" />
            Crowd Analysis
          </h3>
          <p className="text-gray-600">
            Crowd analytics from analyzed video
          </p>
        </div>
        <Badge
          variant="outline"
          className="bg-gradient-to-r from-purple-600 to-orange-600 text-white border-0 shadow-sm rounded-full px-3 py-1 animate-pulse"
        >
          LIVE
        </Badge>
      </div>

      {/* ✅ Summary Stats */}
      <Card className="border border-gray-200 shadow-sm rounded-xl bg-white/90">
        <CardHeader className="pb-2">
          <CardTitle>Summary Statistics</CardTitle>
          <CardDescription>
            Aggregate metrics from video analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center [&>div]:bg-gradient-to-b [&>div]:from-purple-50 [&>div]:to-orange-50 [&>div]:rounded-lg [&>div]:p-3 [&>div]:ring-1 [&>div]:ring-purple-100 [&>div]:shadow-sm">
          <div>
            <div className="text-lg font-bold">{avg_count}</div>
            <div className="text-xs text-gray-500">Avg Count</div>
          </div>
          <div>
            <div className="text-lg font-bold">{peak_count}</div>
            <div className="text-xs text-gray-500">Peak Count</div>
          </div>
          <div>
            <div className="text-lg font-bold">{min_count}</div>
            <div className="text-xs text-gray-500">Min Count</div>
          </div>
        </CardContent>
      </Card>

      {/* ✅ Line Chart */}
      <Card className="border border-gray-200 shadow-sm rounded-xl bg-white/90">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Crowd Density Over Time
          </CardTitle>
          <CardDescription>People count per frame</CardDescription>
        </CardHeader>
        <CardContent className="p-6 bg-gradient-to-b from-white to-purple-50/40 rounded-lg">
          {time_series.length === 0 ? (
            <p className="text-sm text-gray-500">
              No time series data available.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={time_series}>
                <defs>
                  <linearGradient id="crowdLine" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#8b5cf6" />
                    <stop offset="100%" stopColor="#fb923c" />
                  </linearGradient>
                </defs>
                <XAxis dataKey="frame_number" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="people_count"
                  stroke="url(#crowdLine)"
                  strokeWidth={2.5}
                  dot={{ r: 1.5 }}
                  activeDot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* ✅ Frame-wise Heatmaps */}
      <Card className="border border-gray-200 shadow-sm rounded-xl bg-white/90">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2">
            <ImageIcon className="w-5 h-5" />
            Frame-wise Heatmaps
          </CardTitle>
          <CardDescription>
            Detected people count with heatmap per frame
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6 bg-gradient-to-b from-white to-purple-50/40 rounded-lg">
          {results.length === 0 ? (
            <p className="text-sm text-gray-500">
              No per-frame results available.
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[600px] overflow-y-auto pr-1">
              {results.map((row: any, idx: number) => (
                <div
                  key={idx}
                  className="group border border-gray-200 rounded-lg p-3 shadow-sm hover:shadow-md hover:border-purple-200 transition bg-white"
                >
                  {row.heatmap_url ? (
                    <img
                      src={row.heatmap_url}
                      alt={`Frame ${row.frame_number} heatmap`}
                      className="w-full h-40 object-contain rounded-lg mb-2 border border-gray-200 transition-transform duration-200 group-hover:scale-[1.02]"
                    />
                  ) : (
                    <p className="text-xs text-gray-400 italic">
                      No heatmap available
                    </p>
                  )}
                  <p className="text-xs text-gray-600">
                    <span className="font-semibold">Frame:</span>{" "}
                    {row.frame_number}
                  </p>
                  <p className="text-xs text-gray-600">
                    <span className="font-semibold">People Count:</span>{" "}
                    <span className="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium bg-gradient-to-r from-purple-600 to-orange-600 text-white">
                      {row.people_count}
                    </span>
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
