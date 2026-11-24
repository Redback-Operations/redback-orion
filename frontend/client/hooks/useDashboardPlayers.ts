import { useEffect, useState } from "react";
import { getPlayers, type Player } from "@/lib/players";
import type { DashboardPlayer } from "@/components/dashboard/types";

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

/**
 * The Home tab works with a flatter shape plus a spot on the field.
 * It starts from the shared Player, so backend changes only need handling in
 * lib/players.ts.
 */
const toDashboardPlayer = (player: Player): DashboardPlayer => {
  const fieldPosition = getFieldPositionForRole(player.position);

  return {
    id: player.id,
    name: player.name,
    team: player.team,
    position: player.position,
    number: player.number,
    fieldX: fieldPosition.fieldX,
    fieldY: fieldPosition.fieldY,
    kicks: player.stats.kicks,
    handballs: player.stats.handballs,
    marks: player.stats.marks,
    tackles: player.stats.tackles,
    goals: player.stats.goals,
    efficiency: player.stats.efficiency,
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
      const databasePlayers = (await getPlayers()).map(toDashboardPlayer);

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
