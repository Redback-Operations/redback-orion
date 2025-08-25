import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye, EyeOff, User, Mail, Lock, Shield, ArrowRight, ArrowLeft, Users, MapPin, Trophy, Target, BarChart3, TrendingUp, Calendar, Plus, Volume2, Circle, Download, Activity, Clock, Star, Search, BarChart, LineChart } from 'lucide-react'
import './App.css'

// AFL Teams data with colors and emojis
const AFL_TEAMS = [
  { name: 'Adelaide Crows', primary: '#002E5D', secondary: '#FFD100', emoji: '🦅', mascot: 'Crow' },
  { name: 'Brisbane Lions', primary: '#A30046', secondary: '#FFD100', emoji: '🦁', mascot: 'Lion' },
  { name: 'Carlton Blues', primary: '#041E42', secondary: '#FFFFFF', emoji: '🔵', mascot: 'Blue' },
  { name: 'Collingwood Magpies', primary: '#000000', secondary: '#FFFFFF', emoji: '🖤', mascot: 'Magpie' },
  { name: 'Essendon Bombers', primary: '#CC0000', secondary: '#000000', emoji: '✈️', mascot: 'Bomber' },
  { name: 'Fremantle Dockers', primary: '#4A90E2', secondary: '#FFFFFF', emoji: '⚓', mascot: 'Docker' },
  { name: 'Geelong Cats', primary: '#1E3A8A', secondary: '#FFFFFF', emoji: '🐱', mascot: 'Cat' },
  { name: 'Gold Coast Suns', primary: '#FF6B35', secondary: '#FFD100', emoji: '☀️', mascot: 'Sun' },
  { name: 'GWS Giants', primary: '#FF6B35', secondary: '#000000', emoji: '👹', mascot: 'Giant' },
  { name: 'Hawthorn Hawks', primary: '#8B4513', secondary: '#FFD100', emoji: '🦅', mascot: 'Hawk' },
  { name: 'Melbourne Demons', primary: '#000080', secondary: '#FF0000', emoji: '😈', mascot: 'Demon' },
  { name: 'North Melbourne Kangaroos', primary: '#000080', secondary: '#FFFFFF', emoji: '🦘', mascot: 'Kangaroo' },
  { name: 'Port Adelaide Power', primary: '#000000', secondary: '#00A0DC', emoji: '⚡', mascot: 'Power' },
  { name: 'Richmond Tigers', primary: '#FFD100', secondary: '#000000', emoji: '🐯', mascot: 'Tiger' },
  { name: 'St Kilda Saints', primary: '#000000', secondary: '#FF0000', emoji: '⛪', mascot: 'Saint' },
  { name: 'Sydney Swans', primary: '#FF0000', secondary: '#FFFFFF', emoji: '🦢', mascot: 'Swan' },
  { name: 'West Coast Eagles', primary: '#002E5D', secondary: '#FFD100', emoji: '🦅', mascot: 'Eagle' },
  { name: 'Western Bulldogs', primary: '#FF6B35', secondary: '#FFFFFF', emoji: '🐕', mascot: 'Bulldog' }
]

// Player Positions
const PLAYER_POSITIONS = [
  'Forward', 'Midfielder', 'Defender', 'Ruck', 'Interchange'
]

// Mock Dashboard Data
const DASHBOARD_DATA = {
  productiveTime: 12.4,
  focusedTime: 8.5,
  teams: [
    { name: 'Forward Line', utilization: 85, overUtilized: 15, underUtilized: 0 },
    { name: 'Midfield', utilization: 92, overUtilized: 8, underUtilized: 0 },
    { name: 'Defense', utilization: 78, overUtilized: 0, underUtilized: 22 },
    { name: 'Ruck Division', utilization: 88, overUtilized: 12, underUtilized: 0 },
    { name: 'Interchange', utilization: 65, overUtilized: 0, underUtilized: 35 }
  ],
  players: [
    { name: 'Marcus Bontempelli', team: 'Western Bulldogs', position: 'Midfielder', image: '🏉' },
    { name: 'Dustin Martin', team: 'Richmond Tigers', position: 'Midfielder', image: '🏉' },
    { name: 'Patrick Dangerfield', team: 'Geelong Cats', position: 'Midfielder', image: '🏉' }
  ]
}

function App() {
  // Dashboard State
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentView, setCurrentView] = useState('login')
  const [showPlayerStats, setShowPlayerStats] = useState(false)

  const [isLogin, setIsLogin] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [selectedPosition, setSelectedPosition] = useState('')
  const [showTeamSelector, setShowTeamSelector] = useState(false)
  const [showPositionSelector, setShowPositionSelector] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
    team: '',
    position: '',
    favoriteGround: ''
  })

  // Dashboard States
  const [showReferee, setShowReferee] = useState(true)
  const [showBall, setShowBall] = useState(true)
  const [showStaff, setShowStaff] = useState(false)
  const [showCrowd, setShowCrowd] = useState(true)
  const [activeTab, setActiveTab] = useState('player-tracking')

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    
    // Simulate authentication process
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    console.log('Form submitted:', formData)
    setIsLoading(false)
    
    // Switch to dashboard view
    setCurrentView('dashboard')
  }

  const toggleForm = () => {
    setIsLogin(!isLogin)
    setFormData({
      email: '',
      password: '',
      confirmPassword: '',
      name: '',
      team: '',
      position: '',
      favoriteGround: ''
    })
    setSelectedTeam(null)
    setSelectedPosition('')
  }

  const selectTeam = (team) => {
    setSelectedTeam(team)
    setFormData({ ...formData, team: team.name })
    setShowTeamSelector(false)
  }

  const selectPosition = (position) => {
    setSelectedPosition(position)
    setFormData({ ...formData, position })
    setShowPositionSelector(false)
  }

  // Download Report Function
  const downloadReport = () => {
    // Create the report data
    const reportData = {
      matchInfo: {
        teams: "Team A vs Team B",
        score: "2-1",
        time: "12:34",
        quarter: "3"
      },
      analytics: {
        possessionOverTime: [
          { time: "0-5min", teamA: 65, teamB: 35 },
          { time: "5-10min", teamA: 58, teamB: 42 },
          { time: "10-15min", teamA: 72, teamB: 28 },
          { time: "15-20min", teamA: 45, teamB: 55 },
          { time: "20-25min", teamA: 68, teamB: 32 }
        ],
        playerActivity: [
          { player: "Player A", actions: 85, position: "Midfield" },
          { player: "Player B", actions: 92, position: "Forward" },
          { player: "Player C", actions: 78, position: "Defender" },
          { player: "Player D", actions: 88, position: "Midfield" },
          { player: "Player E", actions: 76, position: "Forward" }
        ]
      },
      performanceMetrics: {
        goals: 2,
        assists: 1,
        shotsOnTarget: 5,
        possession: 62,
        passes: 245,
        tackles: 18
      },
      timestamp: new Date().toISOString(),
      generatedBy: "AFL Tracker Analytics"
    }

    // Convert to JSON string
    const jsonString = JSON.stringify(reportData, null, 2)
    
    // Create blob and download
    const blob = new Blob([jsonString], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `match-progression-analytics-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // Dashboard Component
  const Dashboard = () => (
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
              className={`control-btn ${showReferee ? 'active' : ''}`}
              onClick={() => setShowReferee(!showReferee)}
            >
              <Volume2 size={20} />
              <span>Show Referee</span>
            </button>
          </div>
          <div className="control-item">
            <button 
              className={`control-btn ${showBall ? 'active' : ''}`}
              onClick={() => setShowBall(!showBall)}
            >
              <Circle size={20} />
              <span>Show Ball</span>
            </button>
          </div>
          <div className="control-item">
            <button 
              className={`control-btn ${showStaff ? 'active' : ''}`}
              onClick={() => setShowStaff(!showStaff)}
            >
              <Users size={20} />
              <span>Show Staff</span>
            </button>
          </div>
          <div className="control-item">
            <button 
              className={`control-btn ${showCrowd ? 'active' : ''}`}
              onClick={() => setShowCrowd(!showCrowd)}
            >
              <Users size={20} />
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
              className={`tab-btn ${activeTab === 'player-tracking' ? 'active' : ''}`}
              onClick={() => setActiveTab('player-tracking')}
            >
              Player Tracking
            </button>
            <button 
              className={`tab-btn ${activeTab === 'crowd-heatmap' ? 'active' : ''}`}
              onClick={() => setActiveTab('crowd-heatmap')}
            >
              Crowd Heatmap
            </button>
            <button 
              className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveTab('analytics')}
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
            <button className="action-btn" onClick={() => setShowPlayerStats(true)}>
              <Eye size={16} />
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

        {/* Match Progression Analytics */}
        <div className="analytics-section">
          <div className="section-header">
            <h3>Match Progression Analytics</h3>
            <p>Analysis of match changes over time.</p>
            <button className="action-btn" onClick={downloadReport}>
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
                  <div className="bar" style={{ height: '60%' }}></div>
                  <div className="bar" style={{ height: '80%' }}></div>
                  <div className="bar" style={{ height: '40%' }}></div>
                  <div className="bar" style={{ height: '90%' }}></div>
                  <div className="bar" style={{ height: '70%' }}></div>
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
              <Eye size={16} />
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
              <MapPin size={24} />
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
  )

  // Player Stats View Component
  const PlayerStatsView = () => (
    <div className="player-stats-container">
      {/* Header */}
      <div className="player-stats-header">
        <div className="header-left">
          <button 
            className="back-btn"
            onClick={() => setShowPlayerStats(false)}
          >
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <div className="header-icon">📊</div>
          <h1>Player Stats View</h1>
        </div>
        <div className="header-right">
          <nav className="header-nav">
            <a href="#" className="nav-link">Home</a>
            <a href="#" className="nav-link">Matches</a>
            <a href="#" className="nav-link">Players</a>
            <a href="#" className="nav-link">Stats</a>
          </nav>
          <div className="search-bar">
            <Search size={16} />
            <input type="text" placeholder="Search in site" />
          </div>
        </div>
      </div>

      {/* Current Match Section */}
      <div className="current-match-section">
        <h2>Current Match: Team A vs Team B</h2>
        <p>Player Statistics Overview</p>
        <div className="match-tabs">
          <button className="tab-btn active">Overview</button>
          <button className="tab-btn">Heatmaps</button>
          <button className="tab-btn">Performance</button>
        </div>
      </div>

      {/* Player Statistics Section */}
      <div className="player-statistics-section">
        <h3>Player Statistics</h3>
        <p>Detailed stats for each player in the match.</p>
        <div className="player-cards">
          <div className="player-card">
            <div className="player-position">Midfielder</div>
            <div className="player-image-placeholder">
              <span>Player A Image</span>
            </div>
            <div className="player-info">
              <h4>Player A</h4>
              <p>Jersey No: 10</p>
            </div>
          </div>
          <div className="player-card">
            <div className="player-position">Forward</div>
            <div className="player-image-placeholder">
              <span>Player B Image</span>
            </div>
            <div className="player-info">
              <h4>Player B</h4>
              <p>Jersey No: 7</p>
            </div>
          </div>
          <div className="player-card">
            <div className="player-position">Forward</div>
            <div className="player-image-placeholder">
              <span>Player C Image</span>
            </div>
            <div className="player-info">
              <h4>Player C</h4>
              <p>Jersey No: 4</p>
            </div>
          </div>
        </div>
      </div>

      {/* Team Performance Metrics Section */}
      <div className="team-performance-section">
        <h3>Team Performance Metrics</h3>
        <p>Analyze team's overall performance statistics.</p>
        <button className="action-btn">View Detailed Analysis</button>
        <div className="charts-container">
          <div className="chart-card">
            <h4>Average Speed by Player</h4>
            <div className="chart">
              <div className="chart-y-axis">Speed (km/h)</div>
              <div className="bar-chart">
                <div className="bar" style={{ height: '60%' }}></div>
                <div className="bar" style={{ height: '80%' }}></div>
                <div className="bar" style={{ height: '40%' }}></div>
                <div className="bar" style={{ height: '90%' }}></div>
                <div className="bar" style={{ height: '70%' }}></div>
                <div className="bar" style={{ height: '50%' }}></div>
              </div>
              <div className="chart-x-axis">Player</div>
            </div>
          </div>
          <div className="chart-card">
            <h4>Distance Covered Over Time</h4>
            <div className="chart">
              <div className="chart-y-axis">Distance (km)</div>
              <div className="line-chart">
                <div className="line-path"></div>
                <div className="line-fill"></div>
              </div>
              <div className="chart-x-axis">Time</div>
            </div>
          </div>
        </div>
      </div>

      {/* Player Heatmap Zones Section */}
      <div className="heatmap-zones-section">
        <h3>Player Heatmap Zones</h3>
        <p>Visual representation of player movements during the match.</p>
        <button className="action-btn">Show Heatmap</button>
        <div className="heatmap-cards">
          <div className="heatmap-card">
            <div className="heatmap-placeholder"></div>
            <div className="heatmap-info">
              <h4>Player A</h4>
              <p>Heatmap Zone: Defensive Midfield</p>
            </div>
          </div>
          <div className="heatmap-card">
            <div className="heatmap-placeholder"></div>
            <div className="heatmap-info">
              <h4>Player B</h4>
              <p>Heatmap Zone: Attacking Half</p>
            </div>
          </div>
        </div>
      </div>

      {/* Player Tracking Stability Section */}
      <div className="tracking-stability-section">
        <h3>Player Tracking Stability</h3>
        <p>View tracking stability for all players.</p>
        <div className="stability-list">
          <div className="stability-item">
            <BarChart size={20} />
            <div className="stability-info">
              <h4>Player A</h4>
              <p>Stability: High</p>
            </div>
          </div>
          <div className="stability-item">
            <LineChart size={20} />
            <div className="stability-info">
              <h4>Player B</h4>
              <p>Stability: Medium</p>
            </div>
          </div>
          <div className="stability-item">
            <BarChart size={20} />
            <div className="stability-info">
              <h4>Player C</h4>
              <p>Stability: Low</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="player-stats-footer">
        <a href="#">Follow Us on Social Media</a>
        <a href="#">Contact Support</a>
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
      </div>
    </div>
  )

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
                      {selectedTeam ? `${selectedTeam.emoji} ${selectedTeam.name}` : 'Select your team'}
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
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
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
                    <span className="checkmark"></span>
                    I agree to the <a href="#">Terms & Privacy</a>
                  </label>
                </div>
              )}

              <button type="submit" className="submit-btn" disabled={isLoading}>
                {isLoading ? (
                  <div className="loading-spinner"></div>
                ) : (
                  isLogin ? 'Login' : 'Sign Up'
                )}
              </button>
            </form>

            {/* Form Toggle */}
            <div className="form-toggle">
              <p>
                {isLogin ? "Don't have an account?" : "Already have an account?"}
                <button onClick={toggleForm} className="toggle-link">
                  {isLogin ? 'Sign up' : 'Sign in'}
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
            <p>Advanced analytics and real-time monitoring for professional teams</p>
          </div>

          <div className="dashboard-card">
            <div className="dashboard-header">
              <h3>Dashboard</h3>
              <div className="dashboard-controls">
                <select className="team-select">
                  <option>All Teams</option>
                  {AFL_TEAMS.map(team => (
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
                <div className="metric-value">{DASHBOARD_DATA.productiveTime} hr</div>
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
                <div className="metric-value">{DASHBOARD_DATA.focusedTime} hr</div>
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
                      <div className="bar overall" style={{ width: `${team.utilization}%` }}></div>
                      <div className="bar over" style={{ width: `${team.overUtilized}%` }}></div>
                      <div className="bar under" style={{ width: `${team.underUtilized}%` }}></div>
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
                      <div className="player-details">{player.team} • {player.position}</div>
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
  )

  return (
    <div className="app">
      {currentView === 'dashboard' ? (
        showPlayerStats ? <PlayerStatsView /> : <Dashboard />
      ) : (
        <Authentication />
      )}
    </div>
  )
}

export default App
