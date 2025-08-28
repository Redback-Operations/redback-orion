// OAuth configuration and types
export interface OAuthUser {
  id: string;
  email: string;
  name: string;
  picture?: string;
  provider: "google" | "apple";
}

export interface GoogleOAuthConfig {
  clientId: string;
  clientSecret: string;
  redirectUri: string;
}

export interface AppleOAuthConfig {
  clientId: string;
  teamId: string;
  keyId: string;
  privateKey: string;
  redirectUri: string;
}

export interface OAuthResponse {
  success: boolean;
  user?: OAuthUser;
  error?: string;
  accessToken?: string;
  refreshToken?: string;
}

// OAuth endpoints
export const OAUTH_ENDPOINTS = {
  google: {
    auth: "/api/auth/google",
    callback: "/api/auth/google/callback",
  },
  apple: {
    auth: "/api/auth/apple",
    callback: "/api/auth/apple/callback",
  },
} as const;
