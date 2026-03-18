/**
 * Browser Supabase client for auth and progress sync.
 * Uses PUBLIC_SUPABASE_URL and PUBLIC_SUPABASE_ANON_KEY (Vercel/env).
 * Safe for client-only; returns null if env not set (auth disabled).
 *
 * Uses flowType: 'implicit' to avoid PKCE code verifier storage issues
 * (AuthPKCECodeVerifierMissingError) when OAuth redirects back to the callback.
 * With implicit flow, tokens arrive in the URL hash; no code exchange needed.
 */

import { createClient } from "@supabase/supabase-js";
import type { SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null = null;

export function getSupabase(): SupabaseClient | null {
  if (typeof window === "undefined") return null;
  const url = import.meta.env.PUBLIC_SUPABASE_URL as string | undefined;
  const key = import.meta.env.PUBLIC_SUPABASE_ANON_KEY as string | undefined;
  if (!url || !key) return null;
  if (!client) {
    client = createClient(url, key, {
      auth: {
        flowType: "implicit",
        detectSessionInUrl: true,
        persistSession: true,
        autoRefreshToken: true,
      },
    });
  }
  return client;
}
