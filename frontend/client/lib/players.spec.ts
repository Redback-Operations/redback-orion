import { afterEach, describe, expect, it, vi } from "vitest";
import {
  averageStats,
  formatStat,
  getPlayers,
  playersToCsv,
  sumStats,
  toPlayer,
  usingMockPlayers,
  type PlayerApiResponse,
} from "./players";
import { mockPlayers } from "./mockPlayers";

// A player exactly as the backend sends one today (PlayerResponse in
// backend/app/schemas/player.py). Tests copy it and change one thing.
const backendPlayer: PlayerApiResponse = {
  id: 7,
  name: "Marcus Bontempelli",
  team: "Western Bulldogs",
  position: "Midfielder",
  photo: "/uploads/players/7.jpg",
  kicks: 28,
  handballs: 12,
  marks: 8,
  tackles: 6,
  goals: 2,
  efficiency: 87,
  age: 28,
  height: "1.93m",
  weight: "92kg",
  jersey_number: 4,
  inside50s: 7,
  disposals: 40,
  team_logo: null,
  notes: null,
};

describe("toPlayer", () => {
  it("maps a player in today's backend shape", () => {
    const player = toPlayer(backendPlayer);

    expect(player).toMatchObject({
      id: 7,
      name: "Marcus Bontempelli",
      team: "Western Bulldogs",
      position: "Midfielder",
      number: 4,
      age: 28,
      height: "1.93m",
      weight: "92kg",
      photo: "/uploads/players/7.jpg",
    });
    expect(player.stats).toMatchObject({
      kicks: 28,
      handballs: 12,
      disposals: 40,
      marks: 8,
      tackles: 6,
      goals: 2,
      efficiency: 87,
      inside50s: 7,
    });
  });

  it("sets stats the backend doesn't send yet to null, not 0", () => {
    const { stats } = toPlayer(backendPlayer);

    expect(stats.contested).toBeNull();
    expect(stats.uncontested).toBeNull();
    expect(stats.clangers).toBeNull();
    expect(stats.avgSpeed).toBeNull();
    expect(stats.maxSpeed).toBeNull();
  });

  it("doesn't copy efficiency into goal accuracy", () => {
    expect(toPlayer(backendPlayer).stats.goalAccuracy).toBeNull();
  });

  it("reads the new fields once the backend sends them (contract names)", () => {
    const { stats } = toPlayer({
      ...backendPlayer,
      contested: 18,
      uncontested: 22,
      clangers: 3,
      goal_accuracy: 67,
      avg_speed: 24.8,
      max_speed: 32.4,
    });

    expect(stats).toMatchObject({
      contested: 18,
      uncontested: 22,
      clangers: 3,
      goalAccuracy: 67,
      avgSpeed: 24.8,
      maxSpeed: 32.4,
    });
  });

  it("keeps a real 0 as 0", () => {
    const { stats } = toPlayer({ ...backendPlayer, goals: 0, clangers: 0 });

    expect(stats.goals).toBe(0);
    expect(stats.clangers).toBe(0);
  });

  it("treats null, a missing field and an unreadable value as not measured", () => {
    const raw = { ...backendPlayer, goals: null, efficiency: "n/a" } as any;
    delete raw.tackles;

    const { stats } = toPlayer(raw);

    expect(stats.goals).toBeNull();
    expect(stats.tackles).toBeNull();
    expect(stats.efficiency).toBeNull();
  });

  it("turns numbers sent as text into numbers", () => {
    const player = toPlayer({
      ...backendPlayer,
      jersey_number: "12",
      kicks: "15",
    } as any);

    expect(player.number).toBe(12);
    expect(player.stats.kicks).toBe(15);
  });

  it("fills in defaults for missing profile details", () => {
    const player = toPlayer({
      ...backendPlayer,
      photo: null,
      height: null,
      weight: "",
    });

    expect(player.photo).toBe("/image.png");
    expect(player.height).toBe("-");
    expect(player.weight).toBe("-");
  });

  it("returns empty series when the backend doesn't send them", () => {
    const player = toPlayer(backendPlayer);

    expect(player.form).toEqual([]);
    expect(player.heatMap).toEqual([]);
    expect(player.possessionData).toEqual([]);
  });

  it("keeps series the backend sends, and ignores ones that aren't lists", () => {
    const player = toPlayer({
      ...backendPlayer,
      form: [85, 90],
      heat_map: [{ zone: "Forward 50", touches: 12, effectiveness: 85 }],
      possession_data: "not a list",
    } as any);

    expect(player.form).toEqual([85, 90]);
    expect(player.heatMap).toEqual([
      { zone: "Forward 50", touches: 12, effectiveness: 85 },
    ]);
    expect(player.possessionData).toEqual([]);
  });
});

describe("formatStat", () => {
  it("shows a dash for a stat that wasn't measured", () => {
    expect(formatStat(null)).toBe("—");
    expect(formatStat(null, "%")).toBe("—");
  });

  it("shows the value with its unit", () => {
    expect(formatStat(82, "%")).toBe("82%");
    expect(formatStat(24.8, " km/h")).toBe("24.8 km/h");
  });

  it("shows a real 0 as 0", () => {
    expect(formatStat(0)).toBe("0");
  });
});

describe("sumStats", () => {
  it("adds up only the measured values", () => {
    expect(sumStats([2, null, 3])).toBe(5);
  });

  it("counts a real 0", () => {
    expect(sumStats([0, 0])).toBe(0);
  });

  it("is null when nothing was measured", () => {
    expect(sumStats([null, null])).toBeNull();
    expect(sumStats([])).toBeNull();
  });
});

describe("averageStats", () => {
  it("averages only the measured values", () => {
    // If null counted as 0, this would be 41, not 82.
    expect(averageStats([82, null])).toBe(82);
    expect(averageStats([80, 90, null])).toBe(85);
  });

  it("is null when nothing was measured", () => {
    expect(averageStats([null])).toBeNull();
    expect(averageStats([])).toBeNull();
  });
});

describe("getPlayers", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  // Swaps in a fake fetch that answers with `body` and `status`, and returns
  // it so a test can check what was requested.
  const fakeFetch = (body: unknown, status = 200) => {
    const fetchMock = vi.fn(
      async () =>
        new Response(JSON.stringify(body), {
          status,
          headers: { "Content-Type": "application/json" },
        }),
    );
    vi.stubGlobal("fetch", fetchMock);
    return fetchMock;
  };

  // Swaps in a fake localStorage holding `token` (or nothing).
  const fakeLogin = (token: string | null) => {
    vi.stubGlobal("localStorage", {
      getItem: (key: string) => (key === "accessToken" ? token : null),
    });
  };

  it("loads players and converts each one", async () => {
    fakeLogin(null);
    fakeFetch([backendPlayer, { ...backendPlayer, id: 8, goals: null }]);

    const players = await getPlayers();

    expect(players).toHaveLength(2);
    expect(players[0].stats.goals).toBe(2);
    expect(players[1].id).toBe(8);
    expect(players[1].stats.goals).toBeNull();
  });

  it("calls /api/players and sends the login token", async () => {
    fakeLogin("test-token");
    const fetchMock = fakeFetch([]);

    await getPlayers();

    const [url, options] = fetchMock.mock.calls[0] as unknown as [
      string,
      RequestInit,
    ];
    expect(url).toMatch(/\/api\/players$/);
    expect(options.headers).toMatchObject({
      Authorization: "Bearer test-token",
    });
  });

  it("leaves out the Authorization header when nobody is logged in", async () => {
    fakeLogin(null);
    const fetchMock = fakeFetch([]);

    await getPlayers();

    const [, options] = fetchMock.mock.calls[0] as unknown as [
      string,
      RequestInit,
    ];
    expect(options.headers).not.toHaveProperty("Authorization");
  });

  it("uses the backend's error message when it sends one", async () => {
    fakeLogin(null);
    fakeFetch({ detail: "Not authenticated" }, 401);

    await expect(getPlayers()).rejects.toThrow("Not authenticated");
  });

  it("falls back to a readable message when the error isn't text", async () => {
    fakeLogin(null);
    // FastAPI validation errors send detail as a list, not a string.
    fakeFetch({ detail: [{ loc: ["query"], msg: "bad" }] }, 422);

    await expect(getPlayers()).rejects.toThrow(
      "Couldn't load players (error 422)",
    );
  });

  it("rejects a response that isn't a list of players", async () => {
    fakeLogin(null);
    fakeFetch({ players: [] });

    await expect(getPlayers()).rejects.toThrow(
      "The server sent player data in an unexpected format.",
    );
  });
});

describe("example players (mockPlayers.ts)", () => {
  const players = mockPlayers.map(toPlayer);

  it("are off unless VITE_USE_MOCK_PLAYERS is set", () => {
    // The getPlayers tests above rely on this: they expect a real request.
    expect(usingMockPlayers).toBe(false);
  });

  it("all convert into players with readable values", () => {
    for (const player of players) {
      expect(player.id).toBeGreaterThan(0);
      expect(player.name).toMatch(/^Example: /);
      for (const value of Object.values(player.stats)) {
        // Every stat is either a real number or null, never NaN.
        expect(value === null || Number.isFinite(value)).toBe(true);
      }
    }
  });

  it("have unique ids", () => {
    const ids = players.map((p) => p.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("cover the cases the screens need to handle", () => {
    const statValues = players.flatMap((p) => Object.values(p.stats));

    // Not-measured stats and real zeros.
    expect(statValues).toContain(null);
    expect(statValues).toContain(0);
    // Players with and without each series.
    expect(players.some((p) => p.form.length > 0)).toBe(true);
    expect(players.some((p) => p.form.length === 0)).toBe(true);
    expect(players.some((p) => p.heatMap.length > 0)).toBe(true);
    expect(players.some((p) => p.possessionData.length > 0)).toBe(true);
    // Every position the filter offers.
    expect(new Set(players.map((p) => p.position))).toEqual(
      new Set(["Midfielder", "Forward", "Defender", "Ruckman"]),
    );
  });
});

describe("playersToCsv", () => {
  // Splits CSV text into rows, dropping the byte-order mark and the final
  // line break.
  const rows = (csv: string) =>
    csv.replace(/^﻿/, "").replace(/\r\n$/, "").split("\r\n");

  it("writes a header row, then one row per player", () => {
    const csv = playersToCsv([toPlayer(backendPlayer)]);
    const [header, row] = rows(csv);

    expect(header).toBe(
      "id,name,team,position,jersey_number,age,height,weight," +
        "kicks,handballs,disposals,marks,tackles,goals,efficiency,inside50s," +
        "contested,uncontested,clangers,goal_accuracy,avg_speed_kmh,max_speed_kmh",
    );
    expect(row).toBe(
      "7,Marcus Bontempelli,Western Bulldogs,Midfielder,4,28,1.93m,92kg," +
        "28,12,40,8,6,2,87,7,,,,,,",
    );
  });

  it("starts with a byte-order mark so Excel reads accented names", () => {
    expect(playersToCsv([]).startsWith("﻿")).toBe(true);
  });

  it("writes only the header when there are no players", () => {
    expect(rows(playersToCsv([]))).toHaveLength(1);
  });

  it("leaves not-measured stats blank and keeps real zeros", () => {
    const player = toPlayer({ ...backendPlayer, goals: null, clangers: 0 });
    const [header, row] = rows(playersToCsv([player])).map((r) => r.split(","));

    expect(row[header.indexOf("goals")]).toBe("");
    expect(row[header.indexOf("clangers")]).toBe("0");
  });

  it("quotes text containing commas, quotes or line breaks", () => {
    const player = toPlayer({
      ...backendPlayer,
      name: 'Tom "The Tank" O\'Neil, Jr',
      team: "Line\nBreak",
    });
    const csv = playersToCsv([player]);

    expect(csv).toContain('"Tom ""The Tank"" O\'Neil, Jr"');
    expect(csv).toContain('"Line\nBreak"');
  });

  it("stops names being run as spreadsheet formulas", () => {
    const player = toPlayer({ ...backendPlayer, name: "=HYPERLINK(\"x\")" });
    const [, row] = rows(playersToCsv([player]));

    expect(row.split(",")[1]).toBe(`"'=HYPERLINK(""x"")"`);
  });

  it("leaves negative numbers alone", () => {
    // Only text is guarded against formulas; a number is never a formula.
    const player = toPlayer(backendPlayer);
    player.stats.kicks = -1;
    const [header, row] = rows(playersToCsv([player])).map((r) => r.split(","));

    expect(row[header.indexOf("kicks")]).toBe("-1");
  });
});
