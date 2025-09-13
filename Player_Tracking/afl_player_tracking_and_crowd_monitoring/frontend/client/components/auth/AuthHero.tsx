import React from "react";
import { Badge } from "@/components/ui/badge";
import FeatureCards from "@/components/auth/FeatureCards";
import DemoAccessCard from "@/components/auth/DemoAccessCard";
import { Activity, Users, BarChart3, Video, Shield } from "lucide-react";

export default function AuthHero({ onLoadDemo }: { onLoadDemo: () => void }) {
  const features = [
    {
      icon: Activity,
      title: "Player Performance",
      description: "Real-time player statistics and performance metrics",
    },
    {
      icon: Users,
      title: "Crowd Monitoring",
      description: "Stadium crowd density and safety analytics",
    },
    {
      icon: BarChart3,
      title: "Advanced Analytics",
      description: "Comprehensive reporting and data insights",
    },
    {
      icon: Video,
      title: "Video Analysis",
      description: "AI-powered match video analysis and highlights",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <Badge variant="secondary" className="w-fit">
          <Shield className="w-3 h-3 mr-1" />
          Trusted by AFL Teams
        </Badge>
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900">
          Professional AFL
          <span className="block bg-gradient-to-r from-purple-600 to-orange-600 bg-clip-text text-transparent">
            Analytics Platform
          </span>
        </h2>
        <p className="text-lg text-gray-600">
          Comprehensive player performance tracking, crowd monitoring, and match analytics designed specifically for Australian Football League professionals.
        </p>
      </div>

      <FeatureCards features={features} />

      <DemoAccessCard onLoadDemo={onLoadDemo} />
    </div>
  );
}
