# Phase 1 — Manual verification metrics

Use this checklist to verify Phase 1 (Progress + topic-level UI) before moving to Phase 2. Each item is a concrete, quantifiable check you can perform in the app.

---

## Implementation status (code)

| Area | Implemented | Notes |
|------|-------------|--------|
| Question list + filter (All / High Yield) | **100%** | Interleaved by topic, “Showing X questions” label, filter drives list. |
| Progress (Mark done, persistence) | **100%** | `progress.ts` (localStorage), toggle per question, topic + subject counts. |
| Home progress block | **100%** | `HomeProgress` island, per-subject chips, links to subject pages. |
| Edge cases (empty High Yield, expand+mark, multi-topic) | **100%** | Same store and UI support these; verify manually. |

**Overall Phase 1 code: 100%.** All features are implemented. What’s left is **manual verification** (tick the boxes below as you test). After that, the next step is **Phase 2 (Quiz mode)**.

---

## 1. Question list and filter

| # | Metric | How to check | Pass criteria | Status |
|---|--------|----------------|----------------|--------|
| 1.1 | Total question count | Open **Prosthodontics** subject page. Read the **All** button and the progress line. | **All (50)** and **Progress: 0 / 50 completed**. (If you ingest a different subject/count, adjust the expected number.) | ✓ Implemented |
| 1.2 | Topic mix in list (no single-topic run) | With **All (50)** selected, look at the first 6–8 question cards (without scrolling). Note the **topic** label on each card. | You see **more than one topic** in the first 6–8 cards (e.g. Complete Denture, RPD, FPD, Occlusion, etc.). Not all 6 from “Complete Denture Prosthodontics” only. | ✓ Implemented |
| 1.3 | “Showing” count matches filter | With **All** selected, read the text next to the filter buttons. Then click **High Yield**. Read the “Showing” text again. | **All**: “Showing 50 questions”. **High Yield**: “Showing X questions” where X equals the number in the **High Yield (X)** button (e.g. 23). | ✓ Implemented |
| 1.4 | High Yield filter changes the list | Click **High Yield**. Scroll the list and spot-check topic labels and question text. Then click **All** again. | List content and length change when switching between All and High Yield. High Yield list has only questions that show the “High Yield” badge. | ✓ Implemented |
| 1.5 | No duplicate questions | With **All (50)** selected, scroll the full list and mentally or physically note question titles. | Each question text appears **once**. No repeated identical question in the list. | ✓ Implemented |
| 1.6 | Topic breakdown sums to total | On the Prosthodontics page, read the progress section: “Complete Denture: 0/15”, “RPD: 0/10”, etc. | Sum of the **second number** in each topic (e.g. 15+10+12+5+3+5) = **50** (or the total you expect). | ✓ Implemented |

---

## 2. Progress (Mark done) and persistence

| # | Metric | How to check | Pass criteria | Status |
|---|--------|----------------|----------------|--------|
| 2.1 | Mark one question done | Click the **○** on any question card to mark it done. | The control turns to **✓** and the card styling updates (e.g. green border/background). | ✓ Implemented |
| 2.2 | Progress numbers update | After marking one question done, read the progress line and the topic breakdown. | **Progress: 1 / 50 completed**. The topic that question belongs to shows **1/15** (or 1/10, etc.) instead of 0/X. | ✓ Implemented |
| 2.3 | Persistence after refresh | Refresh the page (F5 or reload). | **Progress: 1 / 50 completed** (or whatever you had) is unchanged. The same question still shows **✓**. | ✓ Implemented |
| 2.4 | Mark done and High Yield | Mark 2–3 questions done. Switch to **High Yield**. Check if any of the completed questions are in the High Yield list. | If a completed question is high-yield, it still shows **✓** in the High Yield view. Progress counts do not reset when switching filters. | ✓ Implemented |
| 2.5 | Unmark (toggle off) | Click **✓** on a completed question to unmark. | It changes back to **○**. Progress line and topic breakdown decrease by 1. | ✓ Implemented |
| 2.6 | Clear storage resets progress | In DevTools → Application → Local Storage, delete the key **bds-prep-progress-v1** (or clear all for localhost). Reload the page. | **Progress: 0 / 50 completed** and all topic counts are 0/X. All cards show **○**. | ✓ Implemented |

---

## 3. Home page progress block

| # | Metric | How to check | Pass criteria | Status |
|---|--------|----------------|----------------|--------|
| 3.1 | Progress block visible | Go to **Home**. Look for the “Your progress” section above the schedule. | A block shows **Your progress** and at least one subject with “X / Y” (e.g. Prostho 0/50). | ✓ Implemented |
| 3.2 | Total and per-subject counts | Read the line “X / Y questions completed across subjects” and each subject chip (e.g. “Prostho 0/50”). | Total completed = sum of completed counts for each subject. For 0 done, “0 / 50” (or total questions) and “Prostho 0/50”. | ✓ Implemented |
| 3.3 | Home updates after marking done | Open Prosthodontics, mark 2 questions done, then go back to **Home**. | “Your progress” shows **2 / 50** (or your total) and **Prostho 2/50** (or with %). | ✓ Implemented |
| 3.4 | Subject link from progress | Click the **Prostho** (or subject) chip in “Your progress”. | You navigate to that subject’s page; progress there matches (e.g. 2/50). | ✓ Implemented |

---

## 4. Edge cases and stability

| # | Metric | How to check | Pass criteria | Status |
|---|--------|----------------|----------------|--------|
| 4.1 | High Yield with 0 questions | Use a subject that has no high-yield questions (if any). Select **High Yield**. | “Showing 0 questions” and the empty-state message (e.g. “No questions yet” or similar). No errors in console. | ✓ Implemented |
| 4.2 | Expand/collapse and Mark done | Expand a question (show answer), then click **○** to mark done. | Answer stays visible; **○** becomes **✓**. Collapsing and expanding again keeps **✓**. | ✓ Implemented |
| 4.3 | Multiple topics in progress breakdown | Mark at least one question done in **two different topics** (e.g. one Complete Denture, one RPD). | Progress line shows 2/50. One topic shows 1/15, another 1/10 (or similar). No topic shows a count &gt; its total. | ✓ Implemented |

---

## Quick sign-off (manual verification)

**Code: 100% (19/19 metrics implemented).** Use the boxes below to record that you’ve **manually verified** each area. When all are ticked, Phase 1 is done and you can move to Phase 2.

- [ ] 1.1–1.6: List and filter behave correctly (counts, mix of topics, no duplicates).
- [ ] 2.1–2.6: Mark done toggles, updates counts, persists after refresh, and clears when storage is removed.
- [ ] 3.1–3.4: Home “Your progress” shows and updates with subject completion.
- [ ] 4.1–4.3: No console errors; edge cases (0 high-yield, expand + mark, multiple topics) behave as above.

If any item fails during verification, fix the bug and re-check that row before proceeding. **Next:** Phase 2 — Quiz mode (per-subject quiz, reuse progress, optional “not done” / high yield).
