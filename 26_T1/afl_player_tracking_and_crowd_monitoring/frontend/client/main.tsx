import "./global.css";

import { createRoot } from "react-dom/client";
import { MsalProvider } from "@azure/msal-react";

import App from "./App";
import { msalInstance } from "./lib/microsoftAuth";

// Ensure we only create the React root once
let root: ReturnType<typeof createRoot> | null = null;

function renderApp() {
  if (!root) {
    return;
  }

  root.render(
    <MsalProvider instance={msalInstance}>
      <App />
    </MsalProvider>
  );
}

async function initializeApp() {
  const container = document.getElementById("root");

  if (!container) {
    throw new Error("Could not find root element");
  }

  // MSAL must be initialized before Microsoft authentication is used
  await msalInstance.initialize();

  // Only create the React root once
  if (!root) {
    root = createRoot(container);
  }

  renderApp();
}

// Initialize the application
initializeApp().catch((error) => {
  console.error("Failed to initialize application:", error);
});

// Handle hot module replacement in development
if (import.meta.hot) {
  import.meta.hot.accept(["./App"], () => {
    renderApp();
  });
}