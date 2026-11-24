// Example players for building the Player Performance screens while the
// database is empty. They are only used when VITE_USE_MOCK_PLAYERS=true is
// set in frontend/.env.local, and only under `pnpm dev`; production builds
// never include this file (see getPlayers() in players.ts).
//
// Every player is in the shape GET /api/players should send under the
// Player Performance data contract, so this file doubles as a worked example
// for the backend team. The names are made up.
//
// The set deliberately covers the cases the screens must handle:
//   - players in today's backend shape, with none of the new fields
//   - players with every contract field filled in
//   - null ("not measured") stats, and real 0s
//   - every position and several teams, for the filters

import type { PlayerApiResponse } from "./players";

export const mockPlayers: PlayerApiResponse[] = [
  // Everything filled in, including the three series.
  {
    id: 9001,
    name: "Example: Riley Hart",
    team: "Western Bulldogs",
    position: "Midfielder",
    photo: null,
    jersey_number: 4,
    age: 27,
    height: "1.88m",
    weight: "86kg",
    kicks: 24,
    handballs: 14,
    disposals: 38,
    marks: 7,
    tackles: 8,
    goals: 1,
    efficiency: 84,
    inside50s: 6,
    contested: 17,
    uncontested: 21,
    clangers: 3,
    goal_accuracy: 50,
    avg_speed: 24.6,
    max_speed: 32.1,
    form: [78, 84, 91, 88, 73, 86, 92, 81, 89, 94],
    heat_map: [
      { zone: "Forward 50", touches: 9, effectiveness: 78 },
      { zone: "Center Bounce", touches: 21, effectiveness: 88 },
      { zone: "Defensive 50", touches: 8, effectiveness: 81 },
    ],
    possession_data: [
      { time: 0, possession: 0 },
      { time: 20, possession: 9 },
      { time: 40, possession: 17 },
      { time: 60, possession: 25 },
      { time: 80, possession: 32 },
      { time: 100, possession: 38 },
    ],
  },

  // A forward with every field filled in.
  {
    id: 9002,
    name: "Example: Jordan Pike",
    team: "Carlton",
    position: "Forward",
    photo: null,
    jersey_number: 11,
    age: 24,
    height: "1.95m",
    weight: "94kg",
    kicks: 14,
    handballs: 4,
    disposals: 18,
    marks: 9,
    tackles: 2,
    goals: 4,
    efficiency: 72,
    inside50s: 3,
    contested: 8,
    uncontested: 10,
    clangers: 2,
    goal_accuracy: 67,
    avg_speed: 22.9,
    max_speed: 33.4,
    form: [70, 92, 65, 88, 95, 74, 81, 90, 68, 85],
    heat_map: [
      { zone: "Forward 50", touches: 14, effectiveness: 74 },
      { zone: "Center Bounce", touches: 3, effectiveness: 67 },
      { zone: "Defensive 50", touches: 1, effectiveness: 100 },
    ],
    possession_data: [
      { time: 0, possession: 0 },
      { time: 20, possession: 4 },
      { time: 40, possession: 7 },
      { time: 60, possession: 11 },
      { time: 80, possession: 15 },
      { time: 100, possession: 18 },
    ],
  },

  // Today's backend shape: no contract fields, so those show as "—" and the
  // charts that need series show "No data yet".
  {
    id: 9003,
    name: "Example: Casey Doyle",
    team: "Richmond",
    position: "Defender",
    photo: null,
    jersey_number: 25,
    age: 29,
    height: "1.91m",
    weight: "90kg",
    kicks: 18,
    handballs: 7,
    disposals: 25,
    marks: 8,
    tackles: 3,
    goals: 0,
    efficiency: 88,
    inside50s: 1,
  },

  // A ruckman with some stats not measured (null) and a real 0 for clangers.
  {
    id: 9004,
    name: "Example: Alex Brennan",
    team: "Melbourne",
    position: "Ruckman",
    photo: null,
    jersey_number: 18,
    age: 31,
    height: "2.04m",
    weight: "105kg",
    kicks: 9,
    handballs: 11,
    disposals: 20,
    marks: 4,
    tackles: 5,
    goals: null,
    efficiency: null,
    inside50s: 2,
    contested: 14,
    uncontested: 6,
    clangers: 0,
    goal_accuracy: null,
    avg_speed: null,
    max_speed: null,
    form: [82, 77, 85, 80],
    heat_map: [],
    possession_data: [],
  },

  // Another midfielder on a different team, in today's backend shape.
  {
    id: 9005,
    name: "Example: Morgan Tate",
    team: "Geelong",
    position: "Midfielder",
    photo: null,
    jersey_number: 7,
    age: 22,
    height: "1.83m",
    weight: "80kg",
    kicks: 16,
    handballs: 13,
    disposals: 29,
    marks: 5,
    tackles: 6,
    goals: 2,
    efficiency: 79,
    inside50s: 5,
  },

  // A forward with only partial contract data.
  {
    id: 9006,
    name: "Example: Sam Ellery",
    team: "Brisbane",
    position: "Forward",
    photo: null,
    jersey_number: 30,
    age: 26,
    height: "1.86m",
    weight: "85kg",
    kicks: 11,
    handballs: 6,
    disposals: 17,
    marks: 6,
    tackles: 4,
    goals: 3,
    efficiency: 76,
    inside50s: 4,
    goal_accuracy: 60,
    avg_speed: 25.8,
    max_speed: 34.0,
    form: [66, 71, 79, 84, 88, 90],
  },
];
