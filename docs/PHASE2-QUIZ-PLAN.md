# Phase 2 — Quiz mode implementation plan

This document confirms the Phase 2 scope and gives a step-by-step implementation plan. Use it when building the quiz feature.

---

## What Phase 2 is (confirmed)

**Goal**: Per-subject quiz that reuses the same question set and the same progress store as browse. Students can “test themselves,” see answers after each question, and mark done from the quiz (completions persist and show on the subject page and home).

**Out of scope for v1**: Scoring, timers, history of attempts, or auth. Focus: recall + mark done + optional “not completed” / high-yield filters.

---

## User flow (v1)

1. **Entry**: From a subject page (e.g. Prosthodontics), user clicks **“Start quiz”** → navigates to `/subjects/[slug]/quiz`.
2. **Setup (on quiz page)**:
   - **Filter**: “All” or “High Yield” (same meaning as browse).
   - **Optional**: “Only not completed” (questions not yet in progress store for this subject).
   - **Count**: e.g. 5 / 10 / 20 or “All” (filtered).
3. **Session**: N questions drawn at random without replacement. One question at a time.
   - Show question text (and topic badge, high-yield badge if applicable).
   - User taps **“Show answer”** → reveal answer (and analogy if present); reuse same styling as QAAccordion (readability color, spacing, bold).
   - Then **“Next”** (just advance) or **“Mark done & Next”** (call `toggleQuestionCompleted(subjectSlug, q.id)` then advance).
4. **End**: When all N are done, show a short summary: “You answered X. Y marked as done.” (X = N, Y = number they marked done in this session.) Link back to subject page (or “Start again” if desired).

---

## Technical plan

### 1. New route

- **File**: `src/pages/subjects/[slug]/quiz.astro`
- **Static paths**: Same as subject page (reuse `getStaticPaths` from subjects or duplicate for `quiz`).
- **Props**: Load same subject + content as `[slug].astro` (subject, questions, highYieldIds). Pass to a single React island that handles setup + session + end.

### 2. New component: `QuizSession`

- **File**: `src/components/QuizSession.tsx`
- **Props**:
  - `questions`, `highYieldIds`, `subjectSlug` (same as QAAccordion).
  - Optional `filterNotDone: boolean` (default false): if true, on mount read `getCompletedIds(subjectSlug)` and filter out completed IDs from the pool before applying All/High Yield and drawing N.
- **State**:
  - `step`: `"setup"` | `"session"` | `"end"`.
  - Setup: `filter: "all" | "high-yield"`, `onlyNotDone: boolean`, `count: number` (5 | 10 | 20 | all).
  - Session: `questionOrder: string[]` (question IDs in display order), `currentIndex: number`, `showAnswer: boolean`, `completedDuringQuiz: Set<string>` (IDs marked done this run, for end summary).
- **Behavior**:
  - **Setup**: User picks filter, optional “Only not completed,” and count. On “Start,” compute pool (filter by high-yield if needed, by not-done if needed), shuffle, take first `count` (or all), set `questionOrder`, set `step = "session"`, `currentIndex = 0`, `showAnswer = false`.
  - **Session**: Render current question; “Show answer” sets `showAnswer = true` and renders answer (and analogy) using the same `formatAnswer` + styling as QAAccordion. “Next” advances index (and resets showAnswer for next). “Mark done & Next” calls `toggleQuestionCompleted(subjectSlug, q.id)`, adds id to `completedDuringQuiz`, then advances.
  - **End**: When `currentIndex >= questionOrder.length`, set `step = "end"`. Show “You answered X. Y marked as done.” and a link back to `/subjects/${subjectSlug}`.

### 3. Reuse and consistency

- **formatAnswer**: Export from QAAccordion (or move to a shared util e.g. `src/lib/formatAnswer.ts`) and use in QuizSession for answer + analogy so spacing, bold, and readability color match.
- **Progress**: Use existing `toggleQuestionCompleted`, `getCompletedIds` from `src/lib/progress.ts`. No new store.
- **Styling**: Use same `--answer-text` and paragraph spacing in quiz answer block as in QAAccordion.

### 4. Subject page link

- In `src/pages/subjects/[slug].astro`, add a prominent button or link: **“Start quiz”** → `/subjects/${subject.slug}/quiz`. Place it near the Q&A section (e.g. above or beside the filter buttons) or in the subject header.

---

## Verification checklist (before calling Phase 2 done)

- [ ] From subject page, “Start quiz” goes to `/subjects/[slug]/quiz` and page loads with same subject.
- [ ] Setup: Choosing “High Yield” and 5 questions starts a session with exactly 5 high-yield questions, no duplicates.
- [ ] Setup: “Only not completed” excludes questions already in progress for this subject (test by marking some done in browse, then starting quiz with this option).
- [ ] Session: “Show answer” reveals answer (and analogy if present) with same readability and spacing as browse.
- [ ] Session: “Mark done & Next” marks the question in the progress store; after quiz, return to subject page and that question shows as completed.
- [ ] End: “You answered X. Y marked as done.” shows correct X and Y; link back to subject works.
- [ ] No console errors; works on a subject that has 0 high-yield (or 0 not-done) without crashing.

---

## Dependencies

- Phase 1 complete (progress store, subjectSlug, QAAccordion with filters and mark done).
- Shared `formatAnswer` (or inlined in QuizSession) and `--answer-text` styling already used in browse.

---

## Next after Phase 2

Phase 3 (content volume) and Phase 4 (Gmail + Supabase sync) can follow per the main phased plan. Quiz does not depend on auth; progress remains localStorage until Phase 4.
