import React from "react";

export function TeamCompareBar({
  label,
  aLabel,
  aValue,
  bLabel,
  bValue,
}: {
  label: string;
  aLabel: string;
  aValue: number;
  bLabel: string;
  bValue: number;
}) {
  const max = Math.max(aValue, bValue) || 1;
  const aPct = Math.round((aValue / max) * 100);
  const bPct = Math.round((bValue / max) * 100);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">{label}</span>
        <span className="text-gray-600">
          {aValue} vs {bValue}
        </span>
      </div>
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <span className="w-28 text-xs text-purple-700 truncate">{aLabel}</span>
          <div className="flex-1 bg-gray-200 rounded-full h-3">
            <div className="bg-purple-500 h-3 rounded-full" style={{ width: `${aPct}%` }} />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-28 text-xs text-orange-700 truncate">{bLabel}</span>
          <div className="flex-1 bg-gray-200 rounded-full h-3">
            <div className="bg-orange-600 h-3 rounded-full" style={{ width: `${bPct}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default TeamCompareBar;
