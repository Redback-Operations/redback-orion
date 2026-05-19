import "dotenv/config";
import express from "express";
import cors from "cors";
import { handleDemo } from "./routes/demo";
import {
  initiateGoogleAuth,
  handleGoogleCallback,
  initiateAppleAuth,
  handleAppleCallback,
  verifyToken,
} from "./routes/oauth";

export function createServer() {
  const app = express();

  // Middleware
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Example API routes
  app.get("/api/ping", (_req, res) => {
    const ping = process.env.PING_MESSAGE ?? "ping";
    res.json({ message: ping });
  });

  app.get("/api/demo", handleDemo);

  // OAuth routes
  app.get("/api/auth/google", initiateGoogleAuth);
  app.get("/api/auth/google/callback", handleGoogleCallback);
  app.get("/api/auth/apple", initiateAppleAuth);
  app.post("/api/auth/apple/callback", handleAppleCallback);
  app.post("/api/auth/verify-token", verifyToken);

  return app;
}
