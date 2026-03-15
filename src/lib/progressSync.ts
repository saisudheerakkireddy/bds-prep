/**
 * Progress sync with Supabase when user is logged in.
 * - On first login: merge localStorage progress into Supabase (upsert), then fetch and hydrate localStorage.
 * - On toggle: push update to Supabase (upsert completed, delete when unmarked).
 * Uses same shape as progress.ts: Record<subjectSlug, questionId[]>.
 */

import { getSupabase } from "./supabase";
import { getProgress, setProgress } from "./progress";

const MERGED_FLAG_PREFIX = "bds-prep-progress-merged-";

export function getMergedFlagKey(userId: string): string {
  return `${MERGED_FLAG_PREFIX}${userId}`;
}

export function hasMergedForUser(userId: string): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(getMergedFlagKey(userId)) === "1";
}

export function setMergedForUser(userId: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(getMergedFlagKey(userId), "1");
}

/**
 * Merge local progress into Supabase (upsert each completed question).
 * Call once per user on first login.
 */
export async function mergeLocalToSupabase(userId: string): Promise<void> {
  const supabase = getSupabase();
  if (!supabase) return;

  const local = getProgress();
  const now = new Date().toISOString();
  const rows: { user_id: string; subject_slug: string; question_id: string; completed_at: string }[] = [];
  for (const [subjectSlug, ids] of Object.entries(local)) {
    if (ids && ids.length > 0) {
      for (const questionId of ids) {
        rows.push({
          user_id: userId,
          subject_slug: subjectSlug,
          question_id: questionId,
          completed_at: now,
        });
      }
    }
  }

  if (rows.length === 0) return;

  const { error } = await supabase.from("user_progress").upsert(rows, {
    onConflict: "user_id,subject_slug,question_id",
  });

  if (error) {
    console.error("Progress merge to Supabase failed:", error);
  }
}

/**
 * Fetch user progress from Supabase and write to localStorage (replacing local for that user).
 */
export async function fetchAndApplySupabaseProgress(userId: string): Promise<void> {
  const supabase = getSupabase();
  if (!supabase) return;

  const { data, error } = await supabase
    .from("user_progress")
    .select("subject_slug, question_id")
    .eq("user_id", userId);

  if (error) {
    console.error("Fetch progress from Supabase failed:", error);
    return;
  }

  const next: Record<string, string[]> = {};
  for (const row of data ?? []) {
    const slug = row.subject_slug as string;
    const id = row.question_id as string;
    if (!next[slug]) next[slug] = [];
    next[slug].push(id);
  }

  setProgress(() => next);
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("bds-prep-progress-synced"));
  }
}

/**
 * Push a single toggle to Supabase (upsert when completed, delete when unmarked).
 */
export async function pushProgressToSupabase(
  userId: string,
  subjectSlug: string,
  questionId: string,
  completed: boolean
): Promise<void> {
  const supabase = getSupabase();
  if (!supabase) return;

  if (completed) {
    await supabase.from("user_progress").upsert(
      {
        user_id: userId,
        subject_slug: subjectSlug,
        question_id: questionId,
        completed_at: new Date().toISOString(),
      },
      { onConflict: "user_id,subject_slug,question_id" }
    );
  } else {
    await supabase
      .from("user_progress")
      .delete()
      .eq("user_id", userId)
      .eq("subject_slug", subjectSlug)
      .eq("question_id", questionId);
  }
}
