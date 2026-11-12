import { useLocation } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import MobileNavigation from "@/components/MobileNavigation";

// Routes that render without the app shell.
const BARE_ROUTES = ["/", "/login", "/stitch"];

export default function PageSkeleton() {
  const { pathname } = useLocation();
  const isBare = BARE_ROUTES.includes(pathname);

  const content = (
    <div className="p-4 space-y-6" role="status" aria-label="Loading page">
      <div className="space-y-2">
        <Skeleton className="h-9 w-64" />
        <Skeleton className="h-4 w-80" />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6 space-y-3">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-9 w-20" />
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent className="p-6 space-y-4">
          <Skeleton className="h-5 w-48" />
          <Skeleton className="h-64 w-full" />
        </CardContent>
      </Card>

      <span className="sr-only">Loading page…</span>
    </div>
  );

  if (isBare) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
        {content}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950">
      <MobileNavigation />
      <div className="lg:ml-64 pb-16 lg:pb-0">{content}</div>
    </div>
  );
}