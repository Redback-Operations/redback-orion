import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye, EyeOff, User, Mail, Lock, Shield, ArrowRight, ArrowLeft, Users, MapPin, Trophy, Target, BarChart3, TrendingUp, Users as TeamIcon, Calendar, Plus } from 'lucide-react'
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

  return (
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
}

export default App
