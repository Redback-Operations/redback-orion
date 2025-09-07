import { useEffect, useState } from 'react'

export default function useLiveClock() {
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(t)
  }, [])
  return now.toLocaleString('en-AU', { hour12: false, timeZone: 'Australia/Melbourne' })
}
