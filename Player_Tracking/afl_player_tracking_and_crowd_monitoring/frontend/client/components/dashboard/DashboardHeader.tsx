import React from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Activity, Settings, LogOut } from "lucide-react";

export default function DashboardHeader({
  isLive,
  userEmail,
  onLogout,
}: {
  isLive: boolean;
  userEmail?: string;
  onLogout: () => void;
}) {
  return (
    <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-orange-600 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-orange-600 bg-clip-text text-transparent">
                AFL Analytics
              </h1>
              <p className="text-sm text-gray-600">Real-time match insights & player analytics</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Badge variant={isLive ? "destructive" : "secondary"} className="animate-pulse">
              <div className="w-2 h-2 rounded-full bg-red-500 mr-2" />
              {isLive ? "LIVE" : "OFFLINE"}
            </Badge>
            {userEmail && (
              <span className="text-sm text-gray-600 hidden sm:block">Welcome, {userEmail}</span>
            )}
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
            <Button variant="outline" size="sm" onClick={onLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
