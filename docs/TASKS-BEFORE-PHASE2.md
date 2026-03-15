# Tasks before Phase 2 (readability, formatting, analogies)

Use this as the master task list. Phase 2 (Quiz) starts after these are done.

---

## Confirmed: What Phase 2 actually is

From the phased plan, **Phase 2 = Quiz mode (per subject)**:

- **Entry**: "Start quiz" on subject page → `/subjects/[slug]/quiz`.
- **Options**: All vs High Yield (same as browse); optional "Only not completed"; number of questions (e.g. 5 / 10 / 20 or All).
- **Flow**: Random N questions without replacement → one question at a time → "Show answer" → reveal answer + analogy → "Next" or "Mark done & Next" (progress store).
- **End**: "You answered X. Y marked as done." (No score in v1.)
- **Build**: New page `quiz.astro`, new component `QuizSession.tsx`, reuse `formatAnswer` and progress module; link from subject page.

---

## Task 1: Answer readability (pastel or white)

**Goal**: Answers are easy to read; use a pastel or white that complements the dark theme.

**Details**:
- Current answer text uses `var(--text-secondary)` (#8b949e). On dark bg this can feel flat.
- Use a dedicated color that is either soft white or a complementary pastel so the answer block stands out and remains readable (good contrast, not harsh).
- Apply in QAAccordion answer block (and later in Quiz so it stays consistent).

**Steelman**: Pastel might reduce contrast vs pure white. Mitigation: pick a value that meets readability (e.g. #e2e8f0 or #f0f6fc) and keep contrast ratio sufficient.

**Status**: [ ] Not started → [x] Done (add `--answer-text` in CSS, use in answer div).

---

## Task 2: Answer spacing and structure (not one block)

**Goal**: Answers don’t appear as one solid HTML block; add relevant spacing and line breaks so they’re scannable.

**Details**:
- Support paragraph breaks (e.g. double newline `\n\n` in content = new paragraph).
- Where answers use numbered points “(1) … (2) …”, break so each point can start on a new line or have space before it.
- Keep **bold** for key terms (already supported via `**…**` → `<strong>`); ensure formatting is preserved after adding breaks.

**Steelman**: Auto-inserting breaks might misplace them in some answers. Mitigation: (a) prefer explicit `\n\n` in content where we control it; (b) optional client-side split on “ (1) ” “ (2) ” etc. for numbered lists so we don’t break mid-sentence.

**Status**: [ ] Not started → [x] Done (formatAnswer or wrapper respects `\n\n` and optional numbered-point line breaks).

---

## Task 3: Bold where needed

**Goal**: Important terms in answers are bold for quick scanning.

**Details**:
- Already implemented: `**text**` in answer string → `<strong>` in `formatAnswer`. No code change required.
- Content-side: ensure key terms in JSON answers use `**term**` where appropriate (can be done incrementally; existing prostho content already uses ** in many places).

**Status**: [x] Already done in code; content can be enriched over time.

---

## Task 4: Harry Potter analogies (with clear explanation)

**Goal**: Small analogies that use Harry Potter as a memory hook, written so that **even without HP knowledge** the topic is clear. Include a brief explanation of the HP reference and characters so everyone gets it.

**Details**:
- Add or use optional `analogy` field on questions. Format: (1) One–two sentences that explain the **dental/topic concept** in simple terms. (2) Then: “In Harry Potter, [character/situation] works like this: [short explanation].” So the analogy stands alone.
- Example pattern: “**Topic**: [simple explanation]. In Harry Potter, [X] is like this: [one line]. So just as [X], in dentistry we have [concept].”
- Start with **1–2 exemplar analogies** (e.g. phd001 centric relation, phd004 balanced occlusion); document the pattern for adding more later.

**Steelman**:
- “Not everyone likes Harry Potter” → Analogies are optional (show only when `analogy` is present); label clearly (“Remember it like this”); no HP jargon without explanation.
- “Too much work for 50 questions” → Do 2–3 exemplars now; document pattern; rest added incrementally.
- “Might date the app” → Optional content; can be hidden or removed later without breaking core Q&A.

**Status**: [x] Done. HP analogies removed; replaced with short, crisp narratives.

**"Remember it like this" pattern** (for future content):
- One vivid, everyday or clinical image (e.g. GPS home point, both feet on the ground).
- Weave in **exam keywords** (reproducible, recordable, bilateral contact, etc.) so recall in the hall is easier.
- Keep it to 1–2 sentences. No pop-culture references unless they add real value; prefer universal imagery.

---

## Task 5: Phase 2 quiz implementation plan (written doc)

**Goal**: Single document that confirms Phase 2 scope and gives a step-by-step implementation plan (routes, components, props, progress integration, verification).

**Details**:
- Confirm: entry, options (All / High Yield / Only not completed, N questions), flow (show answer → Next / Mark done & Next), end screen.
- List: new files (`quiz.astro`, `QuizSession.tsx`), props and state, reuse of `formatAnswer` and progress module.
- Include: verification checklist (same as plan Observe) so we can tick before calling Phase 2 done.

**Status**: [ ] Not started → [x] Done (create `docs/PHASE2-QUIZ-PLAN.md`).

---

## Execution order

1. Task 1: Answer readability (CSS + QAAccordion).
2. Task 2: Answer spacing (formatAnswer or wrapper).
3. Task 3: Bold — no change; note in doc.
4. Task 4: Add 2 HP analogy exemplars + pattern note.
5. Task 5: Write Phase 2 quiz plan doc.

After all are done, we’re ready to implement Phase 2 (Quiz) according to the new plan doc.
