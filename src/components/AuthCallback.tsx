import { useEffect, useState } from "react";
import { getSupabase } from "../lib/supabase";

export default function AuthCallback() {
  const [status, setStatus] = useState<"exchanging" | "done" | "error">("exchanging");

  useEffect(() => {
    const supabase = getSupabase();
    if (!supabase) {
      setStatus("error");
      return;
    }

    const next = new URLSearchParams(window.location.search).get("next") || "/";

    // With implicit flow, tokens arrive in URL hash; client auto-detects via detectSessionInUrl.
    // With PKCE we'd exchange code - we use implicit to avoid code verifier storage issues.
    const run = async () => {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code");
      const hasHash = window.location.hash && window.location.hash.length > 1;

      if (code) {
        // PKCE flow (if ever used) - exchange code for session
        const { error } = await supabase.auth.exchangeCodeForSession(code);
        if (error) {
          console.error("Auth exchange error:", error);
          setStatus("error");
          return;
        }
      } else if (hasHash) {
        // Implicit flow - client parses hash automatically; give it a moment
        await new Promise((r) => setTimeout(r, 100));
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
          // Hash present but no session - may have failed
          setStatus("error");
          return;
        }
        // Clear hash from URL before redirect (avoid token in history)
        window.history.replaceState(null, "", window.location.pathname + window.location.search);
      }

      setStatus("done");
      window.location.replace(next);
    };

    run();
  }, []);

  if (status === "error") {
    return (
      <p style={{ color: "var(--text-secondary)" }}>
        Sign-in could not be completed. <a href="/" style={{ color: "var(--accent-1)" }}>Return home</a>.
      </p>
    );
  }

  return (
    <p style={{ color: "var(--text-secondary)" }}>
      Signing you in…
    </p>
  );
}
