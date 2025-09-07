import React, { Component, ErrorInfo, ReactNode } from "react";
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
  RefreshCw,
  Bug,
  AlertTriangle,
  Copy,
  ExternalLink,
} from "lucide-react";
import { Link } from "react-router-dom";

interface Props {
  children?: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    showDetails: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
      showDetails: false,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);

    this.setState({
      error,
      errorInfo,
    });

    // Call the onError callback if provided - wrap in try/catch to prevent cascading errors
    try {
      if (this.props.onError) {
        this.props.onError(error, errorInfo);
      }
    } catch (callbackError) {
      console.error("Error in ErrorBoundary onError callback:", callbackError);
    }

    // In a real app, you might want to send this to a logging service
    // logErrorToService(error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    });
  };

  private handleReload = () => {
    window.location.reload();
  };

  private copyErrorDetails = () => {
    try {
      const errorDetails = this.getErrorDetails();
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard
          .writeText(errorDetails)
          .then(() => {
            console.log("Error details copied to clipboard");
          })
          .catch((error) => {
            console.error("Failed to copy to clipboard:", error);
            // Fallback: try to select text or show alert
            this.fallbackCopy(errorDetails);
          });
      } else {
        this.fallbackCopy(errorDetails);
      }
    } catch (error) {
      console.error("Copy operation failed:", error);
    }
  };

  private fallbackCopy = (text: string) => {
    try {
      // Try to use the old execCommand method as fallback
      const textArea = document.createElement("textarea");
      textArea.value = text;
      textArea.style.position = "fixed";
      textArea.style.left = "-999999px";
      textArea.style.top = "-999999px";
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();

      try {
        document.execCommand("copy");
        console.log("Error details copied using fallback method");
      } finally {
        if (textArea.parentNode) {
          textArea.parentNode.removeChild(textArea);
        }
      }
    } catch (fallbackError) {
      console.error("Fallback copy failed:", fallbackError);
      // Last resort: show alert with the text
      alert("Copy failed. Here are the error details:\n\n" + text);
    }
  };

  private getErrorDetails = () => {
    const { error, errorInfo } = this.state;
    return `
AFL Analytics - Error Report
============================
Time: ${new Date().toISOString()}
URL: ${window.location.href}
User Agent: ${navigator.userAgent}

Error: ${error?.message || "Unknown error"}
Stack: ${error?.stack || "No stack trace"}

Component Stack: ${errorInfo?.componentStack || "No component stack"}
    `.trim();
  };

  public render() {
    if (this.state.hasError) {
      // If a custom fallback is provided, use it
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
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
              <Badge variant="destructive">Application Error</Badge>
            </div>
          </header>

          {/* Main Content */}
          <div className="flex-1 flex items-center justify-center px-4 py-8">
            <div className="max-w-2xl w-full">
              <Card className="text-center border-0 shadow-lg">
                <CardHeader className="pb-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-red-100 to-orange-200 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Bug className="w-10 h-10 text-red-600" />
                  </div>
                  <CardTitle className="text-3xl">
                    Something Went Wrong
                  </CardTitle>
                  <CardDescription className="text-lg">
                    An unexpected error occurred in the application. Our team
                    has been notified.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Error:</strong>{" "}
                      {this.state.error?.message || "An unknown error occurred"}
                    </AlertDescription>
                  </Alert>

                  <div className="flex flex-col sm:flex-row gap-3">
                    <Button
                      onClick={this.handleRetry}
                      className="bg-gradient-to-r from-green-600 to-blue-600 flex-1"
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Try Again
                    </Button>
                    <Button
                      onClick={this.handleReload}
                      variant="outline"
                      className="flex-1"
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Reload Page
                    </Button>
                    <Button asChild variant="outline" className="flex-1">
                      <Link to="/afl-dashboard">
                        <Home className="w-4 h-4 mr-2" />
                        Go Home
                      </Link>
                    </Button>
                  </div>

                  {/* Error Details Section */}
                  <div className="mt-6">
                    <Button
                      variant="ghost"
                      onClick={() =>
                        this.setState({ showDetails: !this.state.showDetails })
                      }
                      className="text-sm"
                    >
                      {this.state.showDetails ? "Hide" : "Show"} Technical
                      Details
                    </Button>

                    {this.state.showDetails && (
                      <div className="mt-4 p-4 bg-gray-50 rounded-lg border text-left">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">
                            Error Details
                          </h4>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={this.copyErrorDetails}
                          >
                            <Copy className="w-3 h-3 mr-1" />
                            Copy
                          </Button>
                        </div>
                        <pre className="text-xs text-gray-600 whitespace-pre-wrap overflow-auto max-h-60">
                          {this.getErrorDetails()}
                        </pre>
                      </div>
                    )}
                  </div>

                  {/* Help Section */}
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h4 className="font-medium text-blue-900 mb-2">
                      Need Help?
                    </h4>
                    <ul className="text-sm text-blue-700 space-y-1 text-left">
                      <li>
                        • Try refreshing the page or going back to the dashboard
                      </li>
                      <li>• Clear your browser cache and cookies</li>
                      <li>• Contact support if the error persists</li>
                      <li>
                        • Include the error details above when reporting the
                        issue
                      </li>
                    </ul>
                    <div className="mt-3 flex gap-2">
                      <Button size="sm" variant="outline" asChild>
                        <a
                          href="mailto:support@aflanalytics.com"
                          className="flex items-center"
                        >
                          <ExternalLink className="w-3 h-3 mr-1" />
                          Contact Support
                        </a>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

// Higher-order component for wrapping components with error boundary
export function withErrorBoundary<T extends object>(
  Component: React.ComponentType<T>,
  onError?: (error: Error, errorInfo: ErrorInfo) => void,
) {
  return function WrappedComponent(props: T) {
    return (
      <ErrorBoundary onError={onError}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}

// Hook for manual error reporting
export function useErrorHandler() {
  return (error: Error, context?: string) => {
    console.error("Manual error report:", { error, context });
    // In a real app, send to logging service
  };
}
