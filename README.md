# 🦷 BDS Final Year Exam Prep — AP 2026

A fast, mobile-first study-aid for BDS Final Year students in Andhra Pradesh. Built with Astro + React + Tailwind, deployed on Vercel.

## Features

- **Subject-wise Q&A** with expandable cards, high-yield filters, and memorable analogies
- **Mermaid mind maps** rendered client-side for concept visualization
- **Live exam countdown** with IST-aware timer
- **Study planner** with visual timeline of all 8 exams + practicals
- **Mobile-first** — works on 320px+ screens (most students use phones)

## Quick Start

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
bds-prep/
├── .cursor/
│   └── prompt.json          # JSON prompt for Opus content generation
├── .cursorrules             # Project context for Cursor AI
├── src/
│   ├── components/
│   │   ├── ExamCountdown.tsx    # Live countdown (React island)
│   │   ├── MermaidDiagram.tsx   # Mermaid renderer (React island)
│   │   └── QAAccordion.tsx      # Q&A cards with filters (React island)
│   ├── content/
│   │   └── subjects/
│   │       └── prosthodontics.json  # Sample — generate rest via Opus
│   ├── layouts/
│   │   └── BaseLayout.astro     # Shared shell with nav + footer
│   ├── lib/
│   │   └── subjects.ts         # Subject metadata + exam schedule
│   ├── pages/
│   │   ├── index.astro          # Home — dashboard with subject grid
│   │   ├── planner.astro        # Study planner timeline
│   │   └── subjects/
│   │       └── [slug].astro     # Dynamic subject detail page
│   └── styles/
│       └── global.css           # Tailwind + custom components
├── astro.config.mjs
├── tailwind.config.mjs
├── tsconfig.json
├── package.json
└── vercel.json
```

## Content Generation Workflow (Cursor + Opus)

### Step 1: Setup
1. Open this project in Cursor
2. Copy your BDS PDFs into a `/data` folder at project root
3. Open `.cursor/prompt.json` — this is the master prompt

### Step 2: Generate content per subject
For each subject, tell Opus in Cursor:

> Read these PDFs: [list from prompt.json → subject_pdf_mapping].
> Follow the tasks in .cursor/prompt.json to generate
> `src/content/subjects/<slug>.json`.
> Ensure minimum 20 questions, 3 mind maps, all with analogies.

Example for Prosthodontics:
> Read data/Prosthodontics.pdf and data/prostho (1).pdf.
> Generate src/content/subjects/prosthodontics.json following .cursor/prompt.json schema.

### Step 3: Verify
```bash
npm run dev
# Open http://localhost:4321/subjects/prosthodontics
# Check Q&A renders, mind maps display, no mermaid errors
```

### Step 4: Curate
- Fix any incorrect answers
- Improve weak analogies
- Validate mermaid at https://mermaid.live
- Add missing high-yield tags

### Step 5: Deploy
```bash
# Push to GitHub, connect to Vercel
vercel

# Or build and deploy manually
npm run build
vercel deploy --prebuilt
```

## Exam Schedule (Source: Controller of Examinations, AP)

| Date       | Day       | Subject                                   | Paper Code |
|------------|-----------|-------------------------------------------|------------|
| 25.03.2026 | Wednesday | Prosthodontics and Crown & Bridge         | 429/409    |
| 28.03.2026 | Saturday  | Conservative Dentistry and Endodontics    | 430/410    |
| 30.03.2026 | Monday    | Oral Maxillofacial Surgery                | 431/412    |
| 01.04.2026 | Wednesday | Public Health Dentistry                   | 432        |
| 04.04.2026 | Saturday  | Oral Medicine & Radiology                 | 425/413    |
| 06.04.2026 | Monday    | Paediatric & Preventive Dentistry         | 426/415    |
| 08.04.2026 | Wednesday | Orthodontics & Dentofacial Orthopaedics   | 427/411    |
| 10.04.2026 | Friday    | Periodontics                              | 428/414    |

Practicals tentatively from 15.04.2026.

## License

MIT — Built with ❤️ for BDS students.
