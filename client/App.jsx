import "./global.css";

import { Toaster } from "@/components/ui/toaster";
import { createRoot } from "react-dom/client";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Login from "./pages/Login.jsx";
import AFLDashboard from "./pages/AFLDashboard.jsx";
import PlayerPerformance from "./pages/PlayerPerformance.jsx";
import CrowdMonitor from "./pages/CrowdMonitor.jsx";
import Analytics from "./pages/Analytics.jsx";
import ApiDiagnostics from "./pages/ApiDiagnostics.jsx";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
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
          <Route path="/reports" element={<Analytics />} />
          <Route path="/api-diagnostics" element={<ApiDiagnostics />} />
          <Route path="/live-match" element={<AFLDashboard />} />
          <Route path="/stitch" element={<Index />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

createRoot(document.getElementById("root")).render(<App />);
