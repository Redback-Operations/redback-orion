import React, { useState, useCallback, memo } from 'react'
import {
  Eye, EyeOff, User, Mail, Lock, Shield, ArrowRight, ArrowLeft, Users, MapPin, Trophy, Target,
  BarChart3, TrendingUp, Calendar, Plus, Volume2, Circle, Download, Activity, Clock, Star, Search,
  BarChart, LineChart, Upload, Video, Play, Pause, FileVideo, AlertCircle, CheckCircle
} from 'lucide-react'
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

// Player Positions (not used in current UI, keeping for future)
const PLAYER_POSITIONS = ['Forward', 'Midfielder', 'Defender', 'Ruck', 'Interchange']

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

/* =========================
   HOISTED CHILD COMPONENTS
   ========================= */

const Dashboard = memo(function Dashboard({
  showReferee, showBall, showStaff, showCrowd,
  setShowReferee, setShowBall, setShowStaff, setShowCrowd,
  activeTab, setActiveTab,
  setShowPlayerStats, setShowCrowdHeatmap,
  downloadReport
}) {
  const [uploadedVideo, setUploadedVideo] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisResults, setAnalysisResults] = useState(null)

  const handleVideoUpload = (event) => {
    const file = event.target.files[0]
    if (file && file.type.startsWith('video/')) {
      setUploadedVideo(file)
      setAnalysisComplete(false)
      setAnalysisResults(null)
    }
  }

  const startAnalysis = async () => {
    if (!uploadedVideo) return
    
    setIsAnalyzing(true)
    setAnalysisProgress(0)
    
    // Simulate analysis progress
    const interval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsAnalyzing(false)
          setAnalysisComplete(true)
          // Generate mock analysis results
          setAnalysisResults({
            matchDuration: '2:15:30',
            totalPlayers: 36,
            goals: 12,
            assists: 8,
            possession: { teamA: 58, teamB: 42 },
            playerStats: [
              { name: 'Player A', goals: 3, assists: 2, distance: '8.5km', speed: '12.3km/h' },
              { name: 'Player B', goals: 2, assists: 1, distance: '7.8km', speed: '11.9km/h' },
              { name: 'Player C', goals: 1, assists: 3, distance: '9.2km', speed: '13.1km/h' }
            ],
            crowdDensity: {
              peak: 1500,
              average: 1200,
              zones: [
                { zone: 'North Stand', density: 85, capacity: 500 },
                { zone: 'South Stand', density: 72, capacity: 500 },
                { zone: 'East Stand', density: 68, capacity: 400 },
                { zone: 'West Stand', density: 75, capacity: 400 }
              ]
            },
            keyEvents: [
              { time: '00:15:30', event: 'Goal by Team A', player: 'Player A' },
              { time: '00:28:45', event: 'Yellow Card', player: 'Player B' },
              { time: '00:45:12', event: 'Goal by Team B', player: 'Player C' },
              { time: '01:12:33', event: 'Goal by Team A', player: 'Player A' },
              { time: '01:45:20', event: 'Red Card', player: 'Player D' }
            ]
          })
          return 100
        }
        return prev + Math.random() * 15
      })
    }, 500)
  }

  const resetAnalysis = () => {
    setUploadedVideo(null)
    setAnalysisComplete(false)
    setAnalysisResults(null)
    setAnalysisProgress(0)
  }
  return (
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
        {/* Video Upload Section */}
        <div className="video-upload-section">
          <div className="section-header">
            <div className="header-content">
              <h2>Match Video Analysis</h2>
              <p>Upload your match video to get comprehensive analysis and insights</p>
            </div>
          </div>
          
          {!uploadedVideo ? (
            <div className="upload-area">
              <div className="upload-zone">
                <Upload size={48} />
                <h3>Upload Match Video</h3>
                <p>Drag and drop your video file here or click to browse</p>
                <p className="file-types">Supported formats: MP4, AVI, MOV, MKV (Max 500MB)</p>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleVideoUpload}
                  className="file-input"
                  id="video-upload"
                />
                <label htmlFor="video-upload" className="upload-btn">
                  Choose Video File
                </label>
              </div>
            </div>
          ) : (
            <div className="video-preview-section">
              <div className="video-info">
                <div className="video-details">
                  <FileVideo size={24} />
                  <div className="video-text">
                    <h4>{uploadedVideo.name}</h4>
                    <p>{(uploadedVideo.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                </div>
                <div className="video-actions">
                  {!isAnalyzing && !analysisComplete && (
                    <button className="action-btn primary" onClick={startAnalysis}>
                      <Play size={16} />
                      Start Analysis
                    </button>
                  )}
                  {!isAnalyzing && analysisComplete && (
                    <button className="action-btn secondary" onClick={resetAnalysis}>
                      <Upload size={16} />
                      Upload New Video
                    </button>
                  )}
                  <button className="action-btn" onClick={resetAnalysis}>
                    <AlertCircle size={16} />
                    Remove
                  </button>
                </div>
              </div>

              {isAnalyzing && (
                <div className="analysis-progress">
                  <div className="progress-header">
                    <h4>Analyzing Video...</h4>
                    <span>{Math.round(analysisProgress)}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${analysisProgress}%` }}
                    ></div>
                  </div>
                  <div className="progress-steps">
                    <div className={`step ${analysisProgress > 0 ? 'active' : ''}`}>
                      <CheckCircle size={16} />
                      <span>Processing video frames</span>
                    </div>
                    <div className={`step ${analysisProgress > 25 ? 'active' : ''}`}>
                      <CheckCircle size={16} />
                      <span>Detecting players and objects</span>
                    </div>
                    <div className={`step ${analysisProgress > 50 ? 'active' : ''}`}>
                      <CheckCircle size={16} />
                      <span>Tracking movements and events</span>
                    </div>
                    <div className={`step ${analysisProgress > 75 ? 'active' : ''}`}>
                      <CheckCircle size={16} />
                      <span>Generating analysis report</span>
                    </div>
                  </div>
                </div>
              )}

              {analysisComplete && analysisResults && (
                <div className="analysis-results">
                  <div className="results-header">
                    <h3>Analysis Complete!</h3>
                    <p>Comprehensive match analysis results</p>
                  </div>
                  
                  <div className="results-grid">
                    <div className="result-card">
                      <h4>Match Overview</h4>
                      <div className="result-stats">
                        <div className="stat">
                          <span className="label">Duration:</span>
                          <span className="value">{analysisResults.matchDuration}</span>
                        </div>
                        <div className="stat">
                          <span className="label">Total Players:</span>
                          <span className="value">{analysisResults.totalPlayers}</span>
                        </div>
                        <div className="stat">
                          <span className="label">Goals:</span>
                          <span className="value">{analysisResults.goals}</span>
                        </div>
                        <div className="stat">
                          <span className="label">Assists:</span>
                          <span className="value">{analysisResults.assists}</span>
                        </div>
                      </div>
                    </div>

                    <div className="result-card">
                      <h4>Possession</h4>
                      <div className="possession-chart">
                        <div className="possession-bar">
                          <div 
                            className="team-a" 
                            style={{ width: `${analysisResults.possession.teamA}%` }}
                          >
                            <span>Team A: {analysisResults.possession.teamA}%</span>
                          </div>
                          <div 
                            className="team-b" 
                            style={{ width: `${analysisResults.possession.teamB}%` }}
                          >
                            <span>Team B: {analysisResults.possession.teamB}%</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="result-card">
                      <h4>Top Performers</h4>
                      <div className="player-list">
                        {analysisResults.playerStats.map((player, index) => (
                          <div key={index} className="player-stat">
                            <div className="player-name">{player.name}</div>
                            <div className="player-metrics">
                              <span>⚽ {player.goals} goals</span>
                              <span>🎯 {player.assists} assists</span>
                              <span>🏃 {player.distance}</span>
                              <span>⚡ {player.speed}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="result-card">
                      <h4>Crowd Analysis</h4>
                      <div className="crowd-stats">
                        <div className="crowd-metric">
                          <span className="label">Peak Attendance:</span>
                          <span className="value">{analysisResults.crowdDensity.peak.toLocaleString()}</span>
                        </div>
                        <div className="crowd-metric">
                          <span className="label">Average Attendance:</span>
                          <span className="value">{analysisResults.crowdDensity.average.toLocaleString()}</span>
                        </div>
                      </div>
                      <div className="zone-list">
                        {analysisResults.crowdDensity.zones.map((zone, index) => (
                          <div key={index} className="zone-item">
                            <span className="zone-name">{zone.zone}</span>
                            <div className="zone-bar">
                              <div 
                                className="zone-fill" 
                                style={{ width: `${zone.density}%` }}
                              ></div>
                            </div>
                            <span className="zone-density">{zone.density}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="key-events">
                    <h4>Key Match Events</h4>
                    <div className="events-timeline">
                      {analysisResults.keyEvents.map((event, index) => (
                        <div key={index} className="event-item">
                          <div className="event-time">{event.time}</div>
                          <div className="event-content">
                            <div className="event-title">{event.event}</div>
                            <div className="event-player">{event.player}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="results-actions">
                    <button className="action-btn primary">
                      <Download size={16} />
                      Download Full Report
                    </button>
                    <button className="action-btn">
                      <BarChart3 size={16} />
                      View Detailed Analytics
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

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
              onClick={() => setShowCrowdHeatmap(true)}
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
              <div className="metric-icon">🎯</div>
              <div className="metric-content">
                <h4>Shots on Target</h4>
                <div className="metric-value">5</div>
                <div className="metric-change positive">+2</div>
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
})

const PlayerStatsView = memo(function PlayerStatsView({ setShowPlayerStats }) {
  return (
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
})

const CrowdHeatmapView = memo(function CrowdHeatmapView({ setShowCrowdHeatmap }) {
  const [activeFilter, setActiveFilter] = useState('current-density')
  const [crowdData] = useState({
    totalDensity: 1200,
    densityChange: 200,
    trend: 'Increased',
    trendDirection: 'Upward',
    zoneData: [
      { zone: 'Zone A', density: 65, color: '#e5e7eb' },
      { zone: 'Zone B', density: 25, color: '#9ca3af' },
      { zone: 'Zone C', density: 10, color: '#374151' }
    ],
    timeSeriesData: [
      { time: '10:00', density: 800 },
      { time: '10:15', density: 950 },
      { time: '10:30', density: 1100 },
      { time: '10:45', density: 1050 },
      { time: '11:00', density: 1200 }
    ]
  })

  return (
    <div className="crowd-heatmap-container">
      {/* Header */}
      <div className="crowd-heatmap-header">
        <div className="header-left">
          <button
            className="back-btn"
            onClick={() => setShowCrowdHeatmap(false)}
          >
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>
          <div className="header-icon">🔥</div>
          <h1>Crowd Heatmap Screen</h1>
        </div>
        <div className="header-right">
          <nav className="header-nav">
            <a href="#" className="nav-link">Home</a>
            <a href="#" className="nav-link">Match Details</a>
            <a href="#" className="nav-link">Player Tracking</a>
            <a href="#" className="nav-link">Analytics</a>
          </nav>
          <div className="search-bar">
            <Search size={16} />
            <input type="text" placeholder="Search in site" />
          </div>
        </div>
      </div>

      {/* Crowd Density Overview Section */}
      <div className="crowd-overview-section">
        <div className="section-header">
          <div className="header-content">
            <h2>Crowd Density Overview</h2>
            <p>Real-time visualization of crowd density in each zone.</p>
          </div>
          <div className="filter-buttons">
            <button
              className={`filter-btn ${activeFilter === 'current-density' ? 'active' : ''}`}
              onClick={() => setActiveFilter('current-density')}
            >
              Current Density
            </button>
            <button
              className={`filter-btn ${activeFilter === 'historical-data' ? 'active' : ''}`}
              onClick={() => setActiveFilter('historical-data')}
            >
              Historical Data
            </button>
            <button
              className={`filter-btn ${activeFilter === 'analysis' ? 'active' : ''}`}
              onClick={() => setActiveFilter('analysis')}
            >
              Analysis
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="crowd-content-grid">
        {/* Left Column */}
        <div className="left-column">
          {/* Total Crowd Density Section */}
          <div className="total-density-section">
            <div className="section-header">
              <div className="header-content">
                <h3>Total Crowd Density</h3>
                <p>Current density metrics for the crowd in designated zones.</p>
              </div>
              <button className="action-btn">
                <Eye size={16} />
                View Detailed Metrics
              </button>
            </div>
            <div className="density-metrics">
              <div className="metric-card">
                <div className="metric-icon">👥</div>
                <div className="metric-content">
                  <h4>Total Density</h4>
                  <div className="metric-value">{crowdData.totalDensity.toLocaleString()} people</div>
                  <div className="metric-change positive">+{crowdData.densityChange}</div>
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-icon">📈</div>
                <div className="metric-content">
                  <h4>Density Trend</h4>
                  <div className="metric-value">{crowdData.trend}</div>
                  <div className="metric-change">{crowdData.trendDirection}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Density Trend Over Time Section */}
          <div className="trend-section">
            <div className="section-header">
              <div className="header-content">
                <h3>Density Trend Over Time</h3>
              </div>
            </div>
            <div className="trend-chart">
              <div className="chart-y-axis">Density</div>
                             <div className="line-chart-container">
                 <svg className="line-chart" viewBox="0 0 400 200" preserveAspectRatio="none">
                   <defs>
                     <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                       <stop offset="0%" stopColor="#4285f4" stopOpacity="0.8"/>
                       <stop offset="100%" stopColor="#4285f4" stopOpacity="0.1"/>
                     </linearGradient>
                   </defs>
                   {/* Grid lines for better readability */}
                   <line x1="0" y1="50" x2="400" y2="50" stroke="#e0e0e0" strokeWidth="1" opacity="0.5"/>
                   <line x1="0" y1="100" x2="400" y2="100" stroke="#e0e0e0" strokeWidth="1" opacity="0.5"/>
                   <line x1="0" y1="150" x2="400" y2="150" stroke="#e0e0e0" strokeWidth="1" opacity="0.5"/>
                   
                   {/* Main trend line */}
                   <path
                     d="M 20,160 L 100,130 L 180,110 L 260,120 L 340,90"
                     stroke="#4285f4"
                     strokeWidth="3"
                     fill="none"
                     className="trend-line"
                     strokeLinecap="round"
                     strokeLinejoin="round"
                   />
                   
                   {/* Gradient fill area */}
                   <path
                     d="M 20,160 L 100,130 L 180,110 L 260,120 L 340,90 L 340,180 L 20,180 Z"
                     fill="url(#lineGradient)"
                     className="trend-fill"
                   />
                   
                   {/* Data points */}
                   <circle cx="20" cy="160" r="4" fill="#4285f4"/>
                   <circle cx="100" cy="130" r="4" fill="#4285f4"/>
                   <circle cx="180" cy="110" r="4" fill="#4285f4"/>
                   <circle cx="260" cy="120" r="4" fill="#4285f4"/>
                   <circle cx="340" cy="90" r="4" fill="#4285f4"/>
                 </svg>
               </div>
              <div className="chart-x-axis">Time</div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="right-column">
          {/* Crowd Zone Density Section */}
          <div className="zone-density-section">
            <div className="section-header">
              <div className="header-content">
                <h3>Crowd Zone Density</h3>
                <p>Visualization of crowd density in marked zones.</p>
              </div>
              <button className="action-btn">
                <Download size={16} />
                Download Heatmap
              </button>
            </div>
            <div className="heatmap-container">
              <h4>Density Heatmap</h4>
              <div className="pie-chart-container">
                <div className="pie-chart">
                  <div className="pie-segment" style={{
                    background: `conic-gradient(${crowdData.zoneData[0].color} 0deg ${crowdData.zoneData[0].density * 3.6}deg, 
                                               ${crowdData.zoneData[1].color} ${crowdData.zoneData[0].density * 3.6}deg ${(crowdData.zoneData[0].density + crowdData.zoneData[1].density) * 3.6}deg,
                                               ${crowdData.zoneData[2].color} ${(crowdData.zoneData[0].density + crowdData.zoneData[1].density) * 3.6}deg 360deg)`
                  }}></div>
                </div>
                <div className="pie-legend">
                  {crowdData.zoneData.map((zone, index) => (
                    <div key={index} className="legend-item">
                      <div className="legend-color" style={{ backgroundColor: zone.color }}></div>
                      <span>{zone.zone}: {zone.density}%</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="chart-x-axis">Zones</div>
            </div>
          </div>

          {/* Static Camera Zone View Section */}
          <div className="camera-zone-section">
            <div className="section-header">
              <div className="header-content">
                <h3>Static Camera Zone View</h3>
              </div>
            </div>
            <div className="camera-view-container">
              <div className="camera-placeholder">
                <MapPin size={24} />
                <p>Static camera zone view with real-time crowd density heatmap.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="crowd-heatmap-footer">
        <a href="#">Follow Us on Social Media</a>
        <a href="#">Contact Support</a>
        <a href="#">Privacy Policy</a>
        <a href="#">Terms of Service</a>
      </div>
    </div>
  )
})

const Authentication = memo(function Authentication({
  AFL_TEAMS,
  isLogin, isLoading, formData,
  selectedTeam, showTeamSelector,
  handleInputChange, handleSubmit, toggleForm,
  setShowTeamSelector, selectTeam,
  showPassword, setShowPassword,
  showConfirmPassword, setShowConfirmPassword
}) {
  return (
    <div className="app-container">
      {/* Left Panel - Authentication Form with Image */}
      <div className="left-panel">
        {/* Image Section */}
        <div className="image-section">
          <div className="image-container">
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
                {DASHBOARD_DATA.teams.map((team) => (
                  <div key={`team-${team.name}`} className="utilization-row">
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
                {DASHBOARD_DATA.players.map((player) => (
                  <div key={`player-${player.name}`} className="player-item">
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
})

/* ===========
   APP (OWNER)
   =========== */

function App() {
  // Views
  const [currentView, setCurrentView] = useState('login')
  const [showPlayerStats, setShowPlayerStats] = useState(false)
  const [showCrowdHeatmap, setShowCrowdHeatmap] = useState(false)

  // Auth states
  const [isLogin, setIsLogin] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [showTeamSelector, setShowTeamSelector] = useState(false)
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

  // Dashboard display states
  const [showReferee, setShowReferee] = useState(true)
  const [showBall, setShowBall] = useState(true)
  const [showStaff, setShowStaff] = useState(false)
  const [showCrowd, setShowCrowd] = useState(true)
  const [activeTab, setActiveTab] = useState('player-tracking')

  // Handlers (memoized)
  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }, [])

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault()
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 2000)) // simulate auth
    console.log('Form submitted:', formData)
    setIsLoading(false)
    setCurrentView('dashboard')
  }, [formData])

  const toggleForm = useCallback(() => {
    setIsLogin(prev => !prev)
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
  }, [])

  const selectTeam = useCallback((team) => {
    setSelectedTeam(team)
    setFormData(prev => ({ ...prev, team: team.name }))
    setShowTeamSelector(false)
  }, [])

  // Download Report Function
  const downloadReport = useCallback(() => {
    const reportData = {
      matchInfo: { teams: "Team A vs Team B", score: "2-1", time: "12:34", quarter: "3" },
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
      performanceMetrics: { goals: 2, assists: 1, shotsOnTarget: 5, possession: 62, passes: 245, tackles: 18 },
      timestamp: new Date().toISOString(),
      generatedBy: "AFL Tracker Analytics"
    }

    const jsonString = JSON.stringify(reportData, null, 2)
    const blob = new Blob([jsonString], { type: 'application/json' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `match-progression-analytics-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }, [])

  return (
    <div className="app">
      {currentView === 'dashboard' ? (
        showPlayerStats ? (
          <PlayerStatsView setShowPlayerStats={setShowPlayerStats} />
        ) : showCrowdHeatmap ? (
          <CrowdHeatmapView setShowCrowdHeatmap={setShowCrowdHeatmap} />
        ) : (
          <Dashboard
            showReferee={showReferee}
            showBall={showBall}
            showStaff={showStaff}
            showCrowd={showCrowd}
            setShowReferee={setShowReferee}
            setShowBall={setShowBall}
            setShowStaff={setShowStaff}
            setShowCrowd={setShowCrowd}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            setShowPlayerStats={setShowPlayerStats}
            setShowCrowdHeatmap={setShowCrowdHeatmap}
            downloadReport={downloadReport}
          />
        )
      ) : (
        <Authentication
          AFL_TEAMS={AFL_TEAMS}
          isLogin={isLogin}
          isLoading={isLoading}
          formData={formData}
          selectedTeam={selectedTeam}
          showTeamSelector={showTeamSelector}
          handleInputChange={handleInputChange}
          handleSubmit={handleSubmit}
          toggleForm={toggleForm}
          setShowTeamSelector={setShowTeamSelector}
          selectTeam={selectTeam}
          showPassword={showPassword}
          setShowPassword={setShowPassword}
          showConfirmPassword={showConfirmPassword}
          setShowConfirmPassword={setShowConfirmPassword}
        />
      )}
    </div>
  )
}

export default App
