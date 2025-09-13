import React from "react";

export type Feature = {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
};

export default function FeatureCards({ features }: { features: Feature[] }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {features.map((feature, index) => {
        const Icon = feature.icon;
        return (
          <div key={index} className="p-4 bg-white rounded-lg border shadow-sm">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-100 to-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Icon className="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900">{feature.title}</h4>
                <p className="text-sm text-gray-600">{feature.description}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
