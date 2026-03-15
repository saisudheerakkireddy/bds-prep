-- BDS Prep: user progress table + RLS
-- Run this in Supabase SQL Editor (Dashboard → SQL Editor) after creating your project.

-- Table: one row per (user, subject, question) when the question is marked completed.
create table if not exists public.user_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  subject_slug text not null,
  question_id text not null,
  completed_at timestamptz not null default now(),
  primary key (user_id, subject_slug, question_id)
);

-- Index for fetching all progress for a user.
create index if not exists idx_user_progress_user_id on public.user_progress(user_id);

-- RLS: users can only read/write their own progress.
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
