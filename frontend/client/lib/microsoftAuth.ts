import {
  Configuration,
  LogLevel,
  PublicClientApplication,
} from "@azure/msal-browser";

const microsoftClientId =
  import.meta.env.VITE_MICROSOFT_CLIENT_ID;

if (!microsoftClientId) {
  console.warn(
    "VITE_MICROSOFT_CLIENT_ID is missing. Microsoft login will not be available."
  );
}

export const msalConfig: Configuration = {
  auth: {
    clientId: microsoftClientId || "",

    authority:
      "https://login.microsoftonline.com/common",

    redirectUri:
      `${window.location.origin}/redirect.html`,

    postLogoutRedirectUri:
      window.location.origin,
  },

  cache: {
    cacheLocation: "localStorage",
  },

  system: {
    loggerOptions: {
      loggerCallback: (
        level,
        message,
        containsPii
      ) => {
        if (containsPii) return;

        if (level === LogLevel.Error) {
          console.error(message);
        } else if (
          level === LogLevel.Warning
        ) {
          console.warn(message);
        }
      },
    },
  },
};

export const microsoftLoginRequest = {
  scopes: [
    "openid",
    "profile",
    "email",
  ],
};

export const msalInstance =
  new PublicClientApplication(msalConfig);