import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createHashRouter, RouterProvider } from "react-router-dom";

// 
function Root({ children }) {
  return (
    <div style={{ maxWidth: 980, margin: "24px auto", padding: 16, fontFamily: "Inter, system-ui, Arial, sans-serif" }}>
      <h2>Player Dashboard — UI States & Fatigue (Demo)</h2>
      <nav style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
        <a href="#/fatigue">Fatigue</a>
        <a href="#/realtimeF">RealtimeF</a>
        <a href="#/realtimeF2">RealtimeF (multi)</a>
        <a href="#/loading">Loading</a>
        <a href="#/empty">Empty</a>
        <a href="#/error">Error</a>
        <a href="/">Team Dashboard</a> {/* back to team app */}
      </nav>
      {children}
    </div>
  );
}

// pages
import RealtimeFCarouselPage from "./pages/RealtimeFCarouselPage.jsx";
import FatiguePage from "./pages/FatiguePage.jsx";
import RealtimeFPage from "./pages/RealtimeFPage.jsx";
import LoadingPage from "./pages/LoadingPage.jsx";
import EmptyPage from "./pages/EmptyPage.jsx";
import ErrorPage from "./pages/ErrorPage.jsx";

const withRoot = (el) => <Root>{el}</Root>;

const router = createHashRouter([
  { index: true, element: withRoot(<FatiguePage />) },
  { path: "/fatigue", element: withRoot(<FatiguePage />) },
  { path: "/realtimeF", element: withRoot(<RealtimeFPage />) },
  { path: "/realtimeF2", element: withRoot(<RealtimeFCarouselPage />) },
  { path: "/loading", element: withRoot(<LoadingPage />) },
  { path: "/empty", element: withRoot(<EmptyPage />) },
  { path: "/error", element: withRoot(<ErrorPage />) },
  { path: "*", element: withRoot(<div>Not Found</div>) },
]);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
