import { RequestHandler } from "express";
import { OAuth2Client } from "google-auth-library";
import jwt from "jsonwebtoken";
import { OAuthUser, OAuthResponse } from "@shared/oauth";

// OAuth configuration from environment variables
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
const APPLE_CLIENT_ID = process.env.APPLE_CLIENT_ID;
const JWT_SECRET = process.env.JWT_SECRET || "your-jwt-secret-key";
const CLIENT_URL = process.env.CLIENT_URL || "http://localhost:8080";

// Initialize Google OAuth client
const googleOAuth2Client = new OAuth2Client(
  GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET,
  `${CLIENT_URL}/api/auth/google/callback`,
);

// Google OAuth initiation
export const initiateGoogleAuth: RequestHandler = (req, res) => {
  try {
    const authUrl = googleOAuth2Client.generateAuthUrl({
      access_type: "offline",
      scope: [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
      ],
      prompt: "consent",
    });

    res.redirect(authUrl);
  } catch (error) {
    console.error("Google OAuth initiation error:", error);
    res.status(500).json({ success: false, error: "OAuth initiation failed" });
  }
};

// Google OAuth callback
export const handleGoogleCallback: RequestHandler = async (req, res) => {
  try {
    const { code } = req.query;

    if (!code || typeof code !== "string") {
      return res
        .status(400)
        .json({ success: false, error: "No authorization code received" });
    }

    // Exchange code for tokens
    const { tokens } = await googleOAuth2Client.getToken(code);
    googleOAuth2Client.setCredentials(tokens);

    // Get user info
    const userInfoResponse = await fetch(
      "https://www.googleapis.com/oauth2/v2/userinfo",
      {
        headers: {
          Authorization: `Bearer ${tokens.access_token}`,
        },
      },
    );

    const userInfo = await userInfoResponse.json();

    const user: OAuthUser = {
      id: userInfo.id,
      email: userInfo.email,
      name: userInfo.name,
      picture: userInfo.picture,
      provider: "google",
    };

    // Generate JWT token
    const accessToken = jwt.sign(
      {
        userId: user.id,
        email: user.email,
        provider: user.provider,
      },
      JWT_SECRET,
      { expiresIn: "24h" },
    );

    // Redirect to frontend with user data
    const redirectUrl = `${CLIENT_URL}/?auth=success&token=${accessToken}&user=${encodeURIComponent(JSON.stringify(user))}`;
    res.redirect(redirectUrl);
  } catch (error) {
    console.error("Google OAuth callback error:", error);
    const redirectUrl = `${CLIENT_URL}/?auth=error&message=${encodeURIComponent("Google authentication failed")}`;
    res.redirect(redirectUrl);
  }
};

// Apple OAuth initiation
export const initiateAppleAuth: RequestHandler = (req, res) => {
  try {
    if (!APPLE_CLIENT_ID) {
      return res
        .status(500)
        .json({ success: false, error: "Apple OAuth not configured" });
    }

    const params = new URLSearchParams({
      response_type: "code",
      response_mode: "form_post",
      client_id: APPLE_CLIENT_ID,
      redirect_uri: `${CLIENT_URL}/api/auth/apple/callback`,
      scope: "name email",
    });

    const authUrl = `https://appleid.apple.com/auth/authorize?${params.toString()}`;
    res.redirect(authUrl);
  } catch (error) {
    console.error("Apple OAuth initiation error:", error);
    res
      .status(500)
      .json({ success: false, error: "Apple OAuth initiation failed" });
  }
};

// Apple OAuth callback
export const handleAppleCallback: RequestHandler = async (req, res) => {
  try {
    const { code, user } = req.body;

    if (!code) {
      return res
        .status(400)
        .json({ success: false, error: "No authorization code received" });
    }

    // Parse user data from Apple (only available on first authorization)
    let userData = null;
    if (user) {
      const parsedUser = typeof user === "string" ? JSON.parse(user) : user;
      userData = {
        firstName: parsedUser.name?.firstName || "",
        lastName: parsedUser.name?.lastName || "",
        email: parsedUser.email || "",
      };
    }

    // For now, create a basic user object
    // In production, you'd validate the code with Apple's servers
    const oauthUser: OAuthUser = {
      id: `apple_${Date.now()}`, // In production, get this from Apple's response
      email: userData?.email || "apple.user@example.com",
      name: userData
        ? `${userData.firstName} ${userData.lastName}`.trim()
        : "Apple User",
      provider: "apple",
    };

    // Generate JWT token
    const accessToken = jwt.sign(
      {
        userId: oauthUser.id,
        email: oauthUser.email,
        provider: oauthUser.provider,
      },
      JWT_SECRET,
      { expiresIn: "24h" },
    );

    // Redirect to frontend with user data
    const redirectUrl = `${CLIENT_URL}/?auth=success&token=${accessToken}&user=${encodeURIComponent(JSON.stringify(oauthUser))}`;
    res.redirect(redirectUrl);
  } catch (error) {
    console.error("Apple OAuth callback error:", error);
    const redirectUrl = `${CLIENT_URL}/?auth=error&message=${encodeURIComponent("Apple authentication failed")}`;
    res.redirect(redirectUrl);
  }
};

// Verify JWT token
export const verifyToken: RequestHandler = (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res
        .status(400)
        .json({ success: false, error: "No token provided" });
    }

    const decoded = jwt.verify(token, JWT_SECRET);
    res.json({ success: true, user: decoded });
  } catch (error) {
    console.error("Token verification error:", error);
    res.status(401).json({ success: false, error: "Invalid token" });
  }
};
