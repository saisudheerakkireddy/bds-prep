/**
 * Browser Supabase client for auth and progress sync.
 * Uses PUBLIC_SUPABASE_URL and PUBLIC_SUPABASE_ANON_KEY (Vercel/env).
 * Safe for client-only; returns null if env not set (auth disabled).
 */

import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null = null;

export function getSupabase(): SupabaseClient | null {
  if (typeof window === "undefined") return null;
  const url = import.meta.env.PUBLIC_SUPABASE_URL as string | undefined;
  const key = import.meta.env.PUBLIC_SUPABASE_ANON_KEY as string | undefined;
  if (!url || !key) return null;
  if (!client) {
    client = createBrowserClient(url, key);
  }
  return client;
}
