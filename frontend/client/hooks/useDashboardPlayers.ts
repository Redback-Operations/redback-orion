import { useEffect, useState } from "react";
import { BACKEND_URL } from "@/lib/config";
import type { DashboardPlayer } from "@/components/dashboard/types";

const getAccessToken = () =>
  localStorage.getItem("accessToken") ||
  localStorage.getItem("access_token") ||
  localStorage.getItem("authToken");

const getFieldPositionForRole = (position: string) => {
  const role = position.trim().toLowerCase();

  if (role.includes("forward")) {
    return { fieldX: 50, fieldY: 24 };
  }

  if (role.includes("defender") || role.includes("back")) {
    return { fieldX: 50, fieldY: 76 };
  }

  if (role.includes("ruck")) {
    return { fieldX: 50, fieldY: 50 };
  }

  if (role.includes("mid") || role.includes("wing")) {
    return { fieldX: 50, fieldY: 50 };
  }

  return { fieldX: 50, fieldY: 50 };
};

const normalizeDatabasePlayer = (player: any): DashboardPlayer => {
  const fieldPosition = getFieldPositionForRole(player.position || "");

  return {
    id: Number(player.id),
    name: player.name || "",
    team: player.team || "",
    position: player.position || "",
    number: Number(player.jersey_number ?? player.jerseyNumber ?? 0),
    fieldX: fieldPosition.fieldX,
    fieldY: fieldPosition.fieldY,
    kicks: Number(player.kicks ?? 0),
    handballs: Number(player.handballs ?? 0),
    marks: Number(player.marks ?? 0),
    tackles: Number(player.tackles ?? 0),
    goals: Number(player.goals ?? 0),
    efficiency: Number(player.efficiency ?? 0),
  };
};

/** Loads players from the backend and holds selection/search state for the Player Performance tab. */
export function useDashboardPlayers() {
  const [players, setPlayers] = useState<DashboardPlayer[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<DashboardPlayer | null>(
    null,
  );
  const [comparisonPlayer, setComparisonPlayer] =
    useState<DashboardPlayer | null>(null);
  const [playersLoading, setPlayersLoading] = useState(true);
  const [playersError, setPlayersError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTeam, setSelectedTeam] = useState("all");

  const loadDatabasePlayers = async () => {
    setPlayersLoading(true);
    setPlayersError(null);

    try {
      const token = getAccessToken();

      const response = await fetch(`${BACKEND_URL}/api/players`, {
        headers: {
          Accept: "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      const data = await response.json().catch(() => []);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `Unable to load players (${response.status})`,
        );
      }

      if (!Array.isArray(data)) {
        throw new Error("Player API returned an unexpected response.");
      }

      const databasePlayers = data.map(normalizeDatabasePlayer);

      setPlayers(databasePlayers);
      setSelectedPlayer(databasePlayers[0] ?? null);
      setComparisonPlayer(databasePlayers[1] ?? databasePlayers[0] ?? null);
    } catch (error) {
      console.error("Failed to load database players:", error);
      setPlayers([]);
      setSelectedPlayer(null);
      setComparisonPlayer(null);
      setPlayersError(
        error instanceof Error ? error.message : "Unable to load players.",
      );
    } finally {
      setPlayersLoading(false);
    }
  };

  useEffect(() => {
    void loadDatabasePlayers();
  }, []);

  const filteredPlayers = players.filter(
    (player) =>
      player.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedTeam === "all" || player.team === selectedTeam),
  );

  // Field display is intentionally search-driven:
  // no player marker is shown until the user searches for a player.
  const normalizedPlayerSearch = searchTerm.trim().toLowerCase();

  const searchedFieldPlayers = normalizedPlayerSearch
    ? players.filter((player) =>
        player.name.toLowerCase().includes(normalizedPlayerSearch),
      )
    : [];

  return {
    players,
    playersLoading,
    playersError,
    loadDatabasePlayers,
    selectedPlayer,
    setSelectedPlayer,
    comparisonPlayer,
    setComparisonPlayer,
    searchTerm,
    setSearchTerm,
    selectedTeam,
    setSelectedTeam,
    filteredPlayers,
    normalizedPlayerSearch,
    searchedFieldPlayers,
  };
}

export type DashboardPlayersState = ReturnType<typeof useDashboardPlayers>;
