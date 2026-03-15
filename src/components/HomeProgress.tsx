import { useState, useEffect } from "react";
import { getProgress } from "../lib/progress";

interface SubjectProgress {
  slug: string;
  shortName: string;
  totalQuestions: number;
}

interface HomeProgressProps {
  subjects: SubjectProgress[];
}

export default function HomeProgress({ subjects }: HomeProgressProps) {
  const [progress, setProgress] = useState<Record<string, string[]>>({});

  useEffect(() => {
    setProgress(getProgress());
    const handler = () => setProgress(getProgress());
    window.addEventListener("storage", handler);
    window.addEventListener("bds-prep-progress-synced", handler);
    return () => {
      window.removeEventListener("storage", handler);
      window.removeEventListener("bds-prep-progress-synced", handler);
    };
  }, []);

  const withContent = subjects.filter((s) => s.totalQuestions > 0);
  if (withContent.length === 0) return null;

  const totalCompleted = withContent.reduce(
    (sum, s) => sum + (progress[s.slug]?.length ?? 0),
    0
  );
  const totalQuestions = withContent.reduce(
    (sum, s) => sum + s.totalQuestions,
    0
  );

  return (
    <div
      className="mb-8 p-4 rounded-xl border"
      style={{
        background: "rgba(255,255,255,0.04)",
        borderColor: "var(--border-color)",
      }}
    >
      <h2 className="text-sm font-semibold mb-3" style={{ color: "var(--text-primary)" }}>
        Your progress
      </h2>
      <p className="text-sm mb-3" style={{ color: "var(--text-secondary)" }}>
        {totalCompleted} / {totalQuestions} questions completed across subjects
      </p>
      <div className="flex flex-wrap gap-3">
        {withContent.map((s) => {
          const completed = progress[s.slug]?.length ?? 0;
          const pct = s.totalQuestions ? Math.round((completed / s.totalQuestions) * 100) : 0;
          return (
            <a
              key={s.slug}
              href={`/subjects/${s.slug}`}
              className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition-colors"
              style={{
                borderColor: "var(--border-color)",
                color: "var(--text-primary)",
                background: "rgba(255,255,255,0.04)",
              }}
            >
              <span className="font-medium">{s.shortName}</span>
              <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                {completed}/{s.totalQuestions}
                {pct > 0 && ` (${pct}%)`}
              </span>
            </a>
          );
        })}
      </div>
    </div>
  );
}
