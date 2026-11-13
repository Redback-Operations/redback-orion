import "./global.css";
import { createRoot } from "react-dom/client";
import App from "./App";

// Ensure we only create the root once
let root: ReturnType<typeof createRoot> | null = null;

function initializeApp() {
  const container = document.getElementById("root");

  if (!container) {
    throw new Error("Could not find root element");
  }

  // Only create root if it doesn't exist
  if (!root) {
    root = createRoot(container);
  }

  root.render(<App />);
}

// Initialize the app
initializeApp();

// Handle hot module replacement in development
if (import.meta.hot) {
  import.meta.hot.accept(["./App"], () => {
    // Re-render the app when modules are updated
    if (root) {
      root.render(<App />);
    }
  });
}
