#!/usr/bin/env python3
"""
Amazon Textract OCR Pipeline for BDS Handwritten Notes
=======================================================
Uploads PDFs to S3, runs Textract async text detection,
downloads results, scores quality, and saves extracted JSON.

Usage:
  python3 scripts/ocr-textract.py                         # all PDFs
  python3 scripts/ocr-textract.py --file Prostho.pdf       # single file
  python3 scripts/ocr-textract.py --skip-upload             # reuse S3 files
"""

import os, sys, json, re, time, hashlib, argparse, datetime

import boto3

ROOT = os.path.join(os.path.dirname(__file__), "..")
NOTES_DIR = os.path.join(ROOT, "docs", "BDS_handwritten_notes_16th")
OUT_DIR = os.path.join(ROOT, "docs", "knowledge-base", "extracted")
S3_BUCKET = "bds-ocr-notes-2026"
REGION = "us-east-1"

SUBJECT_MAP = {
    "ORALMEDICINE.pdf":                       "oral-medicine",
    "oral medicine notes.pdf":                "oral-medicine",
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

SKIP_FILES = {"Pedodontics IV BDS brief notes .pdf"}

DENTAL_TERMS = [
    "tooth", "teeth", "dental", "occlusion", "mandib", "maxill", "gingiv",
    "pulp", "enamel", "dentin", "crown", "bridge", "denture", "caries",
    "periapical", "edentulous", "prosthesis", "impression", "cement",
    "amalgam", "composite", "resin", "fluoride", "plaque", "calculus",
    "abscess", "extraction", "impaction", "fracture", "suture", "flap",
    "implant", "retainer", "orthodon", "perio", "endo", "pedo",
    "anesthesia", "analges", "radiograph", "diagnos", "treatment",
    "classify", "types", "etiology", "pathogen", "prognos", "mucosa",
    "alveolar", "ridge", "palat", "tongue", "saliva", "oral", "cavity",
    "incis", "canine", "premolar", "molar", "cusp", "fossa", "margin",
    "occlus", "articulat", "condyle", "tmj", "biopsy", "lesion",
]


def slug_from_filename(filename):
    return re.sub(r'[^a-z0-9]+', '-', filename.lower().replace('.pdf', '')).strip('-')


def sha256_prefix(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:24]


def readability_score(text):
    if not text or len(text) < 10:
        return 0.0
    words = text.split()
    if not words:
        return 0.0
    real_words = sum(1 for w in words if len(w) > 1 and re.match(r'^[A-Za-z]+$', w))
    word_ratio = real_words / len(words)

    domain_hits = sum(1 for term in DENTAL_TERMS if term in text.lower())
    domain_score = min(0.3, domain_hits * 0.015)

    structural = 0
    for pat in [r'\d+[\.\)]\s', r'\?\s', r'[A-Z]{3,}', r'Define|Describe|Classify|Treatment']:
        if re.search(pat, text):
            structural += 1
    struct_score = min(0.2, structural * 0.05)

    return min(1.0, word_ratio * 0.5 + domain_score + struct_score)


def upload_to_s3(filepath, s3_key, s3_client):
    size_mb = os.path.getsize(filepath) / 1024 / 1024
    print(f"    uploading {s3_key} ({size_mb:.1f} MB)...", flush=True)
    s3_client.upload_file(filepath, S3_BUCKET, s3_key)
    print(f"    uploaded.", flush=True)


def start_textract_job(s3_key, textract_client):
    response = textract_client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {'Bucket': S3_BUCKET, 'Name': s3_key}
        }
    )
    return response['JobId']


def wait_for_textract_job(job_id, textract_client, filename):
    print(f"    processing: ", end="", flush=True)
    while True:
        response = textract_client.get_document_text_detection(JobId=job_id)
        status = response['JobStatus']
        if status == 'SUCCEEDED':
            print(f" done!", flush=True)
            return response
        elif status == 'FAILED':
            msg = response.get('StatusMessage', 'unknown error')
            print(f" FAILED: {msg}", flush=True)
            return None
        else:
            print(".", end="", flush=True)
            time.sleep(5)


def collect_all_results(job_id, textract_client, first_response):
    blocks = first_response.get('Blocks', [])
    next_token = first_response.get('NextToken')
    while next_token:
        response = textract_client.get_document_text_detection(
            JobId=job_id, NextToken=next_token
        )
        blocks.extend(response.get('Blocks', []))
        next_token = response.get('NextToken')
    return blocks


def blocks_to_pages(blocks):
    pages = {}
    for block in blocks:
        if block['BlockType'] == 'LINE':
            page_num = block.get('Page', 1)
            if page_num not in pages:
                pages[page_num] = {"page": page_num, "lines": [], "confidences": []}
            pages[page_num]["lines"].append(block.get('Text', ''))
            pages[page_num]["confidences"].append(block.get('Confidence', 0))

    result = []
    for page_num in sorted(pages.keys()):
        p = pages[page_num]
        text = "\n".join(p["lines"])
        avg_conf = sum(p["confidences"]) / max(len(p["confidences"]), 1)
        result.append({
            "page": page_num,
            "text": text,
            "ocr_confidence": round(avg_conf, 2),
            "readability_score": round(readability_score(text), 3),
            "line_count": len(p["lines"]),
        })
    return result


def process_one(filename, s3_client, textract_client, skip_upload=False):
    filepath = os.path.join(NOTES_DIR, filename)
    if not os.path.isfile(filepath):
        return {"filename": filename, "error": "file not found"}

    s3_key = f"ocr-input/{slug_from_filename(filename)}.pdf"
    subject = SUBJECT_MAP.get(filename, "unclassified")
    file_hash = sha256_prefix(filepath)
    size_mb = round(os.path.getsize(filepath) / 1024 / 1024, 2)

    print(f"\n  [{filename}]", flush=True)

    if not skip_upload:
        upload_to_s3(filepath, s3_key, s3_client)

    job_id = start_textract_job(s3_key, textract_client)
    print(f"    job started: {job_id[:12]}...", flush=True)

    first_response = wait_for_textract_job(job_id, textract_client, filename)
    if first_response is None:
        return {"filename": filename, "subject": subject, "error": "textract failed"}

    blocks = collect_all_results(job_id, textract_client, first_response)
    pages = blocks_to_pages(blocks)

    total_chars = sum(len(p["text"]) for p in pages)
    avg_confidence = sum(p["ocr_confidence"] for p in pages) / max(len(pages), 1)
    avg_readability = sum(p["readability_score"] for p in pages) / max(len(pages), 1)
    good_pages = sum(1 for p in pages if p["readability_score"] > 0.4)

    if avg_readability > 0.5:
        grade = "high"
    elif avg_readability > 0.3:
        grade = "medium"
    elif avg_readability > 0.1:
        grade = "low"
    else:
        grade = "poor"

    result = {
        "filename": filename,
        "subject": subject,
        "sha256_prefix": file_hash,
        "size_mb": size_mb,
        "extractor": "textract",
        "quality_grade": grade,
        "quality_score": round(avg_readability, 3),
        "stats": {
            "total_pages": len(pages),
            "non_empty_pages": sum(1 for p in pages if len(p["text"]) > 30),
            "good_quality_pages": good_pages,
            "total_chars": total_chars,
            "avg_chars_per_page": round(total_chars / max(len(pages), 1), 1),
            "avg_ocr_confidence": round(avg_confidence, 2),
            "avg_readability": round(avg_readability, 3),
        },
        "pages": pages,
    }

    print(f"    result: {len(pages)} pages, {total_chars} chars, grade={grade}, "
          f"confidence={avg_confidence:.0f}%, readability={avg_readability:.1%}", flush=True)

    return result


def cleanup_s3(s3_client, files_processed):
    print(f"\n  Cleaning up S3...", flush=True)
    for fname in files_processed:
        s3_key = f"ocr-input/{slug_from_filename(fname)}.pdf"
        try:
            s3_client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
        except Exception:
            pass
    print(f"    deleted {len(files_processed)} files from S3.", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Textract OCR for BDS PDFs")
    parser.add_argument("--file", help="Single filename to process")
    parser.add_argument("--skip-upload", action="store_true", help="Skip S3 upload (files already there)")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't delete S3 files after processing")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    s3_client = boto3.client('s3', region_name=REGION)
    textract_client = boto3.client('textract', region_name=REGION)

    if args.file:
        files = [args.file]
    else:
        files = sorted(
            f for f in os.listdir(NOTES_DIR)
            if f.lower().endswith('.pdf') and f not in SKIP_FILES
        )

    print(f"BDS Textract OCR Pipeline")
    print(f"{'='*60}")
    print(f"  Files to process: {len(files)}")
    print(f"  S3 Bucket: {S3_BUCKET}")
    print(f"  Output: {OUT_DIR}")
    start_time = time.time()

    report = []
    processed_files = []

    for i, fname in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] ", end="", flush=True)
        try:
            result = process_one(fname, s3_client, textract_client, args.skip_upload)
            processed_files.append(fname)

            if result.get("pages"):
                slug = slug_from_filename(fname)
                out_path = os.path.join(OUT_DIR, f"{slug}.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"    saved → {slug}.json", flush=True)

            report.append({
                "filename": fname,
                "subject": result.get("subject", "?"),
                "quality_grade": result.get("quality_grade", "?"),
                "quality_score": result.get("quality_score", 0),
                "total_chars": result.get("stats", {}).get("total_chars", 0),
                "avg_ocr_confidence": result.get("stats", {}).get("avg_ocr_confidence", 0),
                "avg_readability": result.get("stats", {}).get("avg_readability", 0),
                "total_pages": result.get("stats", {}).get("total_pages", 0),
                "good_quality_pages": result.get("stats", {}).get("good_quality_pages", 0),
                "error": result.get("error"),
            })
        except Exception as e:
            print(f"  ERROR processing {fname}: {e}", flush=True)
            report.append({"filename": fname, "error": str(e)})

    if not args.no_cleanup and processed_files:
        cleanup_s3(s3_client, processed_files)

    elapsed = time.time() - start_time

    report_path = os.path.join(OUT_DIR, "_quality-report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "ocr_engine": "amazon-textract",
            "total_files": len(report),
            "elapsed_seconds": round(elapsed, 1),
            "files": sorted(report, key=lambda x: -x.get("quality_score", 0)),
        }, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  COMPLETE: {len(report)} files in {elapsed/60:.1f} minutes")
    total_pages = sum(r.get("total_pages", 0) for r in report)
    total_chars = sum(r.get("total_chars", 0) for r in report)
    print(f"  Total pages OCR'd: {total_pages}")
    print(f"  Total chars extracted: {total_chars:,}")
    print(f"  Quality report → {report_path}")
    for r in sorted(report, key=lambda x: -x.get("quality_score", 0)):
        grade = r.get("quality_grade", "?")
        score = r.get("avg_readability", 0)
        err = r.get("error", "")
        print(f"    {r['filename']:<45} {grade:<8} {score:.0%}  {err}")


if __name__ == "__main__":
    main()
