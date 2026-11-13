export type Role = "user" | "admin" | "player" | "coach";

export interface AuthUser {
  user_id: string;
  username: string;
  email: string;
  role: Role;
  player_id?: number | null;
  created_at: string;
}

export function saveAuthSession(authResponse: {
  access_token: string;
  user: AuthUser;
}) {
  localStorage.setItem("accessToken", authResponse.access_token);
  localStorage.setItem("user", JSON.stringify(authResponse.user));
}

export function getCurrentUser(): AuthUser | null {
  const raw = localStorage.getItem("user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function getRole(): Role | null {
  return getCurrentUser()?.role ?? null;
}

export function isAdmin(): boolean {
  return getRole() === "admin";
}

export function clearAuthSession() {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("user");
}

export function logout() {
  clearAuthSession();
  window.location.href = "/login";
}

export function canManagePlayers(): boolean {
  const role = getRole();
  return role === "admin" || role === "coach";
}
// Restored from 26_T1 (used by PeakCrowdCard).
// Single place that knows where the login token is stored.
// The app has historically written the token under more than one key, so the
// lookup checks each of them in order.
const TOKEN_KEYS = ["accessToken", "access_token", "authToken"] as const;

export const getAccessToken = (): string | null => {
  try {
    for (const key of TOKEN_KEYS) {
      const value = localStorage.getItem(key);
      if (value) return value;
    }
  } catch {
    // storage unavailable
  }
  return null;
};

// The built-in demo login stores a placeholder token the real backend rejects.
export const isDemoToken = (token: string | null): boolean =>
  !!token && token.startsWith("demo_");
