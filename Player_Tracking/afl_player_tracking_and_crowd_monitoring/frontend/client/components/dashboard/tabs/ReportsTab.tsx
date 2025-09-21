import React, { useEffect, useMemo, useState } from "react";
import { getPlayerDashboard, getCrowdAnalysis, listUploads } from "@/lib/video";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, FileText } from "lucide-react";

interface UploadMeta {
  id: string;
  original_filename: string;
  created_at: string;
  status?: string;
}

function openPDF({
  title,
  upload,
  section,
  data,
}: {
  title: string;
  upload: UploadMeta;
  section: string;
  data: unknown;
}) {
  const win = window.open("", "_blank", "noopener,noreferrer");
  if (!win) return;

  const createdAt = upload.created_at
    ? new Date(upload.created_at).toLocaleString()
    : "";

  const html = `<!doctype html><html><head><meta charset=\"utf-8\"><title>${title}</title>
    <style>
      :root { --grad1: #7c3aed; --grad2: #fb923c; }
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, \"Helvetica Neue\", sans-serif; margin: 0; padding: 24px; color: #111827; }
      .title { font-size: 24px; font-weight: 800; background: linear-gradient(90deg, var(--grad1), var(--grad2)); -webkit-background-clip: text; background-clip: text; color: transparent; margin: 0 0 4px; }
      .meta { font-size: 12px; color: #6b7280; }
      .card { margin-top: 16px; padding: 16px; border: 1px solid #e5e7eb; border-radius: 10px; }
      .card h2 { margin: 0 0 8px; font-size: 16px; font-weight: 700; }
      pre { white-space: pre-wrap; word-break: break-word; background: #f9fafb; padding: 12px; border-radius: 8px; border: 1px solid #eef2f7; font-size: 12px; line-height: 1.5; }
      .footer { margin-top: 24px; font-size: 12px; color: #6b7280; }
    </style>
  </head><body>
    <h1 class="title">${title}</h1>
    <div class="meta">Upload: ${upload.original_filename} • Created: ${createdAt}</div>

    <div class="card">
      <h2>${section}</h2>
      <pre>${data ? JSON.stringify(data, null, 2) : "Not available"}</pre>
    </div>

    <div class="footer">Generated on ${new Date().toLocaleString()}</div>
    <script>window.print()</script>
  </body></html>`;

  win.document.write(html);
  win.document.close();
}

export default function ReportsTab({ upload }: { upload: UploadMeta | null }) {
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
          status: u.status || "Completed",
        }));
        setUploads(normalized);
      } catch (e) {
        console.error("Failed to load uploads", e);
      } finally {
        setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const sortedUploads = useMemo(() => {
    return [...uploads].sort((a, b) => +new Date(b.created_at) - +new Date(a.created_at));
  }, [uploads]);

  const handleCurrentPlayerPDF = async () => {
    if (!upload?.id) return;
    const player = await getPlayerDashboard(upload.id).catch(() => null);
    openPDF({ title: "Player Analysis Report", upload, section: "Player Analysis", data: player });
  };

  const handleCurrentCrowdPDF = async () => {
    if (!upload?.id) return;
    const crowd = await getCrowdAnalysis(upload.id).catch(() => null);
    openPDF({ title: "Crowd Analysis Report", upload, section: "Crowd Analysis", data: crowd });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Download className="w-6 h-6" />
            Reports
          </h2>
          <p className="text-gray-600">Download the analysis that has currently been run</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Export Current Analysis (PDF)
          </CardTitle>
          <CardDescription>
            {upload?.id ? `Selected: ${upload.original_filename}` : "Select a processed upload in Video Analysis first"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button
              className="bg-gradient-to-r from-purple-600 to-orange-600"
              disabled={!upload?.id}
              onClick={handleCurrentPlayerPDF}
            >
              Player PDF
            </Button>
            <Button
              className="bg-gradient-to-r from-purple-600 to-orange-600"
              disabled={!upload?.id}
              onClick={handleCurrentCrowdPDF}
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
                  <Button
                    variant="outline"
                    onClick={async () => {
                      const player = await getPlayerDashboard(u.id).catch(() => null);
                      openPDF({ title: "Player Analysis Report", upload: u, section: "Player Analysis", data: player });
                    }}
                  >
                    Player PDF
                  </Button>
                  <Button
                    variant="outline"
                    onClick={async () => {
                      const crowd = await getCrowdAnalysis(u.id).catch(() => null);
                      openPDF({ title: "Crowd Analysis Report", upload: u, section: "Crowd Analysis", data: crowd });
                    }}
                  >
                    Crowd PDF
                  </Button>
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
  );
}
