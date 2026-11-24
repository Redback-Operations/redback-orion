// The one place that knows what GET /api/players sends and turns it into the
// Player shape the pages use. When the backend changes a field name or adds a
// field, update PlayerApiResponse and toPlayer() here; TypeScript then points
// at every screen that needs to change.

import { BACKEND_URL } from "@/lib/config";
import { getAccessToken } from "@/lib/auth";

// ---------------------------------------------------------------------------
// What the backend sends
// ---------------------------------------------------------------------------

/**
 * One row from GET /api/players. Mirrors PlayerResponse in
 * backend/app/schemas/player.py.
 */
export type PlayerApiResponse = {
  id: number;
  name: string;
  team: string;
  position: string;
  photo?: string | null;

  kicks: number;
  handballs: number;
  marks: number;
  tackles: number;
  goals: number;
  efficiency: number;

  age: number;
  height?: string | null;
  weight?: string | null;

  jersey_number: number;
  inside50s: number;
  disposals: number;

  team_logo?: string | null;
  notes?: string | null;

  // Proposed in the Player Performance data contract; the backend doesn't
  // send these yet. toPlayer() already reads them, so they appear on screen
  // as soon as the backend adds them. null means "not measured".
  contested?: number | null;
  uncontested?: number | null;
  clangers?: number | null;
  goal_accuracy?: number | null;
  avg_speed?: number | null;
  max_speed?: number | null;

  // Note: the contract proposes form as {round, score} objects. If the
  // backend adopts that, convert it in toPlayer().
  form?: number[];
  heat_map?: HeatMapZone[];
  possession_data?: PossessionPoint[];
};

// ---------------------------------------------------------------------------
// What the pages use
// ---------------------------------------------------------------------------

export type HeatMapZone = {
  zone: string;
  touches: number;
  effectiveness: number;
};

export type PossessionPoint = {
  time: number;
  possession: number;
};

/**
 * A stat value. null means "not measured": show it with formatStat() as "—",
 * never as 0, and leave it out of totals, averages and charts.
 *
 * tsconfig has strictNullChecks off, so TypeScript won't warn if you forget.
 * Whenever you show or do maths with a stat, handle null yourself.
 */
export type Stat = number | null;

export type PlayerStats = {
  kicks: Stat;
  handballs: Stat;
  disposals: Stat;
  marks: Stat;
  tackles: Stat;
  goals: Stat;
  efficiency: Stat;
  inside50s: Stat;
  contested: Stat;
  uncontested: Stat;
  clangers: Stat;
  /** Percent, 0–100. */
  goalAccuracy: Stat;
  /** km/h. */
  avgSpeed: Stat;
  /** km/h. */
  maxSpeed: Stat;
};

export type Player = {
  id: number;
  name: string;
  team: string;
  position: string;
  /** Jersey number. */
  number: number;
  age: number;
  height: string;
  weight: string;
  photo: string;
  stats: PlayerStats;
  /** Form scores for recent games. Empty until the backend sends them. */
  form: number[];
  heatMap: HeatMapZone[];
  possessionData: PossessionPoint[];
};

// ---------------------------------------------------------------------------
// Conversion
// ---------------------------------------------------------------------------

/** Turns a missing value into 0 and a numeric string into a number. For ids and other non-stat numbers. */
const num = (value: unknown): number => Number(value ?? 0) || 0;

/**
 * For stats: a missing or unreadable value becomes null ("not measured"),
 * a numeric string like "12" becomes 12, and a real 0 stays 0.
 */
const stat = (value: unknown): Stat => {
  if (value === null || value === undefined || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
};

const list = <T>(value: unknown): T[] => (Array.isArray(value) ? value : []);

// ---------------------------------------------------------------------------
// Helpers for showing stats
// ---------------------------------------------------------------------------

/** "—" for a stat that wasn't measured, otherwise the value plus its unit. */
export const formatStat = (value: Stat, unit = ""): string =>
  value === null || value === undefined ? "—" : `${value}${unit}`;

/** Adds up the measured values only. null if none were measured. */
export const sumStats = (values: Stat[]): Stat => {
  const measured = values.filter((v): v is number => v !== null && v !== undefined);
  return measured.length ? measured.reduce((a, b) => a + b, 0) : null;
};

/** Averages the measured values only. null if none were measured. */
export const averageStats = (values: Stat[]): Stat => {
  const measured = values.filter((v): v is number => v !== null && v !== undefined);
  return measured.length
    ? measured.reduce((a, b) => a + b, 0) / measured.length
    : null;
};

/** Converts one backend row into the Player shape the pages use. */
export function toPlayer(raw: PlayerApiResponse): Player {
  return {
    id: num(raw.id),
    name: raw.name ?? "",
    team: raw.team ?? "",
    position: raw.position ?? "",
    number: num(raw.jersey_number),
    age: num(raw.age),
    height: raw.height || "-",
    weight: raw.weight || "-",
    photo: raw.photo || "/image.png",
    stats: {
      kicks: stat(raw.kicks),
      handballs: stat(raw.handballs),
      disposals: stat(raw.disposals),
      marks: stat(raw.marks),
      tackles: stat(raw.tackles),
      goals: stat(raw.goals),
      efficiency: stat(raw.efficiency),
      inside50s: stat(raw.inside50s),

      // Not sent by the backend yet, so these are null ("—") until it does.
      contested: stat(raw.contested),
      uncontested: stat(raw.uncontested),
      clangers: stat(raw.clangers),
      goalAccuracy: stat(raw.goal_accuracy),
      avgSpeed: stat(raw.avg_speed),
      maxSpeed: stat(raw.max_speed),
    },
    form: list<number>(raw.form),
    heatMap: list<HeatMapZone>(raw.heat_map),
    possessionData: list<PossessionPoint>(raw.possession_data),
  };
}

// ---------------------------------------------------------------------------
// Fetching
// ---------------------------------------------------------------------------

/**
 * True when the screens should show the example players from mockPlayers.ts
 * instead of calling the backend. Turn it on by putting
 * VITE_USE_MOCK_PLAYERS=true in frontend/.env.local and restarting `pnpm dev`.
 *
 * `import.meta.env.DEV` is false in production builds, so this is always
 * false there, whatever the .env files say.
 */
export const usingMockPlayers =
  import.meta.env.DEV && import.meta.env.VITE_USE_MOCK_PLAYERS === "true";

/**
 * Loads every player from GET /api/players.
 * Throws an Error with a readable message if the request fails.
 */
export async function getPlayers(): Promise<Player[]> {
  if (usingMockPlayers) {
    // Loaded only when needed. In a production build `usingMockPlayers` is
    // the constant false, so the bundler drops this branch and the example
    // players never ship.
    const { mockPlayers } = await import("./mockPlayers");
    return mockPlayers.map(toPlayer);
  }

  const token = getAccessToken();

  const response = await fetch(`${BACKEND_URL}/api/players`, {
    headers: {
      Accept: "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      typeof data?.detail === "string"
        ? data.detail
        : typeof data?.message === "string"
          ? data.message
          : `Couldn't load players (error ${response.status})`;
    throw new Error(message);
  }

  if (!Array.isArray(data)) {
    throw new Error("The server sent player data in an unexpected format.");
  }

  return data.map(toPlayer);
}

// ---------------------------------------------------------------------------
// CSV export
// ---------------------------------------------------------------------------

/** The export's columns, in order. Names match the data contract. */
const CSV_COLUMNS: Array<[header: string, value: (p: Player) => unknown]> = [
  ["id", (p) => p.id],
  ["name", (p) => p.name],
  ["team", (p) => p.team],
  ["position", (p) => p.position],
  ["jersey_number", (p) => p.number],
  ["age", (p) => p.age],
  ["height", (p) => p.height],
  ["weight", (p) => p.weight],
  ["kicks", (p) => p.stats.kicks],
  ["handballs", (p) => p.stats.handballs],
  ["disposals", (p) => p.stats.disposals],
  ["marks", (p) => p.stats.marks],
  ["tackles", (p) => p.stats.tackles],
  ["goals", (p) => p.stats.goals],
  ["efficiency", (p) => p.stats.efficiency],
  ["inside50s", (p) => p.stats.inside50s],
  ["contested", (p) => p.stats.contested],
  ["uncontested", (p) => p.stats.uncontested],
  ["clangers", (p) => p.stats.clangers],
  ["goal_accuracy", (p) => p.stats.goalAccuracy],
  ["avg_speed_kmh", (p) => p.stats.avgSpeed],
  ["max_speed_kmh", (p) => p.stats.maxSpeed],
];

/** Formats one value as a CSV cell. */
const csvCell = (value: unknown): string => {
  // Not measured: an empty cell, which spreadsheets treat as blank rather
  // than 0. ("—" is for the screen only.)
  if (value === null || value === undefined) return "";
  if (typeof value === "number") return String(value);

  let text = String(value);
  // A cell starting with = + - or @ is run as a formula by Excel and Google
  // Sheets. Player names come from the database, so neutralise that.
  if (/^[=+\-@]/.test(text)) text = `'${text}`;
  // Quote cells containing a comma, quote or line break; double any quotes.
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
};

/**
 * Turns players into CSV text: a header row, then one row per player.
 * Starts with a byte-order mark so Excel reads accented names correctly.
 */
export function playersToCsv(players: Player[]): string {
  const header = CSV_COLUMNS.map(([name]) => name).join(",");
  const rows = players.map((player) =>
    CSV_COLUMNS.map(([, value]) => csvCell(value(player))).join(","),
  );
  return "﻿" + [header, ...rows].join("\r\n") + "\r\n";
}
