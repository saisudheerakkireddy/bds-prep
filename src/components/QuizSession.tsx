import { useState, useEffect } from "react";
import { formatAnswer, formatParagraph } from "../lib/formatAnswer";
import { getCompletedIds, toggleQuestionCompleted } from "../lib/progress";

export interface QuizQuestion {
  id: string;
  topic: string;
  question: string;
  answer: string;
  analogy?: string;
  highYield: boolean;
}

interface QuizSessionProps {
  questions: QuizQuestion[];
  subjectSlug: string;
  subjectName: string;
}

const PAGE_SIZE = 10;

export default function QuizSession({
  questions,
  subjectSlug,
  subjectName,
}: QuizSessionProps) {
  const total = questions.length;
  const totalPages = total <= 0 ? 0 : Math.ceil(total / PAGE_SIZE);

  const [currentPage, setCurrentPage] = useState(0);
  const [indexInPage, setIndexInPage] = useState(0);
  const [answerVisible, setAnswerVisible] = useState(false);
  const [completedIds, setCompletedIds] = useState<Set<string>>(new Set());

  const displayIndex = currentPage * PAGE_SIZE + indexInPage;
  const q = questions[displayIndex];
  const currentNumber = displayIndex + 1;

  const startForPage = currentPage * PAGE_SIZE;
  const endForPage = Math.min(startForPage + PAGE_SIZE, total);
  const questionsOnPage = questions.slice(startForPage, endForPage);

  useEffect(() => {
    setCompletedIds(getCompletedIds(subjectSlug));
  }, [subjectSlug]);

  useEffect(() => {
    const handler = () => setCompletedIds(getCompletedIds(subjectSlug));
    window.addEventListener("storage", handler);
    window.addEventListener("bds-prep-progress-synced", handler);
    return () => {
      window.removeEventListener("storage", handler);
      window.removeEventListener("bds-prep-progress-synced", handler);
    };
  }, [subjectSlug]);

  useEffect(() => {
    setAnswerVisible(false);
  }, [displayIndex]);

  const handleReveal = () => {
    setAnswerVisible((v) => !v);
  };

  const goToPrev = () => {
    if (displayIndex <= 0) return;
    if (indexInPage > 0) {
      setIndexInPage((i) => i - 1);
    } else {
      setCurrentPage((p) => p - 1);
      setIndexInPage(PAGE_SIZE - 1);
    }
  };

  const goToNext = () => {
    if (displayIndex >= total - 1) return;
    if (indexInPage < PAGE_SIZE - 1 && displayIndex + 1 < endForPage) {
      setIndexInPage((i) => i + 1);
    } else {
      setCurrentPage((p) => p + 1);
      setIndexInPage(0);
    }
  };

  const handleMarkDoneAndNext = () => {
    if (q) {
      const nowCompleted = toggleQuestionCompleted(subjectSlug, q.id);
      setCompletedIds((prev) => {
        const next = new Set(prev);
        if (nowCompleted) next.add(q.id);
        else next.delete(q.id);
        return next;
      });
    }
    goToNext();
  };

  const goToStep = (globalIndex: number) => {
    if (globalIndex < 0 || globalIndex >= total) return;
    const page = Math.floor(globalIndex / PAGE_SIZE);
    const inPage = globalIndex % PAGE_SIZE;
    setCurrentPage(page);
    setIndexInPage(inPage);
  };

  const isCompleted = q ? completedIds.has(q.id) : false;
  const isFirst = displayIndex === 0;
  const isLast = displayIndex === total - 1;

  if (total === 0) {
    return (
      <div className="quiz-empty" style={{ color: "var(--text-secondary)" }}>
        No questions available for this quiz.
      </div>
    );
  }

  return (
    <div className="quiz-session">
      <aside className="quiz-stepper" aria-label="Question progress">
        <p className="quiz-stepper-title">
          Question {currentNumber} of {total}
        </p>
        <div className="quiz-stepper-pagination">
          {totalPages > 1 && (
            <div className="quiz-stepper-page-nav">
              <button
                type="button"
                className="quiz-stepper-page-btn"
                onClick={() => goToStep((currentPage - 1) * PAGE_SIZE)}
                disabled={currentPage === 0}
                aria-label="Previous page"
              >
                ‹
              </button>
              <span className="quiz-stepper-page-label">
                Page {currentPage + 1} of {totalPages}
              </span>
              <button
                type="button"
                className="quiz-stepper-page-btn"
                onClick={() => goToStep(Math.min((currentPage + 1) * PAGE_SIZE, total - 1))}
                disabled={currentPage >= totalPages - 1}
                aria-label="Next page"
              >
                ›
              </button>
            </div>
          )}
        </div>
        <nav className="quiz-stepper-nav" role="tablist" aria-label="Questions">
          {questionsOnPage.map((question, i) => {
            const globalIdx = startForPage + i;
            return (
              <button
                key={question.id}
                type="button"
                className={`quiz-stepper-btn ${globalIdx === displayIndex ? "quiz-stepper-btn--current" : ""} ${completedIds.has(question.id) ? "quiz-stepper-btn--done" : ""}`}
                onClick={() => goToStep(globalIdx)}
                role="tab"
                aria-selected={globalIdx === displayIndex}
                aria-label={`Question ${globalIdx + 1}${completedIds.has(question.id) ? ", completed" : ""}`}
              >
                <span className="quiz-stepper-num">{globalIdx + 1}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="quiz-main">
        <div className="quiz-card quiz-card--premium">
          <div className="quiz-card__meta">
            <span className="quiz-card__topic">{q.topic}</span>
            {q.highYield && <span className="quiz-card__hy">High yield</span>}
          </div>
          <h2 className="quiz-card__question">{q.question}</h2>
          <button
            type="button"
            className="quiz-card__reveal"
            onClick={handleReveal}
            aria-expanded={answerVisible}
            aria-controls="quiz-answer"
          >
            {answerVisible ? "Hide answer" : "Show answer"}
          </button>
          {answerVisible && (
            <div className="quiz-card__answer" id="quiz-answer">
              <div className="quiz-card__answer-text" style={{ color: "var(--answer-text)" }}>
                {formatAnswer(q.answer)}
              </div>
              {q.analogy && (
                <div className="quiz-card__analogy">
                  <p className="quiz-card__analogy-label">Remember it like this</p>
                  <div style={{ color: "var(--answer-text)" }}>
                    {formatParagraph(q.analogy, "analogy")}
                  </div>
                </div>
              )}
            </div>
          )}
          <div className="quiz-card__actions">
            {!isFirst && (
              <button
                type="button"
                className="quiz-card__btn quiz-card__btn--secondary"
                onClick={goToPrev}
              >
                Previous
              </button>
            )}
            {!isLast ? (
              <>
                <button
                  type="button"
                  className="quiz-card__btn quiz-card__btn--secondary"
                  onClick={goToNext}
                >
                  Next
                </button>
                <button
                  type="button"
                  className="quiz-card__btn quiz-card__btn--primary"
                  onClick={handleMarkDoneAndNext}
                >
                  {isCompleted ? "Undo done & Next" : "Mark done & Next"}
                </button>
              </>
            ) : (
              <button
                type="button"
                className="quiz-card__btn quiz-card__btn--primary"
                onClick={() => {
                  if (!q) return;
                  toggleQuestionCompleted(subjectSlug, q.id);
                  setCompletedIds(getCompletedIds(subjectSlug));
                }}
              >
                {isCompleted ? "Undo done" : "Mark done"}
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
