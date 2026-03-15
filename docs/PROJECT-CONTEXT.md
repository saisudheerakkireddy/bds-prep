# BDS Prep — Project Context

## Purpose
Study-aid web app for **BDS Final Year** students (Andhra Pradesh, India) for **AP 2026** exams. Goal: high-yield revision with Q&A, mind maps, progress tracking, and later spaced repetition — so students **see progress, stay motivated**, and **don’t forget what they read**.

## Target Users
- BDS final-year students in AP
- In a hurry to complete syllabus
- Main pain: **forgetting what they read** (especially in subjects like PHD)
- Need to **prioritise** (High Yield vs all) and **see completion** to stay motivated

## Tech Stack
- **Framework**: Astro 5 + React islands (interactive components)
- **Styling**: Tailwind CSS
- **Diagrams**: Mermaid.js (client-side)
- **Hosting**: Vercel
- **Backend / Auth (later)**: Supabase (free tier) — PostgreSQL + Google OAuth
- **Stages**: (1) Local flow + features, (2) Gmail/Supabase for sync, (3) Spaced repetition

## Architecture (current)
- **Subject metadata**: `src/lib/subjects.ts` — exam schedule, slugs, paper codes
- **Content**: `src/content/subjects/<slug>.json` — questions, mind maps, resources, highYield in data
- **Subject page**: `src/pages/subjects/[slug].astro` — loads JSON, passes `questions` + `highYieldIds` to QAAccordion (ID-based filter so High Yield segregation works after hydration)
- **Progress (planned)**: localStorage first (per-device), then Supabase + Gmail for cross-device
- **Student feedback (later)**: `src/content/student-inputs.json` — structure ready; no student input flow yet

## Content Priorities
1. **Volume first**: Add ~50 Q&A per subject (three subjects: Prosthodontics, Conservative Dentistry, Oral Surgery)
2. **Then**: Structure, clarity, and source/verification
3. **Difficulty**: Binary only — High Yield vs rest (no Easy/Medium/Hard)
4. **Topic-level progress**: Track completion by topic as well as by subject

## Feature Priorities (order)
1. **Browse + filter**: All vs High Yield working correctly (fixed via `highYieldIds` prop)
2. **Progress + prioritisation**: localStorage — mark questions completed, topic-level progress, motivate with visible progress
3. **Quiz mode**: Per-subject quiz (after filter and progress are solid)
4. **Gmail + Supabase**: Sync progress across devices (after local flow is perfected)
5. **Spaced repetition**: “Review after each day(s)” — later phase

## Key Files
- Subject list & schedule: `src/lib/subjects.ts`
- Subject content: `src/content/subjects/*.json`
- Q&A UI + High Yield filter: `src/components/QAAccordion.tsx`
- Subject page: `src/pages/subjects/[slug].astro`
- Auth process (when added): `docs/AUTH-GOOGLE-OAUTH.md`
- Roadmap: `docs/ROADMAP.md`
- Student feedback schema: `src/content/student-inputs.json`

## Out of Scope (for now)
- Future batches beyond AP 2026 (later)
- Student-submitted corrections (structure in place; no UI yet)
- Difficulty levels beyond binary High Yield
- Full markdown in answers (only **bold** supported in QAAccordion)
