import { useState, useEffect } from "react";

interface ExamCountdownProps {
  examDate: string;
  subjectName: string;
  icon: string;
}

const LABELS = {
  days: { full: "Days", short: "Days" },
  hours: { full: "Hours", short: "Hrs" },
  minutes: { full: "Minutes", short: "Mins" },
  seconds: { full: "Seconds", short: "Secs" },
} as const;

function useNarrowViewport(breakpoint = 420) {
  const [narrow, setNarrow] = useState(
    typeof window !== "undefined" ? window.innerWidth < breakpoint : false
  );
  useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${breakpoint}px)`);
    const handler = () => setNarrow(mql.matches);
    handler();
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, [breakpoint]);
  return narrow;
}

export default function ExamCountdown({
  examDate,
  subjectName,
  icon,
}: ExamCountdownProps) {
  const [timeLeft, setTimeLeft] = useState(getTimeLeft(examDate));
  const narrow = useNarrowViewport();

  useEffect(() => {
    const timer = setInterval(() => setTimeLeft(getTimeLeft(examDate)), 1000);
    return () => clearInterval(timer);
  }, [examDate]);

  if (timeLeft.total <= 0) {
    return (
      <>
        <h2 className="hero-title">
          {icon} {subjectName} — Exam day!
        </h2>
        <div className="next-exam-details">
          <div className="next-subject">Good luck!</div>
          <div className="next-meta">You've got this.</div>
        </div>
      </>
    );
  }

  const labels = narrow
    ? { days: LABELS.days.short, hours: LABELS.hours.short, minutes: LABELS.minutes.short, seconds: LABELS.seconds.short }
    : { days: LABELS.days.full, hours: LABELS.hours.full, minutes: LABELS.minutes.full, seconds: LABELS.seconds.full };

  return (
    <>
      <h2 className="hero-title">Next exam</h2>
      <div className="countdown-timer">
        <div className="time-block">
          <span className="time-value">{String(timeLeft.days).padStart(2, "0")}</span>
          <span className="time-label">{labels.days}</span>
        </div>
        <span className="countdown-separator" aria-hidden>:</span>
        <div className="time-block">
          <span className="time-value">{String(timeLeft.hours).padStart(2, "0")}</span>
          <span className="time-label">{labels.hours}</span>
        </div>
        <span className="countdown-separator" aria-hidden>:</span>
        <div className="time-block">
          <span className="time-value">{String(timeLeft.minutes).padStart(2, "0")}</span>
          <span className="time-label">{labels.minutes}</span>
        </div>
        <span className="countdown-separator" aria-hidden>:</span>
        <div className="time-block">
          <span className="time-value">{String(timeLeft.seconds).padStart(2, "0")}</span>
          <span className="time-label">{labels.seconds}</span>
        </div>
      </div>
      <div className="next-exam-details">
        <div className="next-subject">
          {icon} {subjectName}
        </div>
        <div className="next-meta">
          {new Date(examDate).toLocaleDateString("en-IN", {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric",
          })}{" "}
          · 10:00 AM – 1:00 PM
        </div>
      </div>
    </>
  );
}

function getTimeLeft(examDate: string) {
  const total = new Date(examDate + "T10:00:00+05:30").getTime() - Date.now();
  return {
    total,
    days: Math.max(0, Math.floor(total / (1000 * 60 * 60 * 24))),
    hours: Math.max(0, Math.floor((total / (1000 * 60 * 60)) % 24)),
    minutes: Math.max(0, Math.floor((total / (1000 * 60)) % 60)),
    seconds: Math.max(0, Math.floor((total / 1000) % 60)),
  };
}
