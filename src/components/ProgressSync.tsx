import { useEffect, useRef } from "react";
import { getSupabase } from "../lib/supabase";
import { setProgressSyncCallback } from "../lib/progress";
import {
  hasMergedForUser,
  setMergedForUser,
  mergeLocalToSupabase,
  fetchAndApplySupabaseProgress,
  pushProgressToSupabase,
} from "../lib/progressSync";

/**
 * Runs when user is logged in: merge local progress to Supabase on first login,
 * then fetch and hydrate localStorage. Registers callback so toggleQuestionCompleted
 * also pushes to Supabase. Renders nothing.
 */
export default function ProgressSync() {
  const ranMergeRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    const supabase = getSupabase();
    if (!supabase) return;

    const runSync = async (userId: string) => {
      if (!hasMergedForUser(userId) && !ranMergeRef.current.has(userId)) {
        ranMergeRef.current.add(userId);
        await mergeLocalToSupabase(userId);
        setMergedForUser(userId);
      }
      await fetchAndApplySupabaseProgress(userId);
    };

    const registerCallback = (userId: string) => {
      setProgressSyncCallback((subjectSlug, questionId, completed) => {
        pushProgressToSupabase(userId, subjectSlug, questionId, completed);
      });
    };

    const unregisterCallback = () => {
      setProgressSyncCallback(null);
    };

    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user?.id) {
        runSync(session.user.id);
        registerCallback(session.user.id);
      } else {
        unregisterCallback();
      }
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user?.id) {
        runSync(session.user.id);
        registerCallback(session.user.id);
      } else {
        ranMergeRef.current.clear();
        unregisterCallback();
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  return null;
}

