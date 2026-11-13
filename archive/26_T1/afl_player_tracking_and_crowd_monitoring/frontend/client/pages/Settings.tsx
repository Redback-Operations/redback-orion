import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Bell,
  CheckCircle2,
  Contrast,
  Moon,
  Ruler,
  Type,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  TextSize,
  useThemePreferences,
} from "@/components/ThemePreferences";

function Toggle({
  checked,
  label,
  onChange,
}: {
  checked: boolean;
  label: string;
  onChange: () => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={onChange}
      className={`relative h-7 w-12 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 ${
        checked ? "bg-blue-600" : "bg-slate-300"
      }`}
    >
      <span
        className={`absolute top-1 h-5 w-5 rounded-full bg-white shadow transition-transform ${
          checked ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
  );
}

export default function Settings() {
  const navigate = useNavigate();
  const preferences = useThemePreferences();

  const [saved, setSaved] = useState(false);
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("Team member");

  useEffect(() => {
    const email = localStorage.getItem("userEmail") || "";

    setUsername(localStorage.getItem("userName") || email.split("@")[0] || "User",);
    setRole(localStorage.getItem("userRole") || "Team member");
  }, []);

  const save = (
    changes: Parameters<typeof preferences.updatePreferences>[0],
  ) => {
    preferences.updatePreferences(changes);
    setSaved(true);

    window.setTimeout(() => {
      setSaved(false);
    }, 3000);
  };

  const textSizes: { value: TextSize; label: string }[] = [
    { value: "normal", label: "Normal" },
    { value: "large", label: "Large" },
    { value: "extra-large", label: "Extra large" },
  ];

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8 dark:bg-slate-950">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="icon"
            onClick={() => navigate(-1)}
            aria-label="Go back"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>

          <div>
            <h1 className="text-3xl font-bold">Settings</h1>
            <p className="text-muted-foreground">
              Manage your account and application preferences.
            </p>
          </div>
        </div>

        {saved && (
          <div
            role="status"
            className="flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 p-3 text-green-800 dark:border-green-900 dark:bg-green-950 dark:text-green-200"
          >
            <CheckCircle2 className="h-5 w-5" />
            Preferences saved successfully.
          </div>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Account</CardTitle>
                      </CardHeader>

          <CardContent className="grid gap-2 text-sm">
            <p>
              <span className="font-medium">Username:</span> {username}
            </p>
            <p>
              <span className="font-medium">Role:</span> {role}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Moon className="h-5 w-5" />
              Appearance
            </CardTitle>
            <CardDescription>
              Choose how the application looks on this device.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-medium">Dark mode</p>
                <p className="text-sm text-muted-foreground">
                  Use a darker colour theme throughout the application.
                </p>
              </div>

              <Toggle
                checked={preferences.darkMode}
                label="Dark mode"
                onChange={() =>
                  save({ darkMode: !preferences.darkMode })
                }
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Notifications
            </CardTitle>
            <CardDescription>
              Select the alerts you would like to receive.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-medium">Match alerts</p>
                <p className="text-sm text-muted-foreground">
                  Receive important match and crowd alerts.
                </p>
              </div>

              <Toggle
                checked={preferences.matchAlerts}
                label="Match alerts"
                onChange={() =>
                  save({ matchAlerts: !preferences.matchAlerts })
                }
              />
            </div>

            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-medium">Player updates</p>
                <p className="text-sm text-muted-foreground">
                  Receive player-performance updates.
                </p>
              </div>

              <Toggle
                checked={preferences.playerUpdates}
                label="Player updates"
                onChange={() =>
                  save({ playerUpdates: !preferences.playerUpdates })
                }
              />
            </div>

            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-medium">System notifications</p>
                <p className="text-sm text-muted-foreground">
                  Receive application and account updates.
                </p>
              </div>

              <Toggle
                checked={preferences.systemNotifications}
                label="System notifications"
                onChange={() =>
                  save({
                    systemNotifications: !preferences.systemNotifications,
                  })
                }
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Ruler className="h-5 w-5" />
              Units
            </CardTitle>
            <CardDescription>
              Choose the measurement units shown in statistics.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="flex gap-3">
              <Button
                variant={preferences.units === "metric" ? "default" : "outline"}
                onClick={() => save({ units: "metric" })}
              >
                Metric
              </Button>

              <Button
                variant={
                  preferences.units === "imperial" ? "default" : "outline"
                }
                onClick={() => save({ units: "imperial" })}
              >
                Imperial
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Type className="h-5 w-5" />
              Accessibility
            </CardTitle>
            <CardDescription>
              Make the application easier to read and use.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-5">
            <div>
              <p className="mb-2 font-medium">Text size</p>

              <div className="flex flex-wrap gap-3">
                {textSizes.map((size) => (
                  <Button
                    key={size.value}
                    variant={
                      preferences.textSize === size.value
                        ? "default"
                        : "outline"
                    }
                    onClick={() => save({ textSize: size.value })}
                  >
                    {size.label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="flex items-center gap-2 font-medium">
                  <Contrast className="h-4 w-4" />
                  High contrast
                </p>
                <p className="text-sm text-muted-foreground">
                  Increase contrast between text, backgrounds and controls.
                </p>
              </div>

              <Toggle
                checked={preferences.highContrast}
                label="High contrast"
                onChange={() =>
                  save({ highContrast: !preferences.highContrast })
                }
              />
            </div>

            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="font-medium">Reduce motion</p>
                <p className="text-sm text-muted-foreground">
                  Minimise animations and movement on screen.
                </p>
              </div>

              <Toggle
                checked={preferences.reducedMotion}
                label="Reduce motion"
                onChange={() =>
                  save({ reducedMotion: !preferences.reducedMotion })
                }
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}