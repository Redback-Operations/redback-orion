import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Play, Pause, Clock } from 'lucide-react';

export default function LiveClock({ isLive, onToggleLive, matchTime }) {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [gameTime, setGameTime] = useState({
    quarter: matchTime?.quarter || 2,
    minutes: 15,
    seconds: 23
  });

  // Update current time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Update game time when live
  useEffect(() => {
    if (!isLive) return;

    const gameTimer = setInterval(() => {
      setGameTime(prev => {
        let newSeconds = prev.seconds - 1;
        let newMinutes = prev.minutes;
        let newQuarter = prev.quarter;

        if (newSeconds < 0) {
          newSeconds = 59;
          newMinutes -= 1;
        }

        if (newMinutes < 0) {
          newMinutes = 19;
          newSeconds = 59;
          newQuarter += 1;
          if (newQuarter > 4) {
            newQuarter = 4;
            newMinutes = 0;
            newSeconds = 0;
          }
        }

        return {
          quarter: newQuarter,
          minutes: newMinutes,
          seconds: newSeconds
        };
      });
    }, 1000);

    return () => clearInterval(gameTimer);
  }, [isLive]);

  const formatTime = (time) => {
    return time.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatGameTime = () => {
    const mins = gameTime.minutes.toString().padStart(2, '0');
    const secs = gameTime.seconds.toString().padStart(2, '0');
    return `${mins}:${secs}`;
  };

  return (
    <div className="flex flex-col sm:flex-row items-center gap-3 p-3 bg-white rounded-lg border shadow-sm">
      {/* Live Status */}
      <div className="flex items-center gap-2">
        <Badge 
          variant={isLive ? "destructive" : "secondary"} 
          className={`${isLive ? 'animate-pulse' : ''} font-medium`}
        >
          <div className={`w-2 h-2 rounded-full mr-2 ${isLive ? 'bg-red-500' : 'bg-gray-400'}`} />
          {isLive ? "LIVE" : "OFFLINE"}
        </Badge>
        
        <Button
          variant="outline"
          size="sm"
          onClick={() => onToggleLive(!isLive)}
          className="flex items-center gap-1"
        >
          {isLive ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
          {isLive ? 'Pause' : 'Go Live'}
        </Button>
      </div>

      {/* Time Display */}
      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-1">
          <Clock className="w-4 h-4 text-gray-500" />
          <span className="font-mono">{formatTime(currentTime)}</span>
        </div>
        
        {isLive && (
          <>
            <div className="h-4 w-px bg-gray-300" />
            <div className="flex items-center gap-2">
              <span className="text-gray-600">Q{gameTime.quarter}</span>
              <span className="font-mono font-medium">{formatGameTime()}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
