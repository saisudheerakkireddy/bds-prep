#!/usr/bin/env python3
"""
PDF Text Extraction Pipeline for BDS Knowledge Base
====================================================
Extracts text from all PDFs in BDS_handwritten_notes_16th/,
grades quality, and outputs structured JSON per file.

Usage:
  python3 scripts/pdf-extract.py                    # extract all
  python3 scripts/pdf-extract.py --file Prostho.pdf # single file
"""

import os, sys, json, hashlib, re, argparse, datetime

NOTES_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "BDS_handwritten_notes_16th")
OUT_DIR   = os.path.join(os.path.dirname(__file__), "..", "docs", "knowledge-base", "extracted")

SUBJECT_MAP = {
    "ORALMEDICINE.pdf":                       "oral-medicine-and-radiology",
    "oral medicine notes.pdf":                "oral-medicine-and-radiology",
    "Orthodontics notes.pdf":                 "orthodontics",
    "Book 4 Aug 2024.pdf":                    "orthodontics",
    "PHD notes (1).pdf":                      "public-health-dentistry",
    "PUBLIC HEALTH VOL 1_watermark (1).pdf":  "public-health-dentistry",
    "PUBLIC HEALTH VOL 2-1_watermark.pdf":    "public-health-dentistry",
    "Pedodontics IV BDS brief notes .pdf":    "pedodontics",
    "pedo.pdf":                               "pedodontics",
    "Periodontics notes .pdf":                "periodontics",
    "Prostho.pdf":                            "prosthodontics",
    "cons and endo.pdf":                      "conservative-dentistry",
    "oral surgery (1).pdf":                   "oral-surgery",
    "os notes.pdf":                           "oral-surgery",
    "Adobe Scan 21 May 2024.pdf":             "unclassified",
}


def sha256_file(path, chunk_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            h.update(data)
    return h.hexdigest()[:24]


def extract_text_pdfplumber(path, max_pages=None):
    """Primary extractor using pdfplumber (best for mixed content)."""
    import pdfplumber
    pages = []
    try:
        with pdfplumber.open(path) as pdf:
            total = len(pdf.pages)
            limit = min(total, max_pages) if max_pages else total
            for i in range(limit):
                text = pdf.pages[i].extract_text() or ""
                pages.append({"page": i + 1, "text": text.strip()})
    except Exception as e:
        return None, str(e)
    return pages, None


def extract_text_pypdf2(path, max_pages=None):
    """Fallback extractor using PyPDF2."""
    import PyPDF2
    pages = []
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            total = len(reader.pages)
            limit = min(total, max_pages) if max_pages else total
            for i in range(limit):
                text = reader.pages[i].extract_text() or ""
                pages.append({"page": i + 1, "text": text.strip()})
    except Exception as e:
        return None, str(e)
    return pages, None


def grade_quality(pages):
    """Grade extraction quality based on text density and structure signals."""
    if not pages:
        return "empty", 0.0, {}

    total_chars = sum(len(p["text"]) for p in pages)
    non_empty   = sum(1 for p in pages if len(p["text"]) > 50)
    avg_chars   = total_chars / len(pages) if pages else 0
    pct_non_empty = non_empty / len(pages) if pages else 0

    structural_signals = 0
    all_text = " ".join(p["text"] for p in pages)
    for pattern in [r'\d+\.\s', r'[A-Z]{2,}', r'\?\s', r'Define\b', r'Describe\b',
                    r'classify', r'enumerate', r'diagnosis', r'treatment']:
        if re.search(pattern, all_text, re.IGNORECASE):
            structural_signals += 1

    if avg_chars > 500 and pct_non_empty > 0.7:
        grade = "high"
        score = min(1.0, 0.7 + (structural_signals * 0.03))
    elif avg_chars > 100 and pct_non_empty > 0.3:
        grade = "medium"
        score = 0.4 + (pct_non_empty * 0.2) + (structural_signals * 0.02)
    elif avg_chars > 20 and pct_non_empty > 0.05:
        grade = "low"
        score = 0.1 + (pct_non_empty * 0.15)
    else:
        grade = "image-only"
        score = 0.0

    stats = {
        "total_pages": len(pages),
        "non_empty_pages": non_empty,
        "pct_non_empty": round(pct_non_empty, 3),
        "total_chars": total_chars,
        "avg_chars_per_page": round(avg_chars, 1),
        "structural_signals": structural_signals,
    }
    return grade, round(score, 3), stats


def extract_one(filename, max_pages=None):
    path = os.path.join(NOTES_DIR, filename)
    if not os.path.isfile(path):
        return {"filename": filename, "error": "file not found"}

    file_hash = sha256_file(path)
    size_mb = round(os.path.getsize(path) / 1024 / 1024, 2)
    subject = SUBJECT_MAP.get(filename, "unclassified")

    pages, err1 = extract_text_pdfplumber(path, max_pages)
    extractor = "pdfplumber"
    if pages is None or all(len(p["text"]) == 0 for p in pages):
        pages, err2 = extract_text_pypdf2(path, max_pages)
        extractor = "PyPDF2"
        if pages is None:
            return {
                "filename": filename,
                "subject": subject,
                "sha256_prefix": file_hash,
                "size_mb": size_mb,
                "error": err2 or err1,
                "quality_grade": "failed",
            }

    grade, score, stats = grade_quality(pages)
    non_empty_pages = [p for p in pages if len(p["text"]) > 30]

    return {
        "filename": filename,
        "subject": subject,
        "sha256_prefix": file_hash,
        "size_mb": size_mb,
        "extractor": extractor,
        "quality_grade": grade,
        "quality_score": score,
        "stats": stats,
        "pages": non_empty_pages,
    }


def main():
    parser = argparse.ArgumentParser(description="Extract text from BDS PDFs")
    parser.add_argument("--file", help="Single filename to process")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit pages per PDF")
    parser.add_argument("--quality-report", action="store_true", help="Only output quality summary")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    if args.file:
        files = [args.file]
    else:
        files = sorted(f for f in os.listdir(NOTES_DIR) if f.lower().endswith(".pdf"))

    report = []
    for fname in files:
        print(f"  extracting: {fname} ...", flush=True)
        result = extract_one(fname, args.max_pages)

        if not args.quality_report and result.get("pages"):
            slug = re.sub(r'[^a-z0-9]+', '-', fname.lower().replace('.pdf', '')).strip('-')
            out_path = os.path.join(OUT_DIR, f"{slug}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"    → {out_path} ({result['quality_grade']}, {result.get('stats',{}).get('non_empty_pages',0)} pages)")

        report.append({
            "filename": fname,
            "subject": result.get("subject", "?"),
            "quality_grade": result.get("quality_grade", "?"),
            "quality_score": result.get("quality_score", 0),
            "total_chars": result.get("stats", {}).get("total_chars", 0),
            "non_empty_pages": result.get("stats", {}).get("non_empty_pages", 0),
            "total_pages": result.get("stats", {}).get("total_pages", 0),
        })

    report_path = os.path.join(OUT_DIR, "_quality-report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_files": len(report),
            "files": sorted(report, key=lambda x: -x["quality_score"]),
        }, f, indent=2)
    print(f"\n  Quality report → {report_path}")


if __name__ == "__main__":
    main()
