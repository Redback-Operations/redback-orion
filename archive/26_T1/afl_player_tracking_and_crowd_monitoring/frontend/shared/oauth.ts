// OAuth configuration and types

export interface OAuthUser {
  id: string;
  email: string;
  name: string;
  picture?: string;
  provider: "google" | "microsoft";
}

export interface GoogleOAuthConfig {
  clientId: string;
  clientSecret: string;
  redirectUri: string;
}

export interface MicrosoftOAuthConfig {
  clientId: string;
  tenantId?: string;
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

  microsoft: {
    auth: "/auth/microsoft",
  },
} as const;