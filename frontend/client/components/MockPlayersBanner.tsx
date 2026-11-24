import { FlaskConical } from "lucide-react";
import { usingMockPlayers } from "@/lib/players";

/**
 * Shown above player screens while VITE_USE_MOCK_PLAYERS is on, so example
 * players are never mistaken for real ones. Renders nothing otherwise.
 */
export default function MockPlayersBanner() {
  if (!usingMockPlayers) return null;

  return (
    <div
      role="status"
      className="flex items-start gap-3 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      <FlaskConical className="mt-0.5 h-4 w-4 shrink-0" />
      <div>
        <p className="font-semibold">Showing example players</p>
        <p>
          These come from <code>client/lib/mockPlayers.ts</code>, not the
          database. Deleting or editing them won't work. To use real data,
          remove <code>VITE_USE_MOCK_PLAYERS</code> from{" "}
          <code>frontend/.env.local</code> and restart the dev server.
        </p>
      </div>
    </div>
  );
}
