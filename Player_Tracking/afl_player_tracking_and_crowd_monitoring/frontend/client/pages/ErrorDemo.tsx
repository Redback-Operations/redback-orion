import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import MobileNavigation from "@/components/MobileNavigation";
import ErrorPage, {
  NetworkError,
  ServerError,
  UnauthorizedError,
  ForbiddenError,
} from "@/pages/Error";
import LoadingState, {
  DataWrapper,
  SuccessState,
} from "@/components/LoadingState";
import {
  Activity,
  Bug,
  Wifi,
  Server,
  Shield,
  AlertTriangle,
  Loader2,
  CheckCircle,
} from "lucide-react";
import { Link } from "react-router-dom";

export default function ErrorDemo() {
  const [currentDemo, setCurrentDemo] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [dataState, setDataState] = useState<{
    data: any[];
    isLoading: boolean;
    error: string | null;
  }>({
    data: [],
    isLoading: false,
    error: null,
  });

  const handleJavaScriptError = () => {
    // This will trigger the ErrorBoundary
    throw new Error(
      "This is a test JavaScript error for ErrorBoundary demonstration",
    );
  };

  const simulateNetworkError = () => {
    setDataState({
      data: [],
      isLoading: false,
      error: "Network error: Failed to fetch data from server",
    });
  };

  const simulateLoadingState = () => {
    setIsLoading(true);
    setDataState({ ...dataState, isLoading: true, error: null });

    setTimeout(() => {
      setIsLoading(false);
      setDataState({
        data: [{ id: 1, name: "Sample Data" }],
        isLoading: false,
        error: null,
      });
    }, 3000);
  };

  const resetDataState = () => {
    setDataState({
      data: [],
      isLoading: false,
      error: null,
    });
    setCurrentDemo(null);
  };

  if (currentDemo) {
    switch (currentDemo) {
      case "network":
        return <NetworkError onRetry={() => setCurrentDemo(null)} />;
      case "server":
        return <ServerError code="500" onRetry={() => setCurrentDemo(null)} />;
      case "unauthorized":
        return <UnauthorizedError onRetry={() => setCurrentDemo(null)} />;
      case "forbidden":
        return <ForbiddenError onRetry={() => setCurrentDemo(null)} />;
      case "general":
        return (
          <ErrorPage
            title="General Error Demo"
            message="This is a demonstration of a general error page."
            onRetry={() => setCurrentDemo(null)}
          />
        );
      default:
        break;
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-orange-50">
      <MobileNavigation />

      <div className="lg:ml-64 pb-16 lg:pb-0">
        <div className="p-4 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-orange-600 bg-clip-text text-transparent">
                Error Demo Page
              </h1>
              <p className="text-gray-600 mt-2">
                Test different error states and fallback pages
              </p>
            </div>
            <Badge
              variant="outline"
              className="text-orange-600 border-orange-200"
            >
              Development Only
            </Badge>
          </div>

          {/* Error Pages Demo */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bug className="w-5 h-5" />
                Error Pages Demo
              </CardTitle>
              <CardDescription>
                Click any button below to see different error page layouts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                <Button
                  onClick={() => setCurrentDemo("network")}
                  variant="outline"
                  className="flex items-center gap-2 h-auto p-4 flex-col"
                >
                  <Wifi className="w-6 h-6 text-purple-600" />
                  <span className="text-center">
                    Network Error
                    <br />
                    <small className="text-gray-500">Connection issues</small>
                  </span>
                </Button>

                <Button
                  onClick={() => setCurrentDemo("server")}
                  variant="outline"
                  className="flex items-center gap-2 h-auto p-4 flex-col"
                >
                  <Server className="w-6 h-6 text-red-600" />
                  <span className="text-center">
                    Server Error
                    <br />
                    <small className="text-gray-500">500 Internal Error</small>
                  </span>
                </Button>

                <Button
                  onClick={() => setCurrentDemo("unauthorized")}
                  variant="outline"
                  className="flex items-center gap-2 h-auto p-4 flex-col"
                >
                  <Shield className="w-6 h-6 text-yellow-600" />
                  <span className="text-center">
                    Unauthorized
                    <br />
                    <small className="text-gray-500">401 Access Denied</small>
                  </span>
                </Button>

                <Button
                  onClick={() => setCurrentDemo("forbidden")}
                  variant="outline"
                  className="flex items-center gap-2 h-auto p-4 flex-col"
                >
                  <AlertTriangle className="w-6 h-6 text-orange-600" />
                  <span className="text-center">
                    Forbidden
                    <br />
                    <small className="text-gray-500">403 Forbidden</small>
                  </span>
                </Button>

                <Button
                  onClick={() => setCurrentDemo("general")}
                  variant="outline"
                  className="flex items-center gap-2 h-auto p-4 flex-col"
                >
                  <Bug className="w-6 h-6 text-purple-600" />
                  <span className="text-center">
                    General Error
                    <br />
                    <small className="text-gray-500">Generic error page</small>
                  </span>
                </Button>

                <Button
                  onClick={handleJavaScriptError}
                  variant="outline"
                  className="flex items-center gap-2 h-auto p-4 flex-col border-red-200 text-red-600 hover:bg-red-50"
                >
                  <AlertTriangle className="w-6 h-6" />
                  <span className="text-center">
                    JavaScript Error
                    <br />
                    <small className="text-gray-500">
                      Triggers ErrorBoundary
                    </small>
                  </span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Loading States Demo */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Loader2 className="w-5 h-5" />
                Loading & Data States Demo
              </CardTitle>
              <CardDescription>
                Test different loading and data states
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-3">
                <Button onClick={simulateLoadingState} disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    "Simulate Loading"
                  )}
                </Button>
                <Button onClick={simulateNetworkError} variant="outline">
                  Simulate Network Error
                </Button>
                <Button onClick={resetDataState} variant="outline">
                  Reset State
                </Button>
              </div>

              {/* Loading State Examples */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <h4 className="font-medium">Inline Loading</h4>
                  <LoadingState
                    isLoading={isLoading}
                    variant="inline"
                    loadingText="Fetching data..."
                  >
                    <div className="p-3 bg-orange-50 border border-orange-200 rounded">
                      ✅ Data loaded successfully!
                    </div>
                  </LoadingState>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium">Card Loading</h4>
                  <LoadingState
                    isLoading={isLoading}
                    variant="card"
                    loadingText="Processing..."
                  >
                    <Card>
                      <CardContent className="p-4">
                        <SuccessState
                          message="Success!"
                          description="Your data has been loaded."
                        />
                      </CardContent>
                    </Card>
                  </LoadingState>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium">Skeleton Loading</h4>
                  <LoadingState
                    isLoading={isLoading}
                    variant="skeleton"
                    skeletonRows={4}
                  >
                    <div className="space-y-2">
                      <div className="p-2 bg-gray-50 rounded">
                        Sample data row 1
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        Sample data row 2
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        Sample data row 3
                      </div>
                    </div>
                  </LoadingState>
                </div>

                <div className="space-y-3">
                  <h4 className="font-medium">Data Wrapper</h4>
                  <DataWrapper
                    data={dataState.data}
                    isLoading={dataState.isLoading}
                    error={dataState.error}
                    emptyMessage="No AFL data available"
                    onRetry={resetDataState}
                  >
                    <div className="p-3 bg-purple-50 border border-purple-200 rounded">
                      📊 AFL data: {dataState.data.length} items
                    </div>
                  </DataWrapper>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Navigation */}
          <Card>
            <CardHeader>
              <CardTitle>Navigation</CardTitle>
              <CardDescription>
                Return to main application pages
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                <Button asChild>
                  <Link to="/afl-dashboard">
                    <Activity className="w-4 h-4 mr-2" />
                    Dashboard
                  </Link>
                </Button>
                <Button asChild variant="outline">
                  <Link to="/login">Login Page</Link>
                </Button>
                <Button asChild variant="outline">
                  <Link to="/nonexistent-page">Test 404 Page</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
