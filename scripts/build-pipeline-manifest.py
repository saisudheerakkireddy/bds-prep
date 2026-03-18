#!/usr/bin/env python3
"""
Builds the central pipeline manifest that ties together:
  - PDF sources and their extraction quality
  - Per-subject KB stats
  - Steelman critique with mitigations
  - Pipeline health metrics
"""

import os, json, datetime

ROOT = os.path.join(os.path.dirname(__file__), "..")
KB_DIR = os.path.join(ROOT, "docs", "knowledge-base")
SUBJECTS_DIR = os.path.join(KB_DIR, "subjects")
EXTRACTED_DIR = os.path.join(KB_DIR, "extracted")

quality_report_path = os.path.join(EXTRACTED_DIR, "_quality-report.json")
quality_report = {}
if os.path.isfile(quality_report_path):
    with open(quality_report_path, "r") as f:
        quality_report = json.load(f)

subject_stats = []
total_q = total_fc = total_eq = 0

for fname in sorted(os.listdir(SUBJECTS_DIR)):
    if not fname.endswith(".json"):
        continue
    with open(os.path.join(SUBJECTS_DIR, fname), "r") as f:
        data = json.load(f)

    stats = data.get("stats", {})
    slug = data.get("subject_slug", fname.replace(".json", ""))

    entry = {
        "slug": slug,
        "kb_version": data.get("kb_version", "1.0"),
        "sources": data.get("sources", []),
        "pdf_sources": data.get("pdf_sources", []),
        "total_questions": stats.get("total_questions", 0),
        "high_yield_questions": stats.get("high_yield_questions", 0),
        "total_flashcards": stats.get("total_flashcards", 0),
        "total_exam_entries": stats.get("total_exam_entries", 0),
        "topics_count": stats.get("topics_count", 0),
        "exam_breakdown": stats.get("exam_breakdown", {}),
        "quality": data.get("quality_metadata", {}),
        "data_richness": "rich" if stats.get("total_questions", 0) >= 20 else (
            "partial" if stats.get("total_questions", 0) > 0 else "empty"
        ),
    }
    subject_stats.append(entry)
    total_q += stats.get("total_questions", 0)
    total_fc += stats.get("total_flashcards", 0)
    total_eq += stats.get("total_exam_entries", 0)

pdf_files = quality_report.get("files", [])
image_only = [f for f in pdf_files if f.get("quality_grade") == "image-only"]
extractable = [f for f in pdf_files if f.get("quality_grade") in ("high", "medium")]

manifest = {
    "manifest_id": "bds-pipeline-v2",
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),

    "pipeline_overview": {
        "description": "End-to-end data pipeline: Student handwritten PDFs → Text extraction → Q&A parsing → Flashcards + Revision + Exam bank",
        "stages": [
            {"stage": 1, "name": "PDF Ingestion",      "script": "scripts/pdf-extract.py",         "status": "operational"},
            {"stage": 2, "name": "KB Construction",     "script": "scripts/build-subject-kb.py",    "status": "operational"},
            {"stage": 3, "name": "Pipeline Manifest",   "script": "scripts/build-pipeline-manifest.py", "status": "operational"},
            {"stage": 4, "name": "App Content Ingestion","script": "scripts/ingest-subject.cjs",    "status": "operational"},
        ],
        "input": "docs/BDS_handwritten_notes_16th/*.pdf + 50_questions_eachsub/*.json",
        "output": "docs/knowledge-base/subjects/*.json → src/content/subjects/*.json → Astro app",
    },

    "aggregate_stats": {
        "total_pdf_sources": len(pdf_files),
        "extractable_pdfs": len(extractable),
        "image_only_pdfs": len(image_only),
        "total_subjects": len(subject_stats),
        "subjects_with_data": sum(1 for s in subject_stats if s["data_richness"] != "empty"),
        "total_questions": total_q,
        "total_flashcards": total_fc,
        "total_exam_entries": total_eq,
    },

    "subjects": subject_stats,

    "pdf_extraction_quality": pdf_files,

    "steelman_critique": [
        {
            "id": "SC-001",
            "criticism": "13 of 15 PDFs are scanned images with zero extractable text. The pipeline silently skips them, losing ~80% of the handwritten knowledge.",
            "severity": "critical",
            "impact": "5 subjects (Orthodontics, Public Health, Periodontics, Oral Medicine, and partially Pedodontics/Oral Surgery) have zero or minimal pipeline output despite having large source PDFs.",
            "mitigation": "Pipeline correctly classifies these as 'image-only' and tracks them. When cloud OCR (Google Vision, AWS Textract) is integrated, re-running pdf-extract.py will automatically flow new text through the full pipeline.",
            "status": "tracked",
            "next_action": "Add optional --ocr flag to pdf-extract.py that uses tesseract or cloud OCR for image-only PDFs."
        },
        {
            "id": "SC-002",
            "criticism": "Flashcard 'back' content is truncated at 500 chars. Long answers lose critical tail content (classifications, treatment protocols).",
            "severity": "medium",
            "impact": "Students reviewing flashcards may miss complete classification lists or step-by-step procedures.",
            "mitigation": "Full answer preserved in exam_bank entries. Flashcards serve as recall triggers, not comprehensive study cards.",
            "status": "accepted-risk",
            "next_action": "Consider generating 'mini-series' flashcards that split long answers into sequential cards."
        },
        {
            "id": "SC-003",
            "criticism": "Deduplication uses MD5 hash of normalized question text only. Two differently-worded questions about the same concept will not be caught.",
            "severity": "medium",
            "impact": "Semantic duplicates may exist across curated Q&A and PDF-extracted content for the same subject.",
            "mitigation": "Current dedup catches exact/near-exact duplicates. Semantic dedup would require embeddings (future enhancement).",
            "status": "tracked",
            "next_action": "Add keyword-overlap scoring as a lightweight semantic dedup layer."
        },
        {
            "id": "SC-004",
            "criticism": "PDF Q&A parser relies on numbered-question regex patterns. Non-standard formatting (tables, diagrams described in text, bullet-only sections) may be missed.",
            "severity": "low",
            "impact": "Some content in extractable PDFs may not be captured as Q&A pairs.",
            "mitigation": "Parser uses 3 complementary regex patterns. Uncaptured text is still preserved in the extracted JSON for manual review.",
            "status": "accepted-risk",
        },
        {
            "id": "SC-005",
            "criticism": "No version control on KB entries. Re-running the pipeline overwrites previous outputs without merge/diff tracking.",
            "severity": "medium",
            "impact": "Manual corrections to KB entries would be lost on re-run.",
            "mitigation": "Pipeline is idempotent and deterministic. Manual corrections should be made to curated source files (50_questions_eachsub/*.json), not to generated outputs.",
            "status": "by-design",
        }
    ],

    "data_flow_for_remaining_subjects": {
        "explanation": "Subjects with empty KBs need content through one of these paths:",
        "paths": [
            {
                "path": "A: OCR Pipeline",
                "description": "Add OCR to pdf-extract.py → re-extract → rebuild KB automatically",
                "subjects": ["orthodontics", "periodontics", "oral-medicine", "public-health-dentistry"],
                "effort": "medium (requires tesseract or cloud OCR setup)"
            },
            {
                "path": "B: Curated Q&A",
                "description": "Create 50_questions_eachsub/<subject>.json manually → run build-subject-kb.py",
                "subjects": ["any subject"],
                "effort": "high (manual content creation) but highest quality"
            },
            {
                "path": "C: Model-Generated",
                "description": "Use LLM to generate Q&A based on BDS syllabus topics → validate → ingest",
                "subjects": ["all empty subjects"],
                "effort": "low (automated) but needs expert validation"
            }
        ]
    }
}

out_path = os.path.join(KB_DIR, "pipeline-manifest.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"Pipeline manifest → {out_path}")
print(f"\nAggregate: {total_q} questions, {total_fc} flashcards, {total_eq} exam entries across {len(subject_stats)} subjects")
print(f"Data-rich subjects: {[s['slug'] for s in subject_stats if s['data_richness'] == 'rich']}")
print(f"Partial subjects:   {[s['slug'] for s in subject_stats if s['data_richness'] == 'partial']}")
print(f"Empty subjects:     {[s['slug'] for s in subject_stats if s['data_richness'] == 'empty']}")
