import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Skeleton that mirrors the real Player Performance layout:
 * a control bar, four stat cards, a filter panel and a player card grid.
 * Matching the real shape avoids layout shift when data arrives.
 */
export default function PlayerPerformanceSkeleton() {
  return (
    <div className="space-y-6" role="status" aria-label="Loading player data">
      {/* Live control bar */}
      <Card>
        <CardContent className="flex items-center gap-4 p-4">
          <Skeleton className="h-8 w-20 rounded-full" />
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-5 w-28" />
          <div className="flex-1" />
          <Skeleton className="h-9 w-28" />
        </CardContent>
      </Card>

      {/* Four summary stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6 space-y-3">
              <div className="flex items-center gap-2">
                <Skeleton className="h-4 w-4 rounded" />
                <Skeleton className="h-4 w-24" />
              </div>
              <Skeleton className="h-9 w-20" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Search and filters */}
      <Card>
        <CardHeader className="pb-3">
          <Skeleton className="h-5 w-44" />
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>

      {/* Player card grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <Card key={i} className="overflow-hidden">
            <Skeleton className="h-16 w-full rounded-none" />
            <CardContent className="space-y-4 p-4">
              <div className="flex items-center gap-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-28" />
                  <Skeleton className="h-3 w-20" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <span className="sr-only">Loading player data…</span>
    </div>
  );
}