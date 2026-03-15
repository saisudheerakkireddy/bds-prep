import { useState, useEffect } from "react";
import { getSupabase } from "../lib/supabase";
import type { User } from "@supabase/supabase-js";

export default function AuthHeader() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const supabase = getSupabase();
    if (!supabase) {
      setLoading(false);
      return;
    }

    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleSignIn = async () => {
    const supabase = getSupabase();
    if (!supabase) return;
    const redirectTo = `${window.location.origin}/auth/callback`;
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo },
    });
  };

  const handleSignOut = async () => {
    const supabase = getSupabase();
    if (!supabase) return;
    await supabase.auth.signOut();
  };

  if (loading || !getSupabase()) {
    return null;
  }

  if (user) {
    return (
      <div className="flex items-center gap-2">
        <span
          className="hidden sm:inline text-sm truncate max-w-[120px]"
          style={{ color: "var(--text-secondary)" }}
          title={user.email ?? undefined}
        >
          {user.email}
        </span>
        <button
          type="button"
          onClick={handleSignOut}
          className="px-3 py-2 text-sm font-medium rounded-lg transition-colors border border-[var(--border-color)] hover:bg-[rgba(255,255,255,0.06)]"
          style={{ color: "var(--text-secondary)" }}
        >
          Sign out
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={handleSignIn}
      className="px-3 py-2 text-sm font-medium rounded-lg transition-colors"
      style={{
        background: "var(--accent-premium)",
        color: "var(--bg-color)",
      }}
    >
      Sign in with Google
    </button>
  );
}
