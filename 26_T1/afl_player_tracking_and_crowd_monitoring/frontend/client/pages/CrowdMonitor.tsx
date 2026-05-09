import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import MobileNavigation from "@/components/MobileNavigation";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle,
  Eye,
  Image as ImageIcon,
  MapPin,
  Shield,
  Users,
} from "lucide-react";

const BACKEND_URL = "http://localhost:8000";

const getAccessToken = () =>
  localStorage.getItem("accessToken") || localStorage.getItem("authToken");

type DensityZone = {
  zone_id?: string;
  person_count?: number;
  density?: number;
  risk_level?: string;
  flagged?: boolean;
};

type CrowdResult = {
  video_id?: string;
  summary?: {
    total_frames_processed?: number;
    peak_person_count?: number;
    crowd_state?: string;
    highest_density_zone?: string | null;
    highest_risk_zone?: string | null;
  };
  peak_crowd_frame?: {
    frame_id?: number;
    timestamp?: number;
    person_count?: number;
    annotated_frame_path?: string | null;
  };
  anomaly_visual?: {
    event_type?: string;
    image_path?: string | null;
  };
  heatmap?: {
    image_path?: string | null;
  };
  time_series_chart?: {
    image_path?: string | null;
  };
  density_extremes?: {
    highest_density_zone?: DensityZone;
    lowest_density_zone?: DensityZone;
  };
};

type JobListResponse = {
  total: number;
  page: number;
  limit: number;
  jobs: Array<{
    job_id: string;
    status: string;
    created_at: string;
    updated_at: string;
  }>;
};

type JobDetailResponse = {
  job_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  results?: {
    crowd?: CrowdResult | null;
    player?: unknown;
  } | null;
  errors?: {
    crowd?: string | null;
    player?: string | null;
  } | null;
};

type ZoneCard = {
  id: string;
  name: string;
  density: number;
  count: number;
  risk: string;
  flagged: boolean;
  trend: "up" | "down" | "stable";
  waitTime: number;
  flow: number;
};

function formatCrowdState(value?: string | null) {
  if (!value) return "Unknown";
  return value.replaceAll("_", " ");
}

function formatRisk(value?: string | null) {
  if (!value) return "unknown";
  return value.replaceAll("_", " ");
}

function toPercent(value?: number) {
  return typeof value === "number" ? Math.round(value * 100) : 0;
}

function getDensityLabel(density: number) {
  if (density >= 95) return "Critical";
  if (density >= 85) return "High";
  if (density >= 70) return "Medium";
  if (density >= 50) return "Low-Medium";
  return "Low";
}

function buildZoneCards(result: CrowdResult | null): ZoneCard[] {
  const highest = result?.density_extremes?.highest_density_zone;
  const lowest = result?.density_extremes?.lowest_density_zone;

  const zones: ZoneCard[] = [];

  if (highest) {
    zones.push({
      id: "highest",
      name: highest.zone_id || "Highest Density Zone",
      density: toPercent(highest.density),
      count: highest.person_count || 0,
      risk: formatRisk(highest.risk_level),
      flagged: Boolean(highest.flagged),
      trend: "up",
      waitTime: 8,
      flow: Math.max(10, (highest.person_count || 0) * 2),
    });
  }

  if (lowest) {
    zones.push({
      id: "lowest",
      name: lowest.zone_id || "Lowest Density Zone",
      density: toPercent(lowest.density),
      count: lowest.person_count || 0,
      risk: formatRisk(lowest.risk_level),
      flagged: Boolean(lowest.flagged),
      trend: "down",
      waitTime: 2,
      flow: Math.max(5, lowest.person_count || 0),
    });
  }

  if (zones.length === 0) {
    zones.push({
      id: "default",
      name: result?.summary?.highest_density_zone || "Crowd Zone",
      density: 0,
      count: result?.summary?.peak_person_count || 0,
      risk: "unknown",
      flagged: false,
      trend: "stable",
      waitTime: 0,
      flow: 0,
    });
  }

  return zones;
}

function ArtifactPanel({
  title,
  subtitle,
  imageUrl,
  fallback,
}: {
  title: string;
  subtitle: string;
  imageUrl: string | null;
  fallback: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        <CardDescription>{subtitle}</CardDescription>
      </CardHeader>
      <CardContent>
        {imageUrl ? (
          <div className="overflow-hidden rounded-xl border border-gray-200 bg-gray-50">
            <img
              src={imageUrl}
              alt={title}
              className="h-72 w-full object-contain bg-white"
            />
          </div>
        ) : (
          <div className="flex h-72 flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 bg-gray-50 px-6 text-center text-sm text-gray-500">
            <ImageIcon className="mb-3 h-8 w-8" />
            <p>{fallback}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function CrowdMonitor() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [viewMode, setViewMode] = useState("peak");
  const [timeRange, setTimeRange] = useState("latest");
  const [crowdResult, setCrowdResult] = useState<CrowdResult | null>(null);
  const [jobId, setJobId] = useState("");
  const [peakFrameUrl, setPeakFrameUrl] = useState<string | null>(null);
  const [anomalyVisualUrl, setAnomalyVisualUrl] = useState<string | null>(null);
  const [personCountChartUrl, setPersonCountChartUrl] = useState<string | null>(null);
  const [heatmapUrl, setHeatmapUrl] = useState<string | null>(null);
  const [pageError, setPageError] = useState<string | null>(null);

  useEffect(() => {
    const isAuthenticated = localStorage.getItem("isAuthenticated");
    if (isAuthenticated !== "true") {
      navigate("/login");
      return;
    }
  }, [navigate]);

  useEffect(() => {
    void loadCrowdResult(searchParams.get("jobId") || undefined);
  }, [searchParams]);

  useEffect(() => {
    const objectUrls: string[] = [];

    async function fetchArtifact(
      endpoint: string,
      setter: (value: string | null) => void,
    ) {
      if (!jobId) {
        setter(null);
        return;
      }

      const token = getAccessToken();
      if (!token) {
        setter(null);
        return;
      }

      try {
        const response = await fetch(`${BACKEND_URL}/jobs/${jobId}/${endpoint}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          setter(null);
          return;
        }

        const blob = await response.blob();
        const objectUrl = URL.createObjectURL(blob);
        objectUrls.push(objectUrl);
        setter(objectUrl);
      } catch {
        setter(null);
      }
    }

    void fetchArtifact("peak-crowd-frame", setPeakFrameUrl);
    void fetchArtifact("anomaly-visual", setAnomalyVisualUrl);
    void fetchArtifact("person-count-chart", setPersonCountChartUrl);
    void fetchArtifact("heatmap", setHeatmapUrl);

    return () => {
      objectUrls.forEach((url) => URL.revokeObjectURL(url));
    };
  }, [jobId]);

  async function getLatestJobId(token: string) {
    const response = await fetch(`${BACKEND_URL}/jobs?page=1&limit=10`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Could not fetch jobs from backend");
    }

    const payload = (await response.json()) as JobListResponse;
    if (!payload.jobs.length) {
      throw new Error("No jobs found in the backend");
    }

    return payload.jobs[0].job_id;
  }

  async function loadCrowdResult(explicitJobId?: string) {
    const token = getAccessToken();
    if (!token) {
      navigate("/login");
      return;
    }

    try {
      setPageError(null);
      const nextJobId = explicitJobId || (await getLatestJobId(token));
      const response = await fetch(`${BACKEND_URL}/jobs/${nextJobId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          setCrowdResult(null);
          setJobId("");
          setPageError("The requested job was not found.");
          return;
        }
        throw new Error("Could not fetch crowd-monitoring result");
      }

      const payload = (await response.json()) as JobDetailResponse;
      setJobId(payload.job_id);
      if (searchParams.get("jobId") !== payload.job_id) {
        setSearchParams({ jobId: payload.job_id }, { replace: true });
      }

      if (payload.results?.crowd) {
        setCrowdResult(payload.results.crowd);
      } else {
        setCrowdResult(null);
        setPageError(
          payload.errors?.crowd || "Crowd result is not available for the latest job yet.",
        );
      }
    } catch (error) {
      setPageError(
        error instanceof Error ? error.message : "Could not load crowd-monitoring result",
      );
    }
  }

  const zoneCards = useMemo(() => buildZoneCards(crowdResult), [crowdResult]);
  const selectedZone = zoneCards[0];
  const averageDensity =
    zoneCards.length > 0
      ? Math.round(
          zoneCards.reduce((sum, zone) => sum + zone.density, 0) / zoneCards.length,
        )
      : 0;
  const criticalZones = zoneCards.filter((zone) => zone.density >= 95);
  const highDensityZones = zoneCards.filter(
    (zone) => zone.density >= 85 && zone.density < 95,
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <MobileNavigation />

      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-4">
          <Card>
            <CardContent className="p-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-600">Current Job ID</p>
                <p className="text-sm font-mono break-all text-gray-900">
                  {jobId || "No completed crowd-monitoring job yet"}
                </p>
              </div>
            </CardContent>
          </Card>

          {pageError ? (
            <Card>
              <CardContent className="p-4 text-sm text-red-600">{pageError}</CardContent>
            </Card>
          ) : null}

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Peak Crowd</p>
                    <p className="text-2xl font-bold">
                      {crowdResult?.summary?.peak_person_count ?? 0}
                    </p>
                    <p className="text-xs text-gray-500">
                      {crowdResult?.peak_crowd_frame?.frame_id != null
                        ? `Frame ${crowdResult.peak_crowd_frame.frame_id}`
                        : "No frame data"}
                    </p>
                  </div>
                  <Users className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Crowd State</p>
                    <p className="text-2xl font-bold capitalize">
                      {formatCrowdState(crowdResult?.summary?.crowd_state)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {crowdResult?.summary?.total_frames_processed ?? 0} frames processed
                    </p>
                  </div>
                  <Activity className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Critical Zones</p>
                    <p className="text-2xl font-bold text-red-600">
                      {criticalZones.length}
                    </p>
                    <p className="text-xs text-gray-500">
                      Highest risk: {crowdResult?.summary?.highest_risk_zone || "None"}
                    </p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-red-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Average Density</p>
                    <p className="text-2xl font-bold">{averageDensity}%</p>
                    <p className="text-xs text-gray-500">
                      {getDensityLabel(averageDensity)}
                    </p>
                  </div>
                  <BarChart3 className="w-8 h-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <Select value={viewMode} onValueChange={setViewMode}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="peak">Peak Crowd Frame</SelectItem>
                <SelectItem value="anomaly">Anomaly Visual</SelectItem>
                <SelectItem value="heatmap">Heatmap</SelectItem>
                <SelectItem value="chart">Person Count Chart</SelectItem>
                <SelectItem value="analytics">Analytics View</SelectItem>
              </SelectContent>
            </Select>

            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="latest">Latest Result</SelectItem>
                <SelectItem value="job">Current Job</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Tabs value={viewMode} onValueChange={setViewMode} className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="peak">Peak Crowd</TabsTrigger>
              <TabsTrigger value="anomaly">Anomaly</TabsTrigger>
              <TabsTrigger value="heatmap">Heatmap</TabsTrigger>
              <TabsTrigger value="chart">Person Count</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
            </TabsList>

            <TabsContent value="peak" className="space-y-4">
              <ArtifactPanel
                title="Peak Crowd Frame"
                subtitle={
                  crowdResult?.peak_crowd_frame
                    ? `Frame ${crowdResult.peak_crowd_frame.frame_id ?? "N/A"} at ${crowdResult.peak_crowd_frame.timestamp ?? "N/A"}s`
                    : "No frame metadata available"
                }
                imageUrl={peakFrameUrl}
                fallback="Peak crowd frame is not available for this job."
              />
              <Card>
                <CardHeader>
                  <CardTitle>{selectedZone.name}</CardTitle>
                  <CardDescription className="flex items-center gap-4">
                    <Badge
                      variant={
                        selectedZone.density >= 95
                          ? "destructive"
                          : selectedZone.density >= 85
                            ? "secondary"
                            : "default"
                      }
                    >
                      {getDensityLabel(selectedZone.density)}
                    </Badge>
                    <span>{selectedZone.count} people detected</span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Density</span>
                          <span>{selectedZone.density}%</span>
                        </div>
                        <Progress value={selectedZone.density} className="h-3" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <h5 className="font-medium text-sm">Risk Level</h5>
                      <div className="text-sm text-gray-600 capitalize">
                        {selectedZone.risk}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <h5 className="font-medium text-sm">Safety State</h5>
                      <div className="text-sm text-gray-600">
                        {selectedZone.flagged ? "Flagged for attention" : "Normal"}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="anomaly" className="space-y-4">
              <ArtifactPanel
                title="Anomaly / Movement Visual"
                subtitle={
                  crowdResult?.anomaly_visual?.event_type
                    ? formatCrowdState(crowdResult.anomaly_visual.event_type)
                    : "No anomaly event available"
                }
                imageUrl={anomalyVisualUrl}
                fallback="Anomaly visual is not available for this job."
              />
            </TabsContent>

            <TabsContent value="heatmap" className="space-y-4">
              <ArtifactPanel
                title="Heatmap"
                subtitle={crowdResult?.heatmap?.image_path || "Heatmap preview"}
                imageUrl={heatmapUrl}
                fallback="Heatmap image is not available for this job."
              />
            </TabsContent>

            <TabsContent value="chart" className="space-y-4">
              <ArtifactPanel
                title="Person Count Over Time"
                subtitle={crowdResult?.time_series_chart?.image_path || "Chart artifact"}
                imageUrl={personCountChartUrl}
                fallback="Person count chart is not available for this job."
              />
            </TabsContent>

            <TabsContent value="analytics" className="space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="w-5 h-5" />
                      Density Distribution
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {zoneCards.map((zone) => (
                      <div key={zone.id} className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span>{zone.name}</span>
                          <span>{zone.density}%</span>
                        </div>
                        <Progress value={zone.density} className="h-2" />
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="w-5 h-5" />
                      Crowd Summary
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h5 className="text-sm font-medium mb-2">Video ID</h5>
                      <div className="text-lg font-semibold">
                        {crowdResult?.video_id || "N/A"}
                      </div>
                    </div>
                    <div>
                      <h5 className="text-sm font-medium mb-2">Highest Density Zone</h5>
                      <div className="text-lg font-semibold">
                        {crowdResult?.summary?.highest_density_zone || "N/A"}
                      </div>
                    </div>
                    <div>
                      <h5 className="text-sm font-medium mb-2">Highest Risk Zone</h5>
                      <div className="text-lg font-semibold">
                        {crowdResult?.summary?.highest_risk_zone || "None"}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5" />
                    Safety & Alerts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {criticalZones.length > 0 && (
                      <div className="p-3 bg-red-50 border border-red-200 rounded">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertTriangle className="w-5 h-5 text-red-500" />
                          <span className="font-medium text-red-700">
                            Critical Density Alert
                          </span>
                        </div>
                        <p className="text-sm text-red-600">
                          {criticalZones.map((zone) => zone.name).join(", ")}
                        </p>
                      </div>
                    )}

                    {highDensityZones.length > 0 && (
                      <div className="p-3 bg-orange-50 border border-orange-200 rounded">
                        <div className="flex items-center gap-2 mb-2">
                          <Eye className="w-5 h-5 text-orange-500" />
                          <span className="font-medium text-orange-700">
                            High Density Warning
                          </span>
                        </div>
                        <p className="text-sm text-orange-600">
                          {highDensityZones.map((zone) => zone.name).join(", ")}
                        </p>
                      </div>
                    )}

                    {criticalZones.length === 0 && highDensityZones.length === 0 && (
                      <div className="p-3 bg-green-50 border border-green-200 rounded">
                        <div className="flex items-center gap-2">
                          <CheckCircle className="w-5 h-5 text-green-500" />
                          <span className="font-medium text-green-700">
                            All zones operating normally
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
