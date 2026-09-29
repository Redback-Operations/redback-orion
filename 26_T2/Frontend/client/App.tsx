import { lazy, Suspense } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ErrorBoundary from "@/components/ErrorBoundary";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { getRole } from "@/lib/auth";
import Index from "./pages/Index";
import Login from "./pages/Login";
import ResetPassword from "./pages/ResetPassword";
import AFLDashboard from "./pages/AFLDashboard";
import PlayerPerformance from "./pages/PlayerPerformance";
import CrowdMonitor from "./pages/CrowdMonitor";
import Analytics from "./pages/Analytics";
import Reports from "./pages/Reports";
import ApiDiagnostics from "./pages/ApiDiagnostics";
import ErrorDemo from "./pages/ErrorDemo";
import About from "./pages/About";
import NotFound from "./pages/NotFound";
import AddPlayer from "./pages/AddPlayer";
import Admin from "./pages/Admin";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        try {
          // Don't retry on 4xx errors
          if (error && typeof error === "object" && "status" in error) {
            const status = (error as any).status;
            if (status >= 400 && status < 500) {
              return false;
            }
          }
          return failureCount < 3;
        } catch (retryError) {
          console.error("Error in retry logic:", retryError);
          return false;
        }
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false, // Prevent unnecessary refetches that could cause errors
    },
    mutations: {
      retry: (failureCount, error) => {
        try {
          // Don't retry mutations on client errors
          if (error && typeof error === "object" && "status" in error) {
            const status = (error as any).status;
            if (status >= 400 && status < 500) {
              return false;
            }
          }
          return failureCount < 2; // Fewer retries for mutations
        } catch (retryError) {
          console.error("Error in mutation retry logic:", retryError);
          return false;
        }
      },
    },
  },
});

// Sends a logged-in user to the dashboard, everyone else to /login
function RootRedirect() {
  const role = getRole();
  return role ? (
    <Navigate to="/afl-dashboard" replace />
  ) : (
    <Navigate to="/login" replace />
  );
}

export default function App() {
  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        // In a real app, send this to your logging service
        console.error("Global error caught:", error, errorInfo);
      }}
    >
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
                        <Suspense
              fallback={
                <div className="flex min-h-screen items-center justify-center">
                  <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-green-600" />
                </div>
              }
            >
              <Routes>
              <Route path="/" element={<RootRedirect />} />
                <Route path="/login" element={<Login />} />
              <Route path="/reset-password" element={<ResetPassword />} />

              <Route
                path="/home"
                element={
                  <ProtectedRoute allowedRoles={["user", "admin", "player", "coach"]}>
                    <AFLDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/afl-dashboard"
                element={
                  <ProtectedRoute allowedRoles={["user", "admin", "player", "coach"]}>
                    <AFLDashboard />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/player-performance"
                element={
                  <ProtectedRoute allowedRoles={["user", "admin", "player", "coach"]}>
                    <PlayerPerformance />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/crowd-monitor"
                element={
                  <ProtectedRoute allowedRoles={["user", "admin","coach"]}>
                    <CrowdMonitor />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/analytics"
                element={
                  <ProtectedRoute allowedRoles={["user", "admin","coach"]}>
                    <Analytics />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/reports"
                element={
                  <ProtectedRoute allowedRoles={["user", "admin", "player", "coach"]}>
                    <Reports />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/add-player"
                element={
                  <ProtectedRoute allowedRoles={["admin","coach"]}>
                    <AddPlayer />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/admin"
                element={
                  <ProtectedRoute allowedRoles={["admin"]}>
                    <Admin />
                  </ProtectedRoute>
                }
              />

                <Route path="/api-diagnostics" element={<ApiDiagnostics />} />
                <Route path="/about" element={<About />} />
                <Route path="/error-demo" element={<ErrorDemo />} />
                <Route path="/add-player" element={<AddPlayer />} />
                <Route path="/stitch" element={<Index />} />
                {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </BrowserRouter>
        </TooltipProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
