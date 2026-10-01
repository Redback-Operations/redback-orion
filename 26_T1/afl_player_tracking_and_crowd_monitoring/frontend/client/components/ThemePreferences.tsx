import { createContext, ReactNode, useContext, useEffect, useState } from "react";

export type TextSize = "normal" | "large" | "extra-large";

type Preferences = {
  darkMode: boolean;
  textSize: TextSize;
  highContrast: boolean;
  reducedMotion: boolean;
  units: "metric" | "imperial";
  matchAlerts: boolean;
  playerUpdates: boolean;
  systemNotifications: boolean;
};

type ThemePreferencesContextValue = Preferences & {
  updatePreferences: (changes: Partial<Preferences>) => void;
};

const STORAGE_KEY = "aflPreferences";

const defaults: Preferences = {
  darkMode: false,
  textSize: "normal",
  highContrast: false,
  reducedMotion: false,
  units: "metric",
  matchAlerts: true,
  playerUpdates: true,
  systemNotifications: true,
};

const ThemePreferencesContext =
  createContext<ThemePreferencesContextValue | undefined>(undefined);

function readPreferences(): Preferences {
  try {
    return {
      ...defaults,
      ...JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"),
    };
  } catch {
    return defaults;
  }
}

export function ThemePreferencesProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [preferences, setPreferences] = useState<Preferences>(readPreferences);

  useEffect(() => {
    const root = document.documentElement;

    root.classList.toggle("dark", preferences.darkMode);
    root.classList.toggle("high-contrast", preferences.highContrast);
    root.classList.toggle("reduce-motion", preferences.reducedMotion);
    root.dataset.textSize = preferences.textSize;

    localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
  }, [preferences]);

  const updatePreferences = (changes: Partial<Preferences>) => {
    setPreferences((current) => ({ ...current, ...changes }));
  };

  return (
    <ThemePreferencesContext.Provider
      value={{ ...preferences, updatePreferences }}
    >
      {children}
    </ThemePreferencesContext.Provider>
  );
}

export function useThemePreferences() {
  const context = useContext(ThemePreferencesContext);

  if (!context) {
    throw new Error(
      "useThemePreferences must be used within ThemePreferencesProvider",
    );
  }

  return context;
}