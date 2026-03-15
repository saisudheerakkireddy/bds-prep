/**
 * Progress store: completed question IDs per subject.
 * Key: bds-prep-progress-v1 (versioned for future migrations).
 * Value: Record<subjectSlug, string[]> — array of completed question IDs.
 * No auth: one store per device. Same shape will sync to Supabase in Phase 4.
 */

const STORAGE_KEY = "bds-prep-progress-v1";

export type ProgressData = Record<string, string[]>;

function read(): ProgressData {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as unknown;
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as ProgressData;
    }
  } catch {
    // ignore
  }
  return {};
}

function write(data: ProgressData): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {
    // ignore
  }
}

/** Get full progress (all subjects). */
export function getProgress(): ProgressData {
  return read();
}

/** Update progress with a function (e.g. merge or replace per subject). */
export function setProgress(updater: (prev: ProgressData) => ProgressData): void {
  const next = updater(read());
  write(next);
}

/** Optional callback fired after toggleQuestionCompleted; used to sync to Supabase when logged in. */
let syncCallback: ((subjectSlug: string, questionId: string, completed: boolean) => void) | null = null;

export function setProgressSyncCallback(cb: ((subjectSlug: string, questionId: string, completed: boolean) => void) | null): void {
  syncCallback = cb;
}

/**
 * Toggle a question's completed state for a subject.
 * @returns true if the question is now completed, false if now incomplete.
 */
export function toggleQuestionCompleted(
  subjectSlug: string,
  questionId: string
): boolean {
  const data = read();
  const list = data[subjectSlug] ?? [];
  const set = new Set(list);
  let nowCompleted: boolean;
  if (set.has(questionId)) {
    set.delete(questionId);
    nowCompleted = false;
  } else {
    set.add(questionId);
    nowCompleted = true;
  }
  write({
    ...data,
    [subjectSlug]: Array.from(set),
  });
  syncCallback?.(subjectSlug, questionId, nowCompleted);
  return nowCompleted;
}

/** Get the set of completed question IDs for a subject. */
export function getCompletedIds(subjectSlug: string): Set<string> {
  const data = read();
  const list = data[subjectSlug] ?? [];
  return new Set(list);
}

/** Check if a specific question is completed. */
export function isQuestionCompleted(
  subjectSlug: string,
  questionId: string
): boolean {
  return getCompletedIds(subjectSlug).has(questionId);
}
