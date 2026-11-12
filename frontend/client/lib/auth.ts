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