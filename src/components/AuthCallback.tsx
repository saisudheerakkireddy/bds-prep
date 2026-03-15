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

    const run = async () => {
      const params = new URLSearchParams(window.location.search);
      const code = params.get("code");
      const next = params.get("next") || "/";

      if (code) {
        const { error } = await supabase.auth.exchangeCodeForSession(code);
        if (error) {
          console.error("Auth exchange error:", error);
          setStatus("error");
          return;
        }
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
