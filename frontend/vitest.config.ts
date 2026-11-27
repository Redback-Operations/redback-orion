import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react-swc";
import path from "node:path";
// Vitest configuration 
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./client"),
      "@shared": path.resolve(__dirname, "./shared"),
    },
  },
// simulates a browser environment for testing using jsdom, disables global variables and sets up test files
  test: {
    environment: "jsdom",
    globals: false,
    setupFiles: ["./client/tests/setup.ts"],
    include: [
      "client/**/*.{test,spec}.{ts,tsx}",
      "shared/**/*.{test,spec}.{ts,tsx}",
    ],
// enables automatic mocking of imported modules and restores mocks after each test
    clearMocks: true,
    restoreMocks: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
      include: [
        "client/**/*.{ts,tsx}",
        "shared/**/*.{ts,tsx}",
      ],
      exclude: [
        "**/*.test.*",
        "**/*.spec.*",
        "**/*.d.ts",
        "**/tests/**",
      ],
    },
  },
});