import { useState, useId, useEffect } from "react";
import { getCompletedIds, toggleQuestionCompleted } from "../lib/progress";
import { formatAnswer, formatParagraph } from "../lib/formatAnswer";

interface QAAccordionProps {
  questions: {
    id: string;
    question: string;
    answer: string;
    analogy?: string;
    highYield: boolean;
    topic: string;
    yearsAsked?: string[];
  }[];
  /** High-yield question IDs — used for filtering so segregation works after hydration. */
  highYieldIds?: string[];
  /** Subject slug for progress (Mark done). When provided, progress UI is shown. */
  subjectSlug?: string;
}

/** Normalize highYield using explicit ID set so filter works after Astro hydration. */
function getNormalizedQuestions(
  questions: QAAccordionProps["questions"],
  highYieldIds: string[]
) {
  const idSet = new Set(highYieldIds);
  return questions.map((q) => ({
    ...q,
    highYield: idSet.has(q.id) || q.highYield === true || q.highYield === "true",
  }));
}

/**
 * Interleave questions by topic so the list shows a mix (not 15 from one topic).
 * Groups by topic, then takes round-robin: first of each topic, then second of each, etc.
 */
function interleaveByTopic<T extends { topic: string }>(questions: T[]): T[] {
  const byTopic = new Map<string, T[]>();
  for (const q of questions) {
    const list = byTopic.get(q.topic) ?? [];
    list.push(q);
    byTopic.set(q.topic, list);
  }
  const topics = Array.from(byTopic.keys());
  const maxLen = Math.max(...Array.from(byTopic.values()).map((a) => a.length));
  const out: T[] = [];
  for (let i = 0; i < maxLen; i++) {
    for (const topic of topics) {
      const list = byTopic.get(topic)!;
      if (i < list.length) out.push(list[i]);
    }
  }
  return out;
}

export default function QAAccordion({
  questions,
  highYieldIds = [],
  subjectSlug,
}: QAAccordionProps) {
  const [openId, setOpenId] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "high-yield">("all");
  const [completedIds, setCompletedIds] = useState<Set<string>>(new Set());
  const baseId = useId();

  const normalized = getNormalizedQuestions(questions, highYieldIds);
  const highYieldCount = normalized.filter((q) => q.highYield).length;
  const filtered =
    filter === "high-yield"
      ? normalized.filter((q) => q.highYield)
      : normalized;
  // Display order: interleave by topic so user sees a mix, not one topic repeated.
  const displayList = interleaveByTopic(filtered);

  // Sync completed IDs from progress store (client-only). Refresh on storage or after Supabase sync.
  useEffect(() => {
    if (subjectSlug) {
      setCompletedIds(getCompletedIds(subjectSlug));
    }
  }, [subjectSlug]);

  useEffect(() => {
    const handler = () => {
      if (subjectSlug) setCompletedIds(getCompletedIds(subjectSlug));
    };
    window.addEventListener("storage", handler);
    window.addEventListener("bds-prep-progress-synced", handler);
    return () => {
      window.removeEventListener("storage", handler);
      window.removeEventListener("bds-prep-progress-synced", handler);
    };
  }, [subjectSlug]);

  const handleToggleDone = (questionId: string) => {
    if (!subjectSlug) return;
    const nowCompleted = toggleQuestionCompleted(subjectSlug, questionId);
    setCompletedIds((prev) => {
      const next = new Set(prev);
      if (nowCompleted) next.add(questionId);
      else next.delete(questionId);
      return next;
    });
  };

  const setFilterAndClose = (f: "all" | "high-yield") => {
    setFilter(f);
    setOpenId(null);
  };

  // Topic-level counts for summary (completed / total per topic).
  const topicCounts = (() => {
    const map = new Map<string, { completed: number; total: number }>();
    for (const q of normalized) {
      const cur = map.get(q.topic) ?? { completed: 0, total: 0 };
      cur.total += 1;
      if (completedIds.has(q.id)) cur.completed += 1;
      map.set(q.topic, cur);
    }
    return Array.from(map.entries()).map(([name, { completed, total }]) => ({
      name,
      completed,
      total,
    }));
  })();
  const totalCompleted = normalized.filter((q) => completedIds.has(q.id)).length;

  return (
    <div>
      {subjectSlug && (
        <div
          className="mb-4 p-4 rounded-xl border space-y-2"
          style={{
            background: "rgba(255,255,255,0.04)",
            borderColor: "var(--border-color)",
          }}
        >
          <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
            Progress: {totalCompleted} / {normalized.length} completed
          </p>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs" style={{ color: "var(--text-secondary)" }}>
            {topicCounts.map(({ name, completed, total }) => (
              <span key={name}>
                {name}: {completed}/{total}
              </span>
            ))}
          </div>
        </div>
      )}
      <div className="flex flex-wrap items-center gap-2 mb-4" role="group" aria-label="Filter questions">
        <button
          type="button"
          onClick={() => setFilterAndClose("all")}
          aria-pressed={filter === "all"}
          aria-label={`Show all questions (${normalized.length})`}
          className={`px-3 py-2.5 rounded-lg text-sm font-medium transition-colors min-h-[44px] ${
            filter === "all"
              ? "text-white"
              : "hover:opacity-90"
          }`}
          style={filter === "all" ? { background: "linear-gradient(90deg, var(--accent-1), var(--accent-2))" } : { background: "rgba(255,255,255,0.06)", color: "var(--text-secondary)" }}
        >
          All ({normalized.length})
        </button>
        <button
          type="button"
          onClick={() => setFilterAndClose("high-yield")}
          aria-pressed={filter === "high-yield"}
          aria-label={`Show high-yield questions only (${highYieldCount})`}
          className={`px-3 py-2.5 rounded-lg text-sm font-medium transition-colors min-h-[44px] ${
            filter === "high-yield"
              ? "text-white"
              : "hover:opacity-90"
          }`}
          style={filter === "high-yield" ? { backgroundColor: "var(--warning)" } : { background: "rgba(255,255,255,0.06)", color: "var(--text-secondary)" }}
        >
          🔥 High Yield ({highYieldCount})
        </button>
        <span className="text-xs ml-1" style={{ color: "var(--text-secondary)" }} aria-live="polite">
          Showing {displayList.length} question{displayList.length !== 1 ? "s" : ""}
        </span>
      </div>

      <div className="space-y-3" key={`qa-list-${filter}`} role="list">
        {displayList.map((q) => {
          const isOpen = openId === q.id;
          const panelId = `${baseId}-${q.id}`;
          return (
            <div
              key={q.id}
              className={`content-card overflow-hidden transition-all duration-200 ${isOpen ? "open" : ""}`.trim()}
            >
              <button
                type="button"
                onClick={() => setOpenId(isOpen ? null : q.id)}
                className="w-full text-left px-4 sm:px-5 py-4 flex items-start gap-3 min-h-[44px]"
                aria-expanded={isOpen}
                aria-controls={panelId}
                id={`${baseId}-btn-${q.id}`}
                style={{ color: "var(--text-primary)" }}
              >
                <span
                  className={`mt-0.5 text-xs transition-transform duration-200 shrink-0 ${isOpen ? "rotate-90" : ""}`}
                  style={{ color: "var(--accent-1)" }}
                  aria-hidden
                >
                  ▶
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span
                      className="text-[10px] font-medium px-2 py-0.5 rounded-full"
                      style={{ background: "rgba(255,255,255,0.08)", color: "var(--text-secondary)" }}
                    >
                      {q.topic}
                    </span>
                    {q.highYield && (
                      <span className="badge-high-yield">High Yield</span>
                    )}
                    {q.yearsAsked?.map((y) => (
                      <span key={y} className="text-[10px] font-mono opacity-70" style={{ color: "var(--text-secondary)" }}>
                        &apos;{y.slice(-2)}
                      </span>
                    ))}
                  </div>
                  <p className="text-sm sm:text-base font-medium leading-snug" style={{ color: "var(--text-primary)" }}>
                    {q.question}
                  </p>
                </div>
                {subjectSlug && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleToggleDone(q.id);
                    }}
                    className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center border transition-colors"
                    style={{
                      borderColor: completedIds.has(q.id) ? "var(--success)" : "var(--border-color)",
                      background: completedIds.has(q.id) ? "rgba(35,134,54,0.2)" : "transparent",
                      color: completedIds.has(q.id) ? "var(--success)" : "var(--text-secondary)",
                    }}
                    aria-label={completedIds.has(q.id) ? "Mark as not done" : "Mark as done"}
                    title={completedIds.has(q.id) ? "Mark as not done" : "Mark as done"}
                  >
                    {completedIds.has(q.id) ? "✓" : "○"}
                  </button>
                )}
              </button>

              {isOpen && (
                <div
                  id={panelId}
                  role="region"
                  aria-labelledby={`${baseId}-btn-${q.id}`}
                  className="px-4 sm:px-5 pb-5 pl-10 sm:pl-12 space-y-3 border-t"
                  style={{ borderColor: "var(--border-color)" }}
                >
                  <div className="text-sm leading-relaxed pt-2 answer-text" style={{ color: "var(--answer-text)" }}>
                    {formatAnswer(q.answer)}
                  </div>
                  {q.analogy && (
                    <div
                      className="rounded-lg px-4 py-3"
                      style={{ background: "rgba(210, 153, 34, 0.12)", border: "1px solid rgba(210, 153, 34, 0.25)" }}
                    >
                      <p className="text-xs font-semibold mb-1" style={{ color: "var(--accent-premium-light)" }}>
                        💡 Remember it like this
                      </p>
                      <p className="text-sm leading-relaxed" style={{ color: "var(--answer-text)" }}>{formatParagraph(q.analogy, "analogy")}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}

        {displayList.length === 0 && (
          <div className="text-center py-12 text-sm" style={{ color: "var(--text-secondary)" }}>
            No questions yet. Content coming soon!
          </div>
        )}
      </div>
    </div>
  );
}
