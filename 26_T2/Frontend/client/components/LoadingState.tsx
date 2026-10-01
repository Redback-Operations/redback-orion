import { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Loader2,
  RefreshCw,
  AlertCircle,
  Wifi,
  Server,
  Clock,
  CheckCircle,
} from "lucide-react";

interface LoadingStateProps {
  isLoading?: boolean;
  error?: Error | string | null;
  isEmpty?: boolean;
  children?: ReactNode;
  loadingText?: string;
  emptyText?: string;
  emptyDescription?: string;
  onRetry?: () => void;
  retryText?: string;
  showRetry?: boolean;
  variant?: "default" | "card" | "inline" | "skeleton";
  skeletonRows?: number;
}

export default function LoadingState({
  isLoading = false,
  error = null,
  isEmpty = false,
  children,
  loadingText = "Loading...",
  emptyText = "No data available",
  emptyDescription = "There's nothing to show here yet.",
  onRetry,
  retryText = "Try Again",
  showRetry = true,
  variant = "default",
  skeletonRows = 3,
}: LoadingStateProps) {
  // Loading state
  if (isLoading) {
    if (variant === "skeleton") {
      return (
        <div className="space-y-3">
          {Array.from({ length: skeletonRows }).map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ))}
        </div>
      );
    }

    if (variant === "inline") {
      return (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-2">
            <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
            <span className="text-sm text-gray-600">{loadingText}</span>
          </div>
        </div>
      );
    }

    if (variant === "card") {
      return (
        <Card>
          <CardContent className="p-8 text-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">{loadingText}</p>
          </CardContent>
        </Card>
      );
    }

    // Default loading
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="w-12 h-12 animate-spin text-blue-600 mb-4" />
        <p className="text-lg text-gray-600">{loadingText}</p>
      </div>
    );
  }

  // Error state
  if (error) {
    const errorMessage = typeof error === "string" ? error : error.message;
    const isNetworkError =
      errorMessage.toLowerCase().includes("network") ||
      errorMessage.toLowerCase().includes("fetch");
    const isServerError =
      errorMessage.toLowerCase().includes("server") ||
      errorMessage.includes("5");

    const ErrorIcon = isNetworkError
      ? Wifi
      : isServerError
        ? Server
        : AlertCircle;
    const errorColor = isNetworkError
      ? "text-blue-600"
      : isServerError
        ? "text-red-600"
        : "text-orange-600";
    const bgColor = isNetworkError
      ? "bg-blue-50 border-blue-200"
      : isServerError
        ? "bg-red-50 border-red-200"
        : "bg-orange-50 border-orange-200";

    if (variant === "inline") {
      return (
        <Alert variant="destructive" className="my-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex items-center justify-between">
            <span>{errorMessage}</span>
            {showRetry && onRetry && (
              <Button size="sm" variant="outline" onClick={onRetry}>
                <RefreshCw className="w-3 h-3 mr-1" />
                {retryText}
              </Button>
            )}
          </AlertDescription>
        </Alert>
      );
    }

    if (variant === "card") {
      return (
        <Card>
          <CardContent className="p-8 text-center">
            <ErrorIcon className={`w-12 h-12 mx-auto mb-4 ${errorColor}`} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {isNetworkError
                ? "Connection Error"
                : isServerError
                  ? "Server Error"
                  : "Error"}
            </h3>
            <p className="text-gray-600 mb-4">{errorMessage}</p>
            {showRetry && onRetry && (
              <Button onClick={onRetry}>
                <RefreshCw className="w-4 h-4 mr-2" />
                {retryText}
              </Button>
            )}
          </CardContent>
        </Card>
      );
    }

    // Default error
    return (
      <div className={`p-6 rounded-lg border ${bgColor}`}>
        <div className="flex items-start space-x-3">
          <ErrorIcon className={`w-6 h-6 ${errorColor} mt-1 flex-shrink-0`} />
          <div className="flex-1">
            <h3 className="font-medium text-gray-900 mb-1">
              {isNetworkError
                ? "Connection Problem"
                : isServerError
                  ? "Server Error"
                  : "Something went wrong"}
            </h3>
            <p className="text-gray-600 mb-3">{errorMessage}</p>
            {showRetry && onRetry && (
              <Button size="sm" variant="outline" onClick={onRetry}>
                <RefreshCw className="w-4 h-4 mr-2" />
                {retryText}
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (isEmpty) {
    if (variant === "inline") {
      return (
        <div className="text-center py-6">
          <p className="text-gray-500">{emptyText}</p>
        </div>
      );
    }

    if (variant === "card") {
      return (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Clock className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {emptyText}
            </h3>
            <p className="text-gray-600">{emptyDescription}</p>
          </CardContent>
        </Card>
      );
    }

    // Default empty
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Clock className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">{emptyText}</h3>
        <p className="text-gray-600">{emptyDescription}</p>
      </div>
    );
  }

  // Success state - render children
  return <>{children}</>;
}

// Specialized loading components
export const SkeletonLoader = ({ rows = 3 }: { rows?: number }) => (
  <LoadingState isLoading variant="skeleton" skeletonRows={rows} />
);

export const InlineLoader = ({ text = "Loading..." }: { text?: string }) => (
  <LoadingState isLoading variant="inline" loadingText={text} />
);

export const CardLoader = ({ text = "Loading..." }: { text?: string }) => (
  <LoadingState isLoading variant="card" loadingText={text} />
);

// Data fetching wrapper component
interface DataWrapperProps {
  data: any;
  isLoading: boolean;
  error: Error | string | null;
  children: ReactNode;
  emptyMessage?: string;
  onRetry?: () => void;
}

export const DataWrapper = ({
  data,
  isLoading,
  error,
  children,
  emptyMessage = "No data available",
  onRetry,
}: DataWrapperProps) => {
  const isEmpty = !data || (Array.isArray(data) && data.length === 0);

  return (
    <LoadingState
      isLoading={isLoading}
      error={error}
      isEmpty={isEmpty}
      emptyText={emptyMessage}
      onRetry={onRetry}
      variant="card"
    >
      {children}
    </LoadingState>
  );
};

// Success state component
export const SuccessState = ({
  message = "Success!",
  description,
  action,
}: {
  message?: string;
  description?: string;
  action?: ReactNode;
}) => (
  <div className="text-center py-8">
    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
      <CheckCircle className="w-8 h-8 text-green-600" />
    </div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">{message}</h3>
    {description && <p className="text-gray-600 mb-4">{description}</p>}
    {action}
  </div>
);
