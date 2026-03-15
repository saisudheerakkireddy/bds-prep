# Google OAuth with Supabase + Vercel (process)

Use this when you implement **Stage 2** (Gmail login + progress sync). All on **free tier** (Supabase + Vercel).

---

## 1. Google Cloud Console (OAuth client)

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project (e.g. “BDS Prep”).
3. **APIs & Services → Credentials → Create credentials → OAuth client ID**.
4. If prompted, configure **OAuth consent screen**:
   - User type: **External** (unless you use a Workspace and want Internal).
   - App name, support email, developer contact; add your email as test user if in “Testing” mode.
5. Application type: **Web application**.
6. **Authorized JavaScript origins** (add both):
   - `http://localhost:4321` (Astro dev)
   - `https://your-app.vercel.app` (replace with your Vercel URL)
7. **Authorized redirect URIs** (add both):
   - `http://localhost:4321` (or the exact redirect path Supabase shows, e.g. `http://localhost:4321/auth/callback`)
   - `https://your-app.vercel.app` (or `https://your-app.vercel.app/auth/callback` — match Supabase redirect URL)
   - Get the **exact** redirect URL from Supabase (step below) and use that.
8. Copy **Client ID** and **Client Secret**; you’ll give the secret only to Supabase (env), never to the browser.

---

## 2. Supabase (Auth + redirect URL)

1. [Supabase](https://supabase.com) → your project (or create one).
2. **Authentication → Providers → Google**:
   - Enable Google.
   - Paste **Client ID** and **Client Secret** from Google.
   - Supabase will show the **Redirect URL** to use (e.g. `https://<project-ref>.supabase.co/auth/v1/callback`). Copy it.
3. In **Google Cloud Console**, add this **exact** Supabase redirect URL under **Authorized redirect URIs**.
4. **Authentication → URL Configuration**:
   - **Site URL**: `https://your-app.vercel.app` (production) or `http://localhost:4321` (dev).
   - **Redirect URLs**: Add:
     - `http://localhost:4321/**`
     - `https://your-app.vercel.app/**`
   So Supabase allows your app’s origin and any path (e.g. `/auth/callback`).

---

## 3. Vercel (env vars)

1. Vercel → your project → **Settings → Environment Variables**.
2. Add (for Astro/Vite, often `PUBLIC_` or `VITE_` so client can read):
   - `PUBLIC_SUPABASE_URL` = `https://<project-ref>.supabase.co`
   - `PUBLIC_SUPABASE_ANON_KEY` = Supabase anon/public key (Project Settings → API).
   Do **not** put the service role key in the client.
3. Redeploy so env vars are available at build/runtime.

---

## 4. App (high level)

1. **Install**: `@supabase/supabase-js` (and optionally `@supabase/ssr` if you use server-side routes).
2. **Supabase client**: Create a client using `PUBLIC_SUPABASE_URL` and `PUBLIC_SUPABASE_ANON_KEY` (browser-safe).
3. **Sign in**: Call `supabase.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: 'https://your-app.vercel.app/auth/callback' } })`. For local dev use `redirectTo: 'http://localhost:4321/auth/callback'` or your actual callback path.
4. **Callback route**: Create a page/route that Supabase redirects to after Google sign-in (e.g. `/auth/callback`). On that route:
   - Exchange the code for a session: e.g. `supabase.auth.getSession()` or `supabase.auth.setSession()` with the code Supabase sends (see Supabase docs for “PKCE” or “implicit” flow).
   - Then redirect user to app home or dashboard.
5. **Progress**: When user is logged in, read/write progress to Supabase (e.g. `user_progress` table with `user_id` from `supabase.auth.getUser()`). When not logged in, keep using localStorage and (optionally) merge or overwrite after first login.

---

## 5. Supabase schema (user progress)

Run the migration in **Supabase Dashboard → SQL Editor** (or via Supabase CLI):

- **File**: `supabase/migrations/001_user_progress.sql`

This creates `public.user_progress` and RLS so users can only read/write their own progress.

## 6. Checklist

- [ ] Google OAuth client (Web application) with correct origins + redirect URIs (including Supabase callback URL).
- [ ] Supabase Google provider enabled; redirect URL from Supabase added in Google Console.
- [ ] Supabase URL Configuration: Site URL + Redirect URLs for local and Vercel.
- [ ] Supabase: run `001_user_progress.sql` to create table and RLS.
- [ ] Vercel env: `PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_ANON_KEY`; redeploy.
- [ ] App: sign-in with Google → redirect to `/auth/callback` → exchange code/session → redirect to app; progress syncs to Supabase when logged in; first login merges localStorage into Supabase.

---

## 7. References

- [Supabase Auth with Google](https://supabase.com/docs/guides/auth/social-login/auth-google)
- [Supabase redirect URLs](https://supabase.com/docs/guides/auth/redirect-urls)
- [Vercel env vars](https://vercel.com/docs/projects/environment-variables)
