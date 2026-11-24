/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BACKEND_URL?: string;
  /** "true" shows example players from client/lib/mockPlayers.ts (dev only). */
  readonly VITE_USE_MOCK_PLAYERS?: string;
}
