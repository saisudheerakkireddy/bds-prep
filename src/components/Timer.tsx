import { useState, useEffect, useCallback } from "react";

const FOCUS_MINUTES = 25;
const BREAK_MINUTES = 5;

type Mode = "focus" | "break";

function toSeconds(minutes: number) {
  return minutes * 60;
}

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

export default function Timer() {
  const [mode, setMode] = useState<Mode>("focus");
  const [totalSeconds, setTotalSeconds] = useState(toSeconds(FOCUS_MINUTES));
  const [remaining, setRemaining] = useState(toSeconds(FOCUS_MINUTES));
  const [isRunning, setIsRunning] = useState(false);

  const resetForMode = useCallback((m: Mode) => {
    const mins = m === "focus" ? FOCUS_MINUTES : BREAK_MINUTES;
    const secs = toSeconds(mins);
    setTotalSeconds(secs);
    setRemaining(secs);
    setMode(m);
  }, []);

  useEffect(() => {
    if (!isRunning || remaining <= 0) return;
    const t = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          setIsRunning(false);
          return 0;
        }
        return r - 1;
      });
    }, 1000);
    return () => clearInterval(t);
  }, [isRunning, remaining]);

  useEffect(() => {
    if (remaining === 0 && totalSeconds > 0) {
      const nextMode: Mode = mode === "focus" ? "break" : "focus";
      resetForMode(nextMode);
    }
  }, [remaining, totalSeconds, mode, resetForMode]);

  const progress = totalSeconds > 0 ? 1 - remaining / totalSeconds : 1;
  const circumference = 2 * Math.PI * 54;
  const strokeDashoffset = circumference * (1 - progress);

  const handlePlayPause = () => {
    if (remaining === 0) {
      resetForMode(mode);
    }
    setIsRunning((r) => !r);
  };

  const handleModeClick = (m: Mode) => {
    if (m === mode) return;
    setIsRunning(false);
    resetForMode(m);
  };

  return (
    <div className="timer-widget" role="region" aria-label="Focus and break timer">
      <h2 className="timer-widget__title">Timer</h2>
      <div className="timer-widget__tabs" role="tablist" aria-label="Timer mode">
        <button
          type="button"
          role="tab"
          aria-selected={mode === "focus"}
          aria-label="Focus mode"
          className={`timer-widget__tab ${mode === "focus" ? "timer-widget__tab--active" : ""}`}
          onClick={() => handleModeClick("focus")}
        >
          Focus
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === "break"}
          aria-label="Break mode"
          className={`timer-widget__tab ${mode === "break" ? "timer-widget__tab--active" : ""}`}
          onClick={() => handleModeClick("break")}
        >
          Break
        </button>
      </div>
      <div className="timer-widget__ring-wrap">
        <svg className="timer-widget__ring" viewBox="0 0 120 120" aria-hidden>
          <circle
            className="timer-widget__ring-bg"
            cx="60"
            cy="60"
            r="54"
            fill="none"
            strokeWidth="6"
          />
          <circle
            className="timer-widget__ring-progress"
            cx="60"
            cy="60"
            r="54"
            fill="none"
            strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform="rotate(-90 60 60)"
          />
        </svg>
        <span className="timer-widget__display" aria-live="polite">
          {formatTime(remaining)}
        </span>
      </div>
      <button
        type="button"
        className="timer-widget__play"
        onClick={handlePlayPause}
        aria-label={isRunning ? "Pause" : "Play"}
      >
        <span className="timer-widget__play-icon" aria-hidden>
          {isRunning ? "⏸" : "▶"}
        </span>
        <span>{isRunning ? "Pause" : "Play"}</span>
      </button>
    </div>
  );
}
