import ConfirmLogout from "@/components/ConfirmLogout";
import { useState } from "react";
import { clearVideoState } from "@/lib/videoState";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Activity,
  BarChart3,
  Users,
  Download,
  Video,
  Menu,
  Home,
  Zap,
  Settings,
  LogOut,
  User,
} from "lucide-react";

const navigationItems = [
  {
    name: "Home",
    href: "/afl-dashboard",
    icon: Home,
    description: "Main dashboard",
  },
  {
    name: "Player Performance",
    href: "/player-performance",
    icon: BarChart3,
    description: "Player stats & analysis",
  },
  {
    name: "Crowd Monitor",
    href: "/crowd-monitor",
    icon: Users,
    description: "Stadium crowd analytics",
  },
  {
    name: "Analytics",
    href: "/analytics",
    icon: Video,
    description: "Video analysis & reports",
  },
  {
    name: "Reports",
    href: "/reports",
    icon: Download,
    description: "Download & manage reports",
  },
 
  // NEW PROFILE NAVIGATION
  {
    name: "Profile",
    href: "/profile",
    icon: User,
    description: "Account & role settings",
  },

  {
    name: "About",
    href: "/about",
    icon: Zap,
    description: "About this system",
  },
];

/*
 * Keep the existing mobile bottom navigation unchanged.
 *
 * Profile is available from:
 * 1. Desktop left sidebar
 * 2. Mobile side drawer
 *
 * But it does not replace any of your existing bottom-navigation items.
 */
const bottomNavigationItems = navigationItems.filter((item) =>
  [
    "Player Performance",
    "Crowd Monitor",
    "Analytics",
    "Reports",
    "About",
  ].includes(item.name),
);

export default function MobileNavigation() {
  const [isOpen, setIsOpen] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();

  /*
   * Automatically highlights the current page.
   *
   * Example:
   * URL = /profile
   * isActive("/profile") = true
   *
   * Therefore Profile receives the green active styling.
   */
  const isActive = (href: string) => {
    return location.pathname.startsWith(href);
  };

 const handleSettings = () => {
  setIsOpen(false);
  navigate("/settings");
};

  const handleLogout = () => {
    clearVideoState();
    /*
     * Remove authentication information.
     *
     * Do not remove "registeredUsers", because signup accounts
     * are currently stored under that key.
     */
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userName");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("authToken");
    localStorage.removeItem("authProvider");

    sessionStorage.removeItem("isAuthenticated");
    sessionStorage.removeItem("userEmail");
    sessionStorage.removeItem("userName");
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    sessionStorage.removeItem("authToken");
    sessionStorage.removeItem("authProvider");

    setIsOpen(false);

    navigate("/login", {
      replace: true,
    });
  };

  return (
    <>
      {/* ===================================================== */}
      {/* MOBILE HEADER */}
      {/* ===================================================== */}

      <header className="sticky top-0 z-50 border-b bg-white/95 backdrop-blur-sm lg:hidden">
        <div className="flex items-center justify-between px-4 py-3">
          {/* Mobile Logo */}
          <button
            type="button"
            onClick={() => navigate("/afl-dashboard")}
            className="flex items-center gap-2 text-left"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-green-600 to-blue-600">
              <Activity className="h-5 w-5 text-white" />
            </div>

            <span className="bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-lg font-bold text-transparent">
              AFL Analytics
            </span>
          </button>

          {/* Mobile Side Drawer */}
          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild>
              <Button
                type="button"
                variant="outline"
                size="sm"
                aria-label="Open navigation menu"
              >
                <Menu className="h-4 w-4" />
              </Button>
            </SheetTrigger>

            <SheetContent
              side="right"
              className="flex h-full w-80 flex-col p-0"
            >
              {/* Drawer Header */}
              <div className="flex items-center gap-2 border-b px-5 py-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-green-600 to-blue-600">
                  <Activity className="h-5 w-5 text-white" />
                </div>

                <span className="text-lg font-bold text-gray-900">
                  AFL Analytics
                </span>
              </div>

              {/* Drawer Navigation */}
              <nav className="flex-1 overflow-y-auto px-4 py-4">
                <div className="space-y-2">
                  {navigationItems.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.href);

                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        onClick={() => setIsOpen(false)}
                        className={`flex items-center gap-3 rounded-lg px-3 py-3 transition-all duration-200 ${
                          active
                            ? "border border-green-200 bg-gradient-to-r from-green-50 to-blue-50 text-green-700 shadow-sm"
                            : "hover:bg-gray-50"
                        }`}
                      >
                        <Icon
                          className={`h-5 w-5 shrink-0 ${
                            active
                              ? "text-green-600"
                              : "text-gray-500"
                          }`}
                        />

                        <div className="min-w-0 flex-1">
                          <div
                            className={`font-medium ${
                              active
                                ? "text-green-700"
                                : "text-gray-700"
                            }`}
                          >
                            {item.name}
                          </div>

                          <div className="text-xs text-gray-500">
                            {item.description}
                          </div>
                        </div>

                        {active && (
                          <div className="h-2 w-2 shrink-0 rounded-full bg-green-500" />
                        )}
                      </Link>
                    );
                  })}

                  {/* ================================================= */}
                  {/* SETTINGS */}
                  {/* ================================================= */}

                  <button
                    type="button"
                    onClick={handleSettings}
                    className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left transition-colors hover:bg-gray-50"
                  >
                    <Settings className="h-5 w-5 shrink-0 text-gray-500" />

                    <div className="min-w-0 flex-1">
                      <div className="font-medium text-gray-700">
                        Settings
                      </div>

                      <div className="text-xs text-gray-500">
                        Application preferences
                      </div>
                    </div>
                  </button>

                  {/* ================================================= */}
                  {/* LOGOUT */}
                  {/* ================================================= */}

                  <ConfirmLogout onConfirm={handleLogout}>
<button
                    type="button"
                    
                    className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-red-600 transition-colors hover:bg-red-50 hover:text-red-700"
                  >
                    <LogOut className="h-5 w-5 shrink-0" />

                    <div className="min-w-0 flex-1">
                      <div className="font-medium">
                        Logout
                      </div>

                      <div className="text-xs text-red-400">
                        Sign out of your account
                      </div>
                    </div>
                  </button>
</ConfirmLogout>
                </div>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </header>

      {/* ===================================================== */}
      {/* DESKTOP LEFT NAVIGATION */}
      {/* ===================================================== */}

      <nav className="fixed left-0 top-0 z-40 hidden h-full w-64 border-r bg-white lg:block">
        <div className="flex h-full flex-col">
          {/* Desktop Logo */}
          <div className="border-b p-6">
            <button
              type="button"
              onClick={() => navigate("/afl-dashboard")}
              className="flex items-center gap-3 text-left transition-opacity hover:opacity-90"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-green-600 to-blue-600">
                <Activity className="h-6 w-6 text-white" />
              </div>

              <h1 className="bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-xl font-bold text-transparent">
                AFL Analytics
              </h1>
            </button>
          </div>

          {/* Desktop Navigation Links */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);

                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center gap-3 rounded-lg px-3 py-3 transition-all duration-200 ${
                      active
                        ? "border border-green-200 bg-gradient-to-r from-green-50 to-blue-50 text-green-700 shadow-sm"
                        : "hover:bg-gray-50"
                    }`}
                  >
                    <Icon
                      className={`h-5 w-5 shrink-0 ${
                        active
                          ? "text-green-600"
                          : "text-gray-500"
                      }`}
                    />

                    <div className="min-w-0 flex-1">
                      <div
                        className={`font-medium ${
                          active
                            ? "text-green-700"
                            : "text-gray-700"
                        }`}
                      >
                        {item.name}
                      </div>

                      <div className="text-xs text-gray-500">
                        {item.description}
                      </div>
                    </div>

                    {active && (
                      <div className="h-2 w-2 shrink-0 rounded-full bg-green-500" />
                    )}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Desktop Logout */}
          <div className="border-t p-4">
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-red-600 transition-colors hover:bg-red-50 hover:text-red-700"
            >
              <LogOut className="h-5 w-5 shrink-0" />

              <div className="min-w-0 flex-1">
                <div className="font-medium">Logout</div>
                <div className="text-xs text-red-400">Sign out of your account</div>
              </div>
            </button>
          </div>
        </div>
      </nav>

      {/* ===================================================== */}
      {/* MOBILE BOTTOM NAVIGATION */}
      {/* ===================================================== */}

      <nav className="fixed bottom-0 left-0 right-0 z-40 border-t bg-white lg:hidden">
        <div className="grid grid-cols-6">
          {bottomNavigationItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex min-w-0 flex-col items-center px-1 py-2 transition-colors ${
                  active
                    ? "text-green-600"
                    : "text-gray-500 hover:bg-gray-100"
                }`}
              >
                <Icon className="mb-1 h-5 w-5" />

                <span className="w-full truncate text-center text-[10px] font-medium sm:text-xs">
                  {item.name.split(" ")[0]}
                </span>
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}