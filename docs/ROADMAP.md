# BDS Prep — Roadmap (Stages)

## Stage 1: Local perfection (current focus)
**Goal**: Nail flow and functionality locally before any auth.

- [x] **High Yield filter**: All vs High Yield correctly segregated (use `highYieldIds` from server so hydration doesn’t break filter)
- [ ] **Progress (localStorage)**:
  - Mark question as “completed” (e.g. checkbox or button)
  - Persist completed question IDs per subject (and optionally per topic) in localStorage
  - Show topic-level progress (e.g. “RPD: 8/12 done”) and subject-level (e.g. “22/48 High Yield done”)
- [ ] **Quiz mode**: Per-subject quiz (e.g. random N questions, show answer after each or at end)
- [ ] **Content**: Add ~50 Q&A per subject for the three priority subjects; then improve structure, clarity, and sources

**Exit**: Students can browse, filter High Yield, mark progress, and take quizzes — all without login.

---

## Stage 2: Gmail + Supabase (sync)
**Goal**: One account, progress synced across devices.

- [ ] **Supabase (free tier)**:
  - Project + PostgreSQL
  - Table(s): e.g. `user_progress(user_id, subject_slug, question_id, completed_at)` and/or topic-level summary
- [ ] **Google OAuth**:
  - Supabase Auth with “Sign in with Google”
  - Redirect URLs set for local + Vercel domain (see `docs/AUTH-GOOGLE-OAUTH.md`)
- [ ] **Vercel**:
  - Env vars: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (or `PUBLIC_` depending on Astro)
  - Deploy; add production URL to Supabase redirect allowlist
- [ ] **App**: Replace or mirror localStorage writes with Supabase; read progress from Supabase when logged in; optional “use offline/local only” for anonymous

**Exit**: Log in with Gmail once; progress syncs across devices.

---

## Stage 3: Spaced repetition (later)
**Goal**: Reduce forgetting (e.g. “review after each day(s)”).

- [ ] **Model**: Per-question “last reviewed” (and optionally “next review” date)
- [ ] **UI**: e.g. “Due for review” list or integrate into quiz/browse (prioritise items due)
- [ ] **Schedule**: Simple rule (e.g. +1 day, +3 days, +7 days) after each “completed” or “reviewed”

**Exit**: Students get reminders to re-see questions so they retain better.

---

## Scope boundaries (for now)
- **Cohort**: AP 2026 only; future batches later
- **Auth**: Gmail only (no email/password)
- **Backend**: Supabase + Vercel free tiers only
- **Student input**: JSON schema ready; no public submission flow yet
