import React from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { User } from "lucide-react";

export default function DemoAccessCard({ onLoadDemo }: { onLoadDemo: () => void }) {
  return (
    <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
      <div className="flex items-center space-x-2 mb-2">
        <User className="w-4 h-4 text-orange-600" />
        <span className="font-medium text-orange-900">Demo Access</span>
      </div>
      <p className="text-sm text-orange-700 mb-3">
        Try the platform with demo credentials to explore all features
      </p>
      <Button
        variant="outline"
        size="sm"
        onClick={onLoadDemo}
        className="text-orange-600 border-orange-300 hover:bg-orange-100"
      >
        Load Demo Credentials
      </Button>
    </div>
  );
}
