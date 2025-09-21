import React, { useEffect, useState } from "react";
import { getPlayerDashboard } from "@/lib/video";

interface PlayerRow {
  player_id: number;
  distance_m: number;
  avg_speed_kmh: number;
  max_speed_kmh: number;
  heatmap_url: string;
  zone_heatmaps?: {
    back_50?: string;
    midfield?: string;
    forward_50?: string;
  };
}

interface TeamHeatmap {
  team_heatmap_url: string;
  zones: {
    back_50?: string;
    midfield?: string;
    forward_50?: string;
  };
}

interface PlayerDashboardResponse {
  upload_id: string;
  team?: TeamHeatmap;
  players: PlayerRow[];
  status?: string; // ✅ to handle not_available
}

interface UploadMeta {
  id: string;
  original_filename: string;
  created_at: string;
  status: string;
}

interface PlayerPerformanceTabProps {
  upload: UploadMeta | null;
}

export default function PlayerPerformanceTab({ upload }: PlayerPerformanceTabProps) {
  const [dashboard, setDashboard] = useState<PlayerDashboardResponse | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerRow | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!upload?.id) return;

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getPlayerDashboard(upload.id);

        if (data?.status === "not_available") {
          setError("⚠ Player tracking was not run for this video.");
        } else {
          setDashboard(data);
        }
      } catch (err) {
        console.error("❌ Failed to load player performance dashboard:", err);
        setError("⚠ Player tracking was not run for this video.");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [upload?.id]);

  const handlePlayerClick = (playerId: number) => {
    const player = dashboard?.players.find((p) => p.player_id === playerId);
    if (player) {
      setSelectedPlayer(player);
    }
  };

  if (!upload) {
    return <p className="p-4 text-gray-500">Upload a video to view player performance.</p>;
  }

  if (loading) {
    return <p className="p-4">Loading player performance...</p>;
  }

  if (error) {
    return <p className="p-4 text-red-500">{error}</p>;
  }

  if (!dashboard) {
    return <p className="p-4 text-gray-500">No analysis data available.</p>;
  }

  return (
    <div className="space-y-6 text-gray-900">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-purple-700 dark:text-purple-400">
          Player Performance – {upload.original_filename}
        </h2>
        <p className="text-sm text-gray-500">
          Uploaded: {new Date(upload.created_at).toLocaleString()}
        </p>
      </div>

      {dashboard.team && (
        <div>
          <h2 className="text-lg font-semibold mb-2 text-gray-800">Team Heatmaps</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <img src={dashboard.team.team_heatmap_url} alt="Team Heatmap" className="rounded-lg shadow ring-1 ring-gray-200 bg-white" />
            {dashboard.team.zones.back_50 && <img src={dashboard.team.zones.back_50} alt="Back 50" className="rounded-lg shadow ring-1 ring-gray-200 bg-white" />}
            {dashboard.team.zones.midfield && <img src={dashboard.team.zones.midfield} alt="Midfield" className="rounded-lg shadow ring-1 ring-gray-200 bg-white" />}
            {dashboard.team.zones.forward_50 && <img src={dashboard.team.zones.forward_50} alt="Forward 50" className="rounded-lg shadow ring-1 ring-gray-200 bg-white" />}
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold mb-2 text-gray-800">Player Stats</h2>
        <table className="w-full border border-gray-200 rounded-lg overflow-hidden bg-white text-sm">
          <thead>
            <tr className="bg-gradient-to-r from-purple-600 to-orange-600 text-white">
              <th className="p-3">Player ID</th>
              <th className="p-3">Distance (m)</th>
              <th className="p-3">Avg Speed (km/h)</th>
              <th className="p-3">Max Speed (km/h)</th>
              <th className="p-3">Heatmap</th>
            </tr>
          </thead>
          <tbody>
            {dashboard.players.map((p) => (
              <tr
                key={p.player_id}
                onClick={() => handlePlayerClick(p.player_id)}
                className="cursor-pointer hover:bg-purple-50/50 even:bg-gray-50/40 transition-colors"
              >
                <td className="p-3">{p.player_id}</td>
                <td className="p-3">{p.distance_m?.toFixed(2)}</td>
                <td className="p-3">{p.avg_speed_kmh?.toFixed(2)}</td>
                <td className="p-3">{p.max_speed_kmh?.toFixed(2)}</td>
                <td className="p-3">
                  {p.heatmap_url && (
                    <img
                      src={p.heatmap_url}
                      alt={`Player ${p.player_id} Heatmap`}
                      className="w-16 h-16 object-cover rounded-md ring-1 ring-gray-200 bg-white"
                    />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedPlayer && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center">
          <div className="bg-white p-6 rounded-xl shadow-2xl max-w-2xl w-[90%] border border-purple-100">
            <h3 className="text-xl font-bold text-purple-700 mb-3">
              Player {selectedPlayer.player_id} Details
            </h3>
            <p>Distance: {selectedPlayer.distance_m?.toFixed(2)} m</p>
            <p>Avg Speed: {selectedPlayer.avg_speed_kmh?.toFixed(2)} km/h</p>
            <p>Max Speed: {selectedPlayer.max_speed_kmh?.toFixed(2)} km/h</p>

            <div className="grid grid-cols-2 gap-3 mt-4">
              {selectedPlayer.heatmap_url && <img src={selectedPlayer.heatmap_url} alt="Player Heatmap" className="rounded-lg ring-1 ring-gray-200 bg-white" />}
              {selectedPlayer.zone_heatmaps && (
                <>
                  {selectedPlayer.zone_heatmaps.back_50 && <img src={selectedPlayer.zone_heatmaps.back_50} alt="Back 50 Zone" className="rounded-lg ring-1 ring-gray-200 bg-white" />}
                  {selectedPlayer.zone_heatmaps.midfield && <img src={selectedPlayer.zone_heatmaps.midfield} alt="Midfield Zone" className="rounded-lg ring-1 ring-gray-200 bg-white" />}
                  {selectedPlayer.zone_heatmaps.forward_50 && <img src={selectedPlayer.zone_heatmaps.forward_50} alt="Forward 50 Zone" className="rounded-lg ring-1 ring-gray-200 bg-white" />}
                </>
              )}
            </div>

            <button
              onClick={() => setSelectedPlayer(null)}
              className="mt-5 px-4 py-2 bg-gradient-to-r from-purple-600 to-orange-600 text-white rounded-md hover:opacity-90 transition"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
