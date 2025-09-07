export const TEAMS = [
  { id: 'COL', name: 'Collingwood', color: '#111111', accent: '#00B0FF', logo: '/logos/COL.svg' },
  { id: 'CAR', name: 'Carlton',     color: '#1F3A93', accent: '#F5C400', logo: '/logos/CAR.svg' },
  { id: 'RIC', name: 'Richmond',     color: '#1A1A1A', accent: '#F5C400', logo: '/logos/RIC.svg' },
  { id: 'GEE', name: 'Geelong',      color: '#0B2545', accent: '#6EC1FF', logo: '/logos/GEE.svg' },
]

export const CURRENT_MATCH = {
  home: { id: 'COL', name: 'Collingwood', score: 72, logo: '/logos/COL.svg', color: '#111111' },
  away: { id: 'CAR', name: 'Carlton',     score: 68, logo: '/logos/CAR.svg', color: '#1F3A93' },
  period: 'Q3',
  timeLeft: '06:21',
  possession: { home: 54, away: 46 },
  keyStats: [
    { label: 'Disposals', value: '210' },
    { label: 'Tackles',   value: '43'  },
    { label: 'Inside 50s', value: '38' },
  ],
}

export const HIGHLIGHTS = [
  { id: 1, title: 'Mark + Goal (COL)', ts: 'Q2 10:32' },
  { id: 2, title: 'Big Tackle (CAR)',  ts: 'Q2 04:15' },
  { id: 3, title: 'Coast-to-coast Play', ts: 'Q3 08:41' },
  { id: 4, title: 'Snap Goal (CAR)',     ts: 'Q3 07:02' },
]

export const TRENDS = [
  { name: 'Q1', COL: 22, CAR: 18 },
  { name: 'Q2', COL: 43, CAR: 40 },
  { name: 'Q3', COL: 72, CAR: 68 },
]

export const FIXTURES = [
  { date: '2025-08-10', opponent: 'Geelong',  venue: 'MCG',   status: 'UPCOMING' },
  { date: '2025-08-03', opponent: 'Richmond', venue: 'Marvel',status: 'W 82–74' },
  { date: '2025-07-27', opponent: 'Carlton',  venue: 'MCG',   status: 'L 70–76' },
]
