import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {
  Activity,
  BarChart3,
  Users,
  Download,
  Video,
  Menu,
  Home,
  Zap,
  Terminal,
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
  {
    name: "API Diagnostics",
    href: "/api-diagnostics",
    icon: Terminal,
    description: "System monitoring",
  },
];

export default function MobileNavigation() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const isActive = (href: string) => {
    if (href === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile Header */}
      <header className="lg:hidden border-b bg-white/95 backdrop-blur-sm sticky top-0 z-50">
        <div className="flex items-center justify-between px-4 py-3">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              AFL Analytics
            </span>
          </Link>

          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild>
              <Button variant="outline" size="sm">
                <Menu className="w-4 h-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-80">
              <div className="flex flex-col h-full">
                <div className="flex items-center space-x-2 pb-4 border-b">
                  <div className="w-8 h-8 bg-gradient-to-br from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
                    <Activity className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-lg font-bold">AFL Analytics</span>
                </div>

                <nav className="flex-1 py-4">
                  <div className="space-y-2">
                    {navigationItems.map((item) => {
                      const Icon = item.icon;
                      const active = isActive(item.href);

                      return (
                        <Link
                          key={item.name}
                          to={item.href}
                          onClick={() => setIsOpen(false)}
                          className={`flex items-center space-x-3 px-3 py-3 rounded-lg transition-colors ${
                            active
                              ? "bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 text-green-700"
                              : "hover:bg-gray-50"
                          }`}
                        >
                          <Icon
                            className={`w-5 h-5 ${active ? "text-green-600" : "text-gray-500"}`}
                          />
                          <div className="flex-1">
                            <div
                              className={`font-medium ${active ? "text-green-700" : "text-gray-700"}`}
                            >
                              {item.name}
                            </div>
                            <div className="text-xs text-gray-500">
                              {item.description}
                            </div>
                          </div>
                          {active && (
                            <div className="w-2 h-2 bg-green-500 rounded-full" />
                          )}
                        </Link>
                      );
                    })}
                  </div>
                </nav>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </header>

      {/* Desktop Navigation */}
      <nav className="hidden lg:block fixed left-0 top-0 h-full w-64 bg-white border-r z-40">
        <div className="flex flex-col h-full">
          <div className="flex items-center space-x-2 p-6 border-b">
            <div className="w-8 h-8 bg-gradient-to-br from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              AFL Analytics
            </span>
          </div>

          <div className="flex-1 p-4">
            <div className="space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);

                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center space-x-3 px-3 py-3 rounded-lg transition-colors ${
                      active
                        ? "bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 text-green-700"
                        : "hover:bg-gray-50"
                    }`}
                  >
                    <Icon
                      className={`w-5 h-5 ${active ? "text-green-600" : "text-gray-500"}`}
                    />
                    <div className="flex-1">
                      <div
                        className={`font-medium ${active ? "text-green-700" : "text-gray-700"}`}
                      >
                        {item.name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {item.description}
                      </div>
                    </div>
                    {active && (
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </nav>

      {/* Bottom Navigation for Mobile */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t z-40">
        <div className="grid grid-cols-5 gap-1">
          {navigationItems.slice(0, 5).map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex flex-col items-center py-2 px-1 transition-colors ${
                  active ? "text-green-600" : "text-gray-500"
                }`}
              >
                <Icon className="w-5 h-5 mb-1" />
                <span className="text-xs font-medium truncate">
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
