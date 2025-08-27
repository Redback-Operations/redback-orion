import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Activity, 
  Home, 
  ArrowLeft, 
  RefreshCw, 
  AlertCircle,
  Bug,
  Wifi,
  Server
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

interface ErrorPageProps {
  type?: "general" | "network" | "server" | "unauthorized" | "forbidden";
  title?: string;
  message?: string;
  code?: string | number;
  details?: string;
  onRetry?: () => void;
  showRetry?: boolean;
}

export default function Error({
  type = "general",
  title,
  message,
  code,
  details,
  onRetry,
  showRetry = true
}: ErrorPageProps) {
  const navigate = useNavigate();

  const getErrorConfig = () => {
    switch (type) {
      case "network":
        return {
          icon: Wifi,
          color: "text-blue-600",
          bgColor: "from-blue-100 to-blue-200",
          badge: "Network Error",
          badgeVariant: "secondary" as const,
          defaultTitle: "Connection Problem",
          defaultMessage: "Unable to connect to AFL Analytics servers. Please check your internet connection and try again.",
          defaultCode: "NETWORK_ERROR"
        };
      case "server":
        return {
          icon: Server,
          color: "text-red-600",
          bgColor: "from-red-100 to-red-200",
          badge: "Server Error",
          badgeVariant: "destructive" as const,
          defaultTitle: "Server Error",
          defaultMessage: "Our servers are experiencing technical difficulties. Our team has been notified and is working to resolve this issue.",
          defaultCode: code || "500"
        };
      case "unauthorized":
        return {
          icon: AlertCircle,
          color: "text-yellow-600",
          bgColor: "from-yellow-100 to-yellow-200",
          badge: "Unauthorized",
          badgeVariant: "secondary" as const,
          defaultTitle: "Access Denied",
          defaultMessage: "You don't have permission to access this resource. Please sign in with appropriate credentials.",
          defaultCode: "401"
        };
      case "forbidden":
        return {
          icon: AlertCircle,
          color: "text-orange-600",
          bgColor: "from-orange-100 to-orange-200",
          badge: "Forbidden",
          badgeVariant: "secondary" as const,
          defaultTitle: "Access Forbidden",
          defaultMessage: "You don't have the required permissions to access this resource.",
          defaultCode: "403"
        };
      default:
        return {
          icon: Bug,
          color: "text-purple-600",
          bgColor: "from-purple-100 to-purple-200",
          badge: "Error",
          badgeVariant: "secondary" as const,
          defaultTitle: "Something Went Wrong",
          defaultMessage: "An unexpected error occurred. Please try again or contact support if the problem persists.",
          defaultCode: code || "ERROR"
        };
    }
  };

  const config = getErrorConfig();
  const Icon = config.icon;

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      window.location.reload();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex flex-col">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/afl-dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-green-600 to-blue-600 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
              AFL Analytics
            </span>
          </Link>
          <Badge variant={config.badgeVariant}>
            {config.badge}
            {config.defaultCode && ` (${config.defaultCode})`}
          </Badge>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="max-w-2xl w-full">
          <Card className="text-center border-0 shadow-lg">
            <CardHeader className="pb-6">
              <div className={`w-20 h-20 bg-gradient-to-br ${config.bgColor} rounded-full flex items-center justify-center mx-auto mb-4`}>
                <Icon className={`w-10 h-10 ${config.color}`} />
              </div>
              <CardTitle className="text-3xl">
                {title || config.defaultTitle}
              </CardTitle>
              <CardDescription className="text-lg">
                {message || config.defaultMessage}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {details && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-left">
                    <strong>Technical Details:</strong> {details}
                  </AlertDescription>
                </Alert>
              )}

              <div className="flex flex-col sm:flex-row gap-3">
                {showRetry && (
                  <Button
                    onClick={handleRetry}
                    className="bg-gradient-to-r from-green-600 to-blue-600 flex-1"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Try Again
                  </Button>
                )}
                <Button
                  asChild
                  variant="outline"
                  className="flex-1"
                >
                  <Link to="/afl-dashboard">
                    <Home className="w-4 h-4 mr-2" />
                    Go to Dashboard
                  </Link>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => navigate(-1)}
                  className="flex-1"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Go Back
                </Button>
              </div>

              {type === "server" && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-900 mb-2">What can you do?</h4>
                  <ul className="text-sm text-blue-700 space-y-1 text-left">
                    <li>• Wait a few minutes and try again</li>
                    <li>• Check our status page for ongoing issues</li>
                    <li>• Contact support if the problem persists</li>
                    <li>• Try accessing a different section of the platform</li>
                  </ul>
                </div>
              )}

              {type === "network" && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-900 mb-2">Troubleshooting steps:</h4>
                  <ul className="text-sm text-blue-700 space-y-1 text-left">
                    <li>• Check your internet connection</li>
                    <li>• Disable VPN if you're using one</li>
                    <li>• Try refreshing the page</li>
                    <li>• Clear your browser cache and cookies</li>
                  </ul>
                </div>
              )}

              {(type === "unauthorized" || type === "forbidden") && (
                <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <h4 className="font-medium text-yellow-900 mb-2">Need access?</h4>
                  <ul className="text-sm text-yellow-700 space-y-1 text-left">
                    <li>• Make sure you're signed in with the correct account</li>
                    <li>• Contact your administrator for access permissions</li>
                    <li>• Verify your subscription includes this feature</li>
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

// Pre-configured error components for common use cases
export const NetworkError = (props: Omit<ErrorPageProps, "type">) => (
  <Error type="network" {...props} />
);

export const ServerError = (props: Omit<ErrorPageProps, "type">) => (
  <Error type="server" {...props} />
);

export const UnauthorizedError = (props: Omit<ErrorPageProps, "type">) => (
  <Error type="unauthorized" {...props} />
);

export const ForbiddenError = (props: Omit<ErrorPageProps, "type">) => (
  <Error type="forbidden" {...props} />
);
