import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Eye,
  EyeOff,
  User,
  Mail,
  Lock,
  Shield,
  ArrowRight,
  ArrowLeft,
  Users,
  MapPin,
  Trophy,
  Target,
  BarChart3,
  TrendingUp,
  Users as TeamIcon,
  Calendar,
  Plus,
  Volume2,
  Circle,
  Users as StaffIcon,
  Users as CrowdIcon,
  Download,
  Eye as ViewIcon,
  Activity,
  Clock,
  Target as GoalIcon,
  Star,
  MapPin as PinIcon,
} from "lucide-react";
import "./App.css";

import FatigueLivePanel from "./components/FatigueLivePanel.jsx";
import ScreenLoader from "./components/ScreenLoader.jsx";
import ScreenError from "./components/ScreenError.jsx";

// AFL Teams data with colors and emojis
const AFL_TEAMS = [
  {
    name: "Adelaide Crows",
    primary: "#002E5D",
    secondary: "#FFD100",
    emoji: "🦅",
    mascot: "Crow",
  },
  {
    name: "Brisbane Lions",
    primary: "#A30046",
    secondary: "#FFD100",
    emoji: "🦁",
    mascot: "Lion",
  },
  {
    name: "Carlton Blues",
    primary: "#041E42",
    secondary: "#FFFFFF",
    emoji: "🔵",
    mascot: "Blue",
  },
  {
    name: "Collingwood Magpies",
    primary: "#000000",
    secondary: "#FFFFFF",
    emoji: "🖤",
    mascot: "Magpie",
  },
  {
    name: "Essendon Bombers",
    primary: "#CC0000",
    secondary: "#000000",
    emoji: "✈️",
    mascot: "Bomber",
  },
  {
    name: "Fremantle Dockers",
    primary: "#4A90E2",
    secondary: "#FFFFFF",
    emoji: "⚓",
    mascot: "Docker",
  },
  {
    name: "Geelong Cats",
    primary: "#1E3A8A",
    secondary: "#FFFFFF",
    emoji: "🐱",
    mascot: "Cat",
  },
  {
    name: "Gold Coast Suns",
    primary: "#FF6B35",
    secondary: "#FFD100",
    emoji: "☀️",
    mascot: "Sun",
  },
  {
    name: "GWS Giants",
    primary: "#FF6B35",
    secondary: "#000000",
    emoji: "👹",
    mascot: "Giant",
  },
  {
    name: "Hawthorn Hawks",
    primary: "#8B4513",
    secondary: "#FFD100",
    emoji: "🦅",
    mascot: "Hawk",
  },
  {
    name: "Melbourne Demons",
    primary: "#000080",
    secondary: "#FF0000",
    emoji: "😈",
    mascot: "Demon",
  },
  {
    name: "North Melbourne Kangaroos",
    primary: "#000080",
    secondary: "#FFFFFF",
    emoji: "🦘",
    mascot: "Kangaroo",
  },
  {
    name: "Port Adelaide Power",
    primary: "#000000",
    secondary: "#00A0DC",
    emoji: "⚡",
    mascot: "Power",
  },
  {
    name: "Richmond Tigers",
    primary: "#FFD100",
    secondary: "#000000",
    emoji: "🐯",
    mascot: "Tiger",
  },
  {
    name: "St Kilda Saints",
    primary: "#000000",
    secondary: "#FF0000",
    emoji: "⛪",
    mascot: "Saint",
  },
  {
    name: "Sydney Swans",
    primary: "#FF0000",
    secondary: "#FFFFFF",
    emoji: "🦢",
    mascot: "Swan",
  },
  {
    name: "West Coast Eagles",
    primary: "#002E5D",
    secondary: "#FFD100",
    emoji: "🦅",
    mascot: "Eagle",
  },
  {
    name: "Western Bulldogs",
    primary: "#FF6B35",
    secondary: "#FFFFFF",
    emoji: "🐕",
    mascot: "Bulldog",
  },
];

// Player Positions
const PLAYER_POSITIONS = [
  "Forward",
  "Midfielder",
  "Defender",
  "Ruck",
  "Interchange",
];

// Mock Dashboard Data
const DASHBOARD_DATA = {
  productiveTime: 12.4,
  focusedTime: 8.5,
  teams: [
    {
      name: "Forward Line",
      utilization: 85,
      overUtilized: 15,
      underUtilized: 0,
    },
    { name: "Midfield", utilization: 92, overUtilized: 8, underUtilized: 0 },
    { name: "Defense", utilization: 78, overUtilized: 0, underUtilized: 22 },
    {
      name: "Ruck Division",
      utilization: 88,
      overUtilized: 12,
      underUtilized: 0,
    },
    {
      name: "Interchange",
      utilization: 65,
      overUtilized: 0,
      underUtilized: 35,
    },
  ],
  players: [
    {
      name: "Marcus Bontempelli",
      team: "Western Bulldogs",
      position: "Midfielder",
      image: "🏉",
    },
    {
      name: "Dustin Martin",
      team: "Richmond Tigers",
      position: "Midfielder",
      image: "🏉",
    },
    {
      name: "Patrick Dangerfield",
      team: "Geelong Cats",
      position: "Midfielder",
      image: "🏉",
    },
  ],
};

function App() {
  // Dashboard State
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentView, setCurrentView] = useState("login");

  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedPosition, setSelectedPosition] = useState("");
  const [showTeamSelector, setShowTeamSelector] = useState(false);
  const [showPositionSelector, setShowPositionSelector] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [devError, setDevError] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    name: "",
    team: "",
    position: "",
    favoriteGround: "",
  });

  // DEV: To skip login from the URL while testing
  useEffect(() => {
    const sp = new URLSearchParams(window.location.search);

    // skip login
    if (sp.get("view") === "dashboard" || sp.get("dev") === "1") {
      setCurrentView("dashboard");
    }

    // gates
    const gate = sp.get("gate");
    if (gate === "loading") setIsLoading(true);
    if (gate === "error") setDevError(true);
  }, []);

  // Dashboard States
  const [showReferee, setShowReferee] = useState(true);
  const [showBall, setShowBall] = useState(true);
  const [showStaff, setShowStaff] = useState(false);
  const [showCrowd, setShowCrowd] = useState(true);
  const [activeTab, setActiveTab] = useState("player-tracking");

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate authentication process
    await new Promise((resolve) => setTimeout(resolve, 2000));

    console.log("Form submitted:", formData);
    setIsLoading(false);

    // Switch to dashboard view
    setCurrentView("dashboard");
  };

  const toggleForm = () => {
    setIsLogin(!isLogin);
    setFormData({
      email: "",
      password: "",
      confirmPassword: "",
      name: "",
      team: "",
      position: "",
      favoriteGround: "",
    });
    setSelectedTeam(null);
    setSelectedPosition("");
  };

  const selectTeam = (team) => {
    setSelectedTeam(team);
    setFormData({ ...formData, team: team.name });
    setShowTeamSelector(false);
  };

  const selectPosition = (position) => {
    setSelectedPosition(position);
    setFormData({ ...formData, position });
    setShowPositionSelector(false);
  };

  /* ------------------- Generic section loader/error wiring ------------------- */
  const SectionGate = ({ loading, error, onRetry, label, children }) => {
    if (loading) return <ScreenLoader label={label} />;
    if (error)
      return (
        <ScreenError title="Failed to load" message={error} onRetry={onRetry} />
      );
    return <>{children}</>;
  };

  // per-section loading/error state ( later hook these to real APIs)
  const [metricsLoading, setMetricsLoading] = useState(false);
  const [metricsError, setMetricsError] = useState("");

  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState("");

  const [trackingLoading, setTrackingLoading] = useState(false);
  const [trackingError, setTrackingError] = useState("");

  const [actionsLoading, setActionsLoading] = useState(false);
  const [actionsError, setActionsError] = useState("");

  const [mapLoading, setMapLoading] = useState(false);
  const [mapError, setMapError] = useState("");

  // demo "fetch" functions (replace later with real calls)
  const refetchMetrics = () => {
    setMetricsError("");
    setMetricsLoading(true);
    setTimeout(() => {
      setMetricsLoading(false);
      // setMetricsError("Timeout from API"); // uncomment to test error
    }, 600);
  };

  const refetchAnalytics = () => {
    setAnalyticsError("");
    setAnalyticsLoading(true);
    setTimeout(() => {
      setAnalyticsLoading(false);
    }, 700);
  };

  const refetchTracking = () => {
    setTrackingError("");
    setTrackingLoading(true);
    setTimeout(() => {
      setTrackingLoading(false);
    }, 500);
  };

  const refetchActions = () => {
    setActionsError("");
    setActionsLoading(true);
    setTimeout(() => {
      setActionsLoading(false);
    }, 550);
  };

  const refetchMap = () => {
    setMapError("");
    setMapLoading(true);
    setTimeout(() => {
      setMapLoading(false);
    }, 500);
  };

  // fire once when dashboard mounts
  useEffect(() => {
    if (currentView === "dashboard") {
      refetchMetrics();
      refetchAnalytics();
      refetchTracking();
      refetchActions();
      refetchMap();
    }
  }, [currentView]);
  /* ------------------------------------------------------------------------------- */

  // Dashboard Component
  const Dashboard = () =>
    isLoading ? (
      <ScreenLoader label="Loading dashboard…" />
    ) : devError ? (
      <ScreenError
        title="Analytics failed"
        message="Timeout from API"
        onRetry={() => window.location.reload()}
      />
    ) : (
      <div className="dashboard-container">
        {/* Left Sidebar */}
        <div className="dashboard-sidebar">
          <div className="sidebar-header">
            <div className="logo-section">
              <div className="afl-logo">
                <div className="logo-icon">🏉</div>
                <h1>AFL Tracker</h1>
              </div>
            </div>
          </div>

          <div className="sidebar-controls">
            <h3>Display Controls</h3>
            <div className="control-item">
              <button
                className={`control-btn ${showReferee ? "active" : ""}`}
                onClick={() => setShowReferee(!showReferee)}
              >
                <Volume2 size={20} />
                <span>Show Referee</span>
              </button>
            </div>
            <div className="control-item">
              <button
                className={`control-btn ${showBall ? "active" : ""}`}
                onClick={() => setShowBall(!showBall)}
              >
                <Circle size={20} />
                <span>Show Ball</span>
              </button>
            </div>
            <div className="control-item">
              <button
                className={`control-btn ${showStaff ? "active" : ""}`}
                onClick={() => setShowStaff(!showStaff)}
              >
                <StaffIcon size={20} />
                <span>Show Staff</span>
              </button>
            </div>
            <div className="control-item">
              <button
                className={`control-btn ${showCrowd ? "active" : ""}`}
                onClick={() => setShowCrowd(!showCrowd)}
              >
                <CrowdIcon size={20} />
                <span>Show Crowd</span>
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="dashboard-main">
          {/* Current Match Overview */}
          <div className="match-overview">
            <h2>Current Match: Team A vs Team B</h2>
            <div className="match-stats">
              <span>Score: 2-1</span>
              <span>Time: 12:34</span>
              <span>Quarter: 3</span>
            </div>
            <div className="match-tabs">
              <button
                className={`tab-btn ${
                  activeTab === "player-tracking" ? "active" : ""
                }`}
                onClick={() => setActiveTab("player-tracking")}
              >
                Player Tracking
              </button>
              <button
                className={`tab-btn ${
                  activeTab === "crowd-heatmap" ? "active" : ""
                }`}
                onClick={() => setActiveTab("crowd-heatmap")}
              >
                Crowd Heatmap
              </button>
              <button
                className={`tab-btn ${
                  activeTab === "analytics" ? "active" : ""
                }`}
                onClick={() => setActiveTab("analytics")}
              >
                Analytics
              </button>
            </div>
          </div>

          {/* Player Performance Metrics */}
          <div className="metrics-section">
            <div className="section-header">
              <h3>Player Performance Metrics</h3>
              <p>Real-time tracking of key player stats.</p>
              <button className="action-btn">
                <ViewIcon size={16} />
                View Detailed Stats
              </button>
            </div>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-icon">⚽</div>
                <div className="metric-content">
                  <h4>Goals</h4>
                  <div className="metric-value">2</div>
                  <div className="metric-change positive">+1</div>
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-icon">🤝</div>
                <div className="metric-content">
                  <h4>Assists</h4>
                  <div className="metric-value">1</div>
                  <div className="metric-change">0</div>
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-icon">🎯</div>
                <div className="metric-content">
                  <h4>Shots on Target</h4>
                  <div className="metric-value">5</div>
                  <div className="metric-change positive">+2</div>
                </div>
              </div>
            </div>
          </div>

          {/* Player Fatigue (Live) panel */}
          <FatigueLivePanel />

          {/* Match Progression Analytics */}
          <div className="analytics-section">
            <div className="section-header">
              <h3>Match Progression Analytics</h3>
              <p>Analysis of match changes over time.</p>
              <button className="action-btn">
                <Download size={16} />
                Download Report
              </button>
            </div>
            <div className="charts-grid">
              <div className="chart-card">
                <h4>Possession Over Time</h4>
                <div className="chart-container">
                  <div className="chart-placeholder">
                    <div className="chart-line"></div>
                    <div className="chart-line"></div>
                    <div className="chart-line"></div>
                  </div>
                  <div className="chart-labels">
                    <span>Possession %</span>
                    <span>Time</span>
                  </div>
                </div>
              </div>
              <div className="chart-card">
                <h4>Player Activity</h4>
                <div className="chart-container">
                  <div className="bar-chart">
                    <div className="bar" style={{ height: "60%" }}></div>
                    <div className="bar" style={{ height: "80%" }}></div>
                    <div className="bar" style={{ height: "40%" }}></div>
                    <div className="bar" style={{ height: "90%" }}></div>
                    <div className="bar" style={{ height: "70%" }}></div>
                  </div>
                  <div className="chart-labels">
                    <span>Actions</span>
                    <span>Player</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Live Player Tracking */}
          <div className="tracking-section">
            <div className="section-header">
              <h3>Live Player Tracking</h3>
              <p>Visual representation of player movements.</p>
              <button className="action-btn">
                <ViewIcon size={16} />
                Show Heatmap
              </button>
            </div>
            <div className="tracking-content">
              <div className="player-info-cards">
                <div className="player-card">
                  <h4>Player A</h4>
                  <p>Position: Midfield</p>
                  <p>Confidence: 95%</p>
                </div>
                <div className="player-card">
                  <h4>Player B</h4>
                  <p>Position: Forward</p>
                  <p>Confidence: 90%</p>
                </div>
              </div>
            </div>
          </div>

          {/* Current Actions */}
          <div className="actions-section">
            <div className="section-header">
              <h3>Current Actions</h3>
              <p>List of actions occurring in the match.</p>
            </div>
            <div className="actions-list">
              <div className="action-item">
                <div className="action-icon goal">⚽</div>
                <div className="action-content">
                  <h4>Goal by Team A</h4>
                  <p>Player A, 12:03</p>
                </div>
              </div>
              <div className="action-item">
                <div className="action-icon card">🟨</div>
                <div className="action-content">
                  <h4>Yellow Card</h4>
                  <p>Player B, 11:45</p>
                </div>
              </div>
            </div>
          </div>

          {/* Interactive Map */}
          <div className="map-section">
            <div className="interactive-map">
              <div className="map-placeholder">
                <PinIcon size={24} />
                <p>Interactive map showing player positions and movements.</p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="dashboard-footer">
            <a href="#">Follow Us on Social Media</a>
            <a href="#">Contact Support</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
          </div>
        </div>
      </div>
    );

  // Authentication Component
  const Authentication = () => (
    <div className="app-container">
      {/* Left Panel - Authentication Form with Image */}
      <div className="left-panel">
        {/* Image Section */}
        <div className="image-section">
          <div className="image-container">
            {/* Replace this with your actual image */}
            <div className="placeholder-image">
              <div className="image-overlay">
                <div className="image-content">
                  <div className="image-logo">🏉</div>
                  <h2>AFL Player Tracking</h2>
                  <p>Professional analytics for elite performance</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Form Section */}
        <div className="form-section">
          <div className="auth-container">
            {/* Logo */}
            <div className="logo-section">
              <div className="afl-logo">
                <div className="logo-icon">🏉</div>
                <h1>AFL Tracker</h1>
              </div>
            </div>

            {/* Form Header */}
            <div className="form-header">
              <h2>Get Started Now</h2>
              <p>Track your AFL players with precision and analytics</p>
            </div>

            {/* Social Login Buttons */}
            <div className="social-login">
              <button className="social-btn google">
                <div className="social-icon">G</div>
                Log in with Google
              </button>
              <button className="social-btn apple">
                <div className="social-icon">🍎</div>
                Log in with Apple
              </button>
            </div>

            {/* Divider */}
            <div className="divider">
              <span>or</span>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="auth-form">
              {!isLogin && (
                <div className="input-group">
                  <label>Name</label>
                  <input
                    type="text"
                    name="name"
                    placeholder="Enter your full name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required={!isLogin}
                  />
                </div>
              )}

              <div className="input-group">
                <label>Email address</label>
                <input
                  type="email"
                  name="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>

              {!isLogin && (
                <div className="input-group">
                  <label>Team</label>
                  <div className="select-wrapper">
                    <button
                      type="button"
                      className="select-btn"
                      onClick={() => setShowTeamSelector(!showTeamSelector)}
                    >
                      {selectedTeam
                        ? `${selectedTeam.emoji} ${selectedTeam.name}`
                        : "Select your team"}
                    </button>

                    {showTeamSelector && (
                      <div className="dropdown">
                        {AFL_TEAMS.map((team) => (
                          <button
                            key={team.name}
                            type="button"
                            className="dropdown-item"
                            onClick={() => selectTeam(team)}
                          >
                            <span className="team-emoji">{team.emoji}</span>
                            {team.name}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="input-group">
                <label>Password</label>
                <div className="password-input">
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    placeholder="min 8 chars"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff /> : <Eye />}
                  </button>
                </div>
              </div>

              {!isLogin && (
                <div className="input-group">
                  <label>Confirm Password</label>
                  <div className="password-input">
                    <input
                      type={showConfirmPassword ? "text" : "password"}
                      name="confirmPassword"
                      placeholder="Confirm your password"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      required={!isLogin}
                    />
                    <button
                      type="button"
                      className="password-toggle"
                      onClick={() =>
                        setShowConfirmPassword(!showConfirmPassword)
                      }
                    >
                      {showConfirmPassword ? <EyeOff /> : <Eye />}
                    </button>
                  </div>
                </div>
              )}

              {isLogin && (
                <div className="forgot-password">
                  <a href="#">Forgot password?</a>
                </div>
              )}

              {!isLogin && (
                <div className="checkbox-group">
                  <label className="checkbox">
                    <input type="checkbox" required />
                    <span className="checkmark"></span>I agree to the{" "}
                    <a href="#">Terms & Privacy</a>
                  </label>
                </div>
              )}

              <button type="submit" className="submit-btn" disabled={isLoading}>
                {isLoading ? (
                  <div className="loading-spinner"></div>
                ) : isLogin ? (
                  "Login"
                ) : (
                  "Sign Up"
                )}
              </button>
            </form>

            {/* Form Toggle */}
            <div className="form-toggle">
              <p>
                {isLogin
                  ? "Don't have an account?"
                  : "Already have an account?"}
                <button onClick={toggleForm} className="toggle-link">
                  {isLogin ? "Sign up" : "Sign in"}
                </button>
              </p>
            </div>

            {/* Footer */}
            <div className="footer">
              <p>© 2025 AFL Tracker, All rights reserved.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Dashboard Preview */}
      <div className="right-panel">
        <div className="dashboard-preview">
          <div className="preview-header">
            <h2>The simplest way to track your AFL players</h2>
            <p>
              Advanced analytics and real-time monitoring for professional teams
            </p>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-header">
              <h3>Dashboard</h3>
              <div className="dashboard-controls">
                <select className="team-select">
                  <option>All Teams</option>
                  {AFL_TEAMS.map((team) => (
                    <option key={team.name}>{team.name}</option>
                  ))}
                </select>
                <div className="date-range">
                  <Calendar size={16} />
                  <span>Dec 21 2024 - Jan 03 2025</span>
                </div>
              </div>
            </div>

            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-header">
                  <h4>Player Performance</h4>
                  <TrendingUp size={20} />
                </div>
                <div className="metric-value">
                  {DASHBOARD_DATA.productiveTime} hr
                </div>
                <div className="metric-change positive">+12.5%</div>
                <div className="metric-chart">
                  <div className="chart-line"></div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <h4>Match Time</h4>
                  <BarChart3 size={20} />
                </div>
                <div className="metric-value">
                  {DASHBOARD_DATA.focusedTime} hr
                </div>
                <div className="metric-change positive">+8.2%</div>
                <div className="metric-chart">
                  <div className="chart-line"></div>
                </div>
              </div>
            </div>

            <div className="team-utilization">
              <h4>Team's Performance</h4>
              <div className="utilization-table">
                {DASHBOARD_DATA.teams.map((team, index) => (
                  <div key={index} className="utilization-row">
                    <div className="team-name">{team.name}</div>
                    <div className="utilization-bars">
                      <div
                        className="bar overall"
                        style={{ width: `${team.utilization}%` }}
                      ></div>
                      <div
                        className="bar over"
                        style={{ width: `${team.overUtilized}%` }}
                      ></div>
                      <div
                        className="bar under"
                        style={{ width: `${team.underUtilized}%` }}
                      ></div>
                    </div>
                    <div className="utilization-stats">
                      <span className="overall">{team.utilization}%</span>
                      <span className="over">{team.overUtilized}%</span>
                      <span className="under">{team.underUtilized}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Add Player Card */}
            <div className="add-player-card">
              <div className="card-header">
                <h4>Add Player</h4>
                <Plus size={20} />
              </div>
              <div className="player-input">
                <input type="email" placeholder="Enter player email" />
                <button className="add-btn">Add</button>
              </div>
              <div className="existing-players">
                {DASHBOARD_DATA.players.map((player, index) => (
                  <div key={index} className="player-item">
                    <div className="player-avatar">{player.image}</div>
                    <div className="player-info">
                      <div className="player-name">{player.name}</div>
                      <div className="player-details">
                        {player.team} • {player.position}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <button className="copy-link-btn">Copy link</button>
            </div>
          </div>

          {/* Partner Logos */}
          <div className="partner-logos">
            <div className="logo">🏉 AFL</div>
            <div className="logo">🏟️ MCG</div>
            <div className="logo">🏆 Premiership</div>
            <div className="logo">📊 Stats</div>
            <div className="logo">🎯 Analytics</div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app">
      {currentView === "dashboard" ? <Dashboard /> : <Authentication />}
    </div>
  );
}

export default App;
