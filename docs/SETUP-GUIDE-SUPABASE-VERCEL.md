# BDS Prep: Step-by-Step Setup Guide

Complete guide to push the app to GitHub, deploy on Vercel, and enable Google sign-in + progress sync with Supabase.

---

## Overview

1. **GitHub** — Push your code and create a repository
2. **Google Cloud Console** — Create OAuth 2.0 credentials for "Sign in with Google"
3. **Supabase** — Create project, enable Google provider, run migration
4. **Vercel** — Deploy from GitHub, add environment variables
5. **Optional** — Add remaining Conservative Dentistry questions

---

## Step 1: Push to GitHub

### 1.1 Initialize Git (if not already)

```bash
cd /path/to/BDS/bds-prep
git init
git add .
git commit -m "Initial commit: BDS Prep app with Supabase auth"
```

### 1.2 Create and push to GitHub

1. Go to [github.com](https://github.com) → **New repository**
2. Name: `bds-prep` (or your choice)
3. Visibility: **Public** or **Private**
4. **Do not** add README, .gitignore, or license (you already have code)
5. Click **Create repository**
6. Run the commands shown on the empty repo page, e.g.:

```bash
git remote add origin https://github.com/YOUR_USERNAME/bds-prep.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## Step 2: Google Cloud Console (OAuth 2.0)

### 2.1 Create or select a project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Use the project dropdown at the top
3. Click **New Project** → Name: `BDS Prep` → **Create**
4. Or select an existing project

### 2.2 Configure OAuth consent screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. User type: **External** → **Create**
3. Fill in:
   - **App name**: BDS Prep
   - **User support email**: your email
   - **Developer contact**: your email
4. Click **Save and Continue** through the scopes and test users screens (add your email as test user if in "Testing" mode)

### 2.3 Create OAuth client ID

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `BDS Prep Web`
5. **Authorized JavaScript origins** — add:

   | Environment | URL |
   |-------------|-----|
   | Local dev | `http://localhost:4321` |
   | Production | `https://YOUR-VERCEL-APP.vercel.app` |

   Replace `YOUR-VERCEL-APP` with your actual Vercel deployment URL (e.g. `bds-prep-abc123`).

6. **Authorized redirect URIs** — add:

   | Use | URL |
   |-----|-----|
   | Supabase callback | `https://YOUR-PROJECT-REF.supabase.co/auth/v1/callback` |

   You will get the exact Supabase URL in **Step 3.2**. Come back here and add it after creating your Supabase project.

7. Click **Create**
8. Copy and save:
   - **Client ID** (e.g. `123456789-xxx.apps.googleusercontent.com`)
   - **Client Secret** (e.g. `GOCSPX-xxxx`)

   Keep the Client Secret private; you will add it only in Supabase, never in your code or Vercel.

---

## Step 3: Supabase

### 3.1 Create a project

1. Go to [supabase.com](https://supabase.com) → **Start your project**
2. Sign in (GitHub is fine)
3. **New project** → Name: `bds-prep` (or your choice)
4. Choose a database password and region
5. Click **Create new project** — wait for it to be ready

### 3.2 Enable Google provider

1. In your Supabase project: **Authentication** → **Providers**
2. Find **Google** → turn it **ON**
3. Paste:
   - **Client ID** (from Google Cloud)
   - **Client Secret** (from Google Cloud)
4. Click **Save**
5. **Copy the Redirect URL** shown (e.g. `https://abcdefgh.supabase.co/auth/v1/callback`)
6. Go back to **Google Cloud Console** → Credentials → your OAuth client → edit → add this URL to **Authorized redirect URIs** → Save

### 3.3 Configure auth URLs

1. In Supabase: **Authentication** → **URL Configuration**
2. Set:

   | Setting | Value |
   |---------|-------|
   | **Site URL** | `https://YOUR-VERCEL-APP.vercel.app` (your production URL) |
   | **Redirect URLs** | Add both: |
   | | `http://localhost:4321/**` |
   | | `https://YOUR-VERCEL-APP.vercel.app/**` |

3. Click **Save**

### 3.4 Run the migration (user progress table)

1. In Supabase: **SQL Editor** → **New query**
2. Copy the contents of `supabase/migrations/001_user_progress.sql` (or paste the SQL below)
3. Click **Run**

```sql
create table if not exists public.user_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  subject_slug text not null,
  question_id text not null,
  completed_at timestamptz not null default now(),
  primary key (user_id, subject_slug, question_id)
);

create index if not exists idx_user_progress_user_id on public.user_progress(user_id);

alter table public.user_progress enable row level security;

create policy "Users can read own progress"
  on public.user_progress for select
  using (auth.uid() = user_id);

create policy "Users can insert own progress"
  on public.user_progress for insert
  with check (auth.uid() = user_id);

create policy "Users can update own progress"
  on public.user_progress for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "Users can delete own progress"
  on public.user_progress for delete
  using (auth.uid() = user_id);
```

4. You should see "Success. No rows returned"

### 3.5 Get API keys

1. Supabase: **Project Settings** (gear icon) → **API**
2. Copy and save:
   - **Project URL** (e.g. `https://abcdefgh.supabase.co`)
   - **anon public** key (under "Project API keys")

---

## Step 4: Vercel

### 4.1 Import project from GitHub

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project**
2. Import your `bds-prep` repository from GitHub
3. Root Directory: `bds-prep` (if the app is inside the BDS folder)
4. Framework Preset: **Astro** (usually auto-detected)
5. Click **Deploy** — first deploy will run without env vars (auth UI will not show yet)

### 4.2 Add environment variables

1. Project → **Settings** → **Environment Variables**
2. Add:

   | Name | Value | Environment |
   |------|-------|-------------|
   | `PUBLIC_SUPABASE_URL` | Your Supabase Project URL (from 3.5) | Production, Preview, Development |
   | `PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anon public key (from 3.5) | Production, Preview, Development |

3. Click **Save** for each

### 4.3 Redeploy

1. Go to **Deployments**
2. Click the **⋯** on the latest deployment → **Redeploy**
3. Or push a new commit to trigger a deploy

### 4.4 Update Google and Supabase with final URL

After the first deploy, you’ll have a URL like `https://bds-prep-xyz.vercel.app`:

1. **Google Cloud Console** → Credentials → OAuth client → add this under **Authorized JavaScript origins** and under **Authorized redirect URIs** if needed (you already have the Supabase callback; no change needed there)
2. **Supabase** → Authentication → URL Configuration → set **Site URL** and **Redirect URLs** to your real Vercel URL

---

## Step 5: Verify

1. Visit your Vercel URL — you should see the **Sign in with Google** button in the header
2. Click it → you should be redirected to Google → sign in → return to the app
3. Mark some questions as done → sign out → sign in again on another device/browser — progress should sync
4. On first login, existing localStorage progress should be merged into Supabase

---

## Optional: Add remaining Conservative Dentistry questions

The app currently has 10 Conservative Dentistry questions (con001–con010). To add more:

1. Add questions to `50_questions_eachsub/endo.json` (same shape as existing ones), or
2. Add directly to `src/content/subjects/conservative-dentistry.json`

Each question must have:

- `id` — e.g. `con011`, `con012`, …
- `topic` — display name (e.g. `"Pulp Biology and Diagnosis"`)
- `question` — the question text
- `answer` — supports `**bold**` and `\n\n` for paragraphs
- `highYield` — `true` or `false`
- `yearsAsked` — optional `[]`

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| No sign-in button | Env vars set in Vercel? Redeployed after adding them? |
| "Redirect URI mismatch" | Supabase callback URL added in Google redirect URIs? Site URL and Redirect URLs correct in Supabase? |
| "Invalid redirect URL" | Supabase URL Configuration has your Vercel URL with `/**`? |
| Progress not syncing | `user_progress` migration run in Supabase? RLS policies active? |
| Local dev auth fails | Site URL in Supabase set to `http://localhost:4321` for testing, or add `http://localhost:4321/**` to Redirect URLs |

---

## Quick reference

- **Google**: [console.cloud.google.com](https://console.cloud.google.com/) → Credentials
- **Supabase**: Project → Authentication, SQL Editor, Project Settings → API
- **Vercel**: Project → Settings → Environment Variables, Deployments
