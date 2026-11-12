import { defineConfig, Plugin } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { createServer } from "./server";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,

    fs: {
      allow: [
        "./client",
        "./shared",
      ],

      deny: [
        ".env",
        ".env.*",
        "*.{crt,pem}",
        "**/.git/**",
        "server/**",
      ],
    },
  },

  build: {
    outDir: "dist/spa",

    rollupOptions: {
      input: {
        main: path.resolve(
          __dirname,
          "index.html"
        ),

        microsoftRedirect: path.resolve(
          __dirname,
          "redirect.html"
        ),
      },
    },
  },

  plugins: [
    react(),
    expressPlugin(),
  ],

  resolve: {
    alias: {
      "@": path.resolve(
        __dirname,
        "./client"
      ),

      "@shared": path.resolve(
        __dirname,
        "./shared"
      ),
    },
  },
}));

function expressPlugin(): Plugin {
  return {
    name: "express-plugin",

    // Only apply during development.
    apply: "serve",

    configureServer(server) {
      const app = createServer();

      // Add Express app as middleware
      // to the Vite development server.
      server.middlewares.use(app);
    },
  };
}