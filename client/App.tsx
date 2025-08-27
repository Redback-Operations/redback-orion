import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ErrorBoundary from "@/components/ErrorBoundary";
import Index from "./pages/Index";
import Login from "./pages/Login";
import AFLDashboard from "./pages/AFLDashboard";
import PlayerPerformance from "./pages/PlayerPerformance";
import CrowdMonitor from "./pages/CrowdMonitor";
import Analytics from "./pages/Analytics";
import Reports from "./pages/Reports";
import ApiDiagnostics from "./pages/ApiDiagnostics";
import ErrorDemo from "./pages/ErrorDemo";
import NotFound from "./pages/NotFound";

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
      cacheTime: 10 * 60 * 1000, // 10 minutes
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
            <Routes>
              <Route path="/" element={<Login />} />
              <Route path="/login" element={<Login />} />
              <Route path="/home" element={<AFLDashboard />} />
              <Route path="/afl-dashboard" element={<AFLDashboard />} />
              <Route path="/player-performance" element={<PlayerPerformance />} />
              <Route path="/crowd-monitor" element={<CrowdMonitor />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/video-analysis" element={<Analytics />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/api-diagnostics" element={<ApiDiagnostics />} />
              <Route path="/error-demo" element={<ErrorDemo />} />
              <Route path="/live-match" element={<AFLDashboard />} />
              <Route path="/stitch" element={<Index />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
