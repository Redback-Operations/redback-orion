import { lazy, Suspense } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ErrorBoundary from "@/components/ErrorBoundary";
import Login from "./pages/Login";
import PageSkeleton from "@/components/PageSkeleton";

const Index = lazy(() => import("./pages/Index"));
const AFLDashboard = lazy(() => import("./pages/AFLDashboard"));
const PlayerPerformance = lazy(() => import("./pages/PlayerPerformance"));
const CrowdMonitor = lazy(() => import("./pages/CrowdMonitor"));
const Analytics = lazy(() => import("./pages/Analytics"));
const Reports = lazy(() => import("./pages/Reports"));
const ApiDiagnostics = lazy(() => import("./pages/ApiDiagnostics"));
const ErrorDemo = lazy(() => import("./pages/ErrorDemo"));
const About = lazy(() => import("./pages/About"));
const NotFound = lazy(() => import("./pages/NotFound"));
const AddPlayer = lazy(() => import("./pages/AddPlayer"));

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
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Suspense fallback={<PageSkeleton />}>
              <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/login" element={<Login />} />
                <Route path="/home" element={<AFLDashboard />} />
                <Route path="/afl-dashboard" element={<AFLDashboard />} />
                <Route path="/player-performance" element={<PlayerPerformance />} />
                <Route path="/crowd-monitor" element={<CrowdMonitor />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/reports" element={<Reports />} />
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
