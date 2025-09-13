import React from "react";
import { Badge } from "@/components/ui/badge";
import { Activity, Monitor, Smartphone } from "lucide-react";

export default function HeaderBrand() {
  return (
    <header className="border-b bg-white/80 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-orange-600 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-orange-600 bg-clip-text text-transparent">
                AFL Analytics
              </h1>
              <p className="text-sm text-gray-600">Professional Sports Analytics Platform</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="hidden sm:flex">
              <Monitor className="w-3 h-3 mr-1" />
              Web App
            </Badge>
            <Badge variant="outline">
              <Smartphone className="w-3 h-3 mr-1" />
              Mobile Optimized
            </Badge>
          </div>
        </div>
      </div>
    </header>
  );
}
