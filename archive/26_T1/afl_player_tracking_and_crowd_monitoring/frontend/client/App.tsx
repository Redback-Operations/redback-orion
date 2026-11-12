import { lazy, Suspense } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ErrorBoundary from "@/components/ErrorBoundary";
import Login from "./pages/Login";
import PageSkeleton from "@/components/PageSkeleton";
import { ThemePreferencesProvider } from "@/components/ThemePreferences";
import ProtectedRoute from "@/components/ProtectedRoute";

const Index = lazy(() => import("./pages/Index"));
const AFLDashboard = lazy(() => import("./pages/AFLDashboard"));
const PlayerPerformance = lazy(() => import("./pages/PlayerPerformance"));
const CrowdMonitor = lazy(() => import("./pages/CrowdMonitor"));
const Analytics = lazy(() => import("./pages/Analytics"));
const Reports = lazy(() => import("./pages/Reports"));
const ErrorDemo = lazy(() => import("./pages/ErrorDemo"));
const About = lazy(() => import("./pages/About"));
const NotFound = lazy(() => import("./pages/NotFound"));
const AddPlayer = lazy(() => import("./pages/AddPlayer"));
const Profile = lazy(() => import("./pages/Profile"));
const Settings = lazy(() => import("./pages/Settings"));

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

export default function App() {
  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        // In a real app, send this to your logging service
        console.error("Global error caught:", error, errorInfo);
      }}
    >
      <QueryClientProvider client={queryClient}>
        <ThemePreferencesProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Suspense fallback={<PageSkeleton />}>
              <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/login" element={<Login />} />
                <Route
                  path="/home"
                  element={
                    <ProtectedRoute>
                      <AFLDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/afl-dashboard"
                  element={
                    <ProtectedRoute>
                      <AFLDashboard />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/player-performance"
                  element={
                    <ProtectedRoute>
                      <PlayerPerformance />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/crowd-monitor"
                  element={
                    <ProtectedRoute>
                      <CrowdMonitor />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/analytics"
                  element={
                    <ProtectedRoute>
                      <Analytics />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/reports"
                  element={
                    <ProtectedRoute>
                      <Reports />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/about"
                  element={
                    <ProtectedRoute>
                      <About />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/error-demo"
                  element={
                    <ProtectedRoute>
                      <ErrorDemo />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/add-player"
                  element={
                    <ProtectedRoute>
                      <AddPlayer />
                    </ProtectedRoute>
                  }
                />
                <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <Settings />
                    </ProtectedRoute>
                  }
                />
                <Route path="/stitch" element={<Index />} />
                {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </BrowserRouter>
        </TooltipProvider>
        </ThemePreferencesProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
