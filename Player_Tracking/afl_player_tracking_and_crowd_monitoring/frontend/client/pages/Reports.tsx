import React, { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, FileText } from "lucide-react";
import MobileNavigation from "@/components/MobileNavigation";
import LiveClock from "@/components/LiveClock";
import { getPlayerDashboard, getCrowdAnalysis, listUploads } from "@/lib/video";
import { buildAnalysisPdf } from "@/lib/pdf";
import { downloadFile } from "@/lib/download";

interface UploadMeta {
  id: string;
  original_filename: string;
  created_at: string;
}

function slugify(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}

async function generatePDFWithFetcher(title: string, upload: UploadMeta, section: string, fetcher: () => Promise<any>) {
  try {
    const data = await fetcher();
    const blob = await buildAnalysisPdf({ title, upload, section, data });
    const name = `${slugify(title)}_${slugify(upload.original_filename)}_${Date.now()}.pdf`;
    downloadFile(blob, name, "application/pdf");
  } catch (e) {
    const blob = await buildAnalysisPdf({ title, upload, section, data: { error: "Failed to load analysis" } });
    const name = `${slugify(title)}_${slugify(upload.original_filename)}_${Date.now()}.pdf`;
    downloadFile(blob, name, "application/pdf");
  }
}

export default function Reports() {
  const [isLive, setIsLive] = useState(false);
  const [uploads, setUploads] = useState<UploadMeta[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        const res = await listUploads();
        if (!mounted) return;
        const normalized: UploadMeta[] = (res || []).map((u: any) => ({
          id: u.id,
          original_filename: u.original_filename,
          created_at: u.created_at,
        }));
        setUploads(normalized);
      } catch (e) {
        console.error("Failed to load uploads", e);
      } finally {
        setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const sortedUploads = useMemo(() => {
    return [...uploads].sort((a, b) => +new Date(b.created_at) - +new Date(a.created_at));
  }, [uploads]);

  const mostRecent = sortedUploads[0] || null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
      <MobileNavigation />
      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-4">
          <LiveClock isLive={isLive} onToggleLive={setIsLive} matchTime={{ quarter: 0, timeRemaining: "" }} />

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Export Current Analysis (PDF)
              </CardTitle>
              <CardDescription>
                {mostRecent ? `Most recent: ${mostRecent.original_filename}` : loading ? "Loading..." : "No analyses found"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                <Button
                  className="bg-gradient-to-r from-purple-600 to-orange-600"
                  disabled={!mostRecent}
                  onClick={async () => {
                    if (!mostRecent) return;
                    await generatePDFWithFetcher(
                      "Player Analysis Report",
                      mostRecent,
                      "Player Analysis",
                      () => getPlayerDashboard(mostRecent.id).catch(() => null),
                    );
                  }}
                >
                  Player PDF
                </Button>
                <Button
                  className="bg-gradient-to-r from-purple-600 to-orange-600"
                  disabled={!mostRecent}
                  onClick={async () => {
                    if (!mostRecent) return;
                    await generatePDFWithFetcher(
                      "Crowd Analysis Report",
                      mostRecent,
                      "Crowd Analysis",
                      () => getCrowdAnalysis(mostRecent.id).catch(() => null),
                    );
                  }}
                >
                  Crowd PDF
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download className="w-5 h-5" />
                Previous Analyses
              </CardTitle>
              <CardDescription>
                {loading ? "Loading..." : "Download any past analysis as separate Player or Crowd reports"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {sortedUploads.map((u) => (
                  <div key={u.id} className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 p-3 border rounded-lg">
                    <div>
                      <div className="font-medium text-gray-900">{u.original_filename}</div>
                      <div className="text-xs text-gray-500">{new Date(u.created_at).toLocaleString()}</div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" onClick={async () => {
                        await generatePDFWithFetcher(
                          "Player Analysis Report",
                          u,
                          "Player Analysis",
                          () => getPlayerDashboard(u.id).catch(() => null),
                        );
                      }}>Player PDF</Button>
                      <Button variant="outline" onClick={async () => {
                        await generatePDFWithFetcher(
                          "Crowd Analysis Report",
                          u,
                          "Crowd Analysis",
                          () => getCrowdAnalysis(u.id).catch(() => null),
                        );
                      }}>Crowd PDF</Button>
                    </div>
                  </div>
                ))}
                {!loading && sortedUploads.length === 0 && (
                  <div className="text-sm text-gray-500">No analyses found.</div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
