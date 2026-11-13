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
