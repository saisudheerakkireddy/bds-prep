#!/usr/bin/env python3
"""
BDS Knowledge Base Builder
===========================
Transforms curated Q&A + extracted PDF text into a multi-format
knowledge base per subject: flashcards, revision nodes, exam bank.

Sources:
  1. Curated Q&A       → 50_questions_eachsub/*.json
  2. Extracted PDF text → docs/knowledge-base/extracted/*.json
  3. Existing app data  → src/content/subjects/*.json

Output → docs/knowledge-base/subjects/<slug>.json (enriched)

Usage:
  python3 scripts/build-subject-kb.py --subject prosthodontics
  python3 scripts/build-subject-kb.py --all
"""

import os, sys, json, re, hashlib, argparse, datetime

ROOT = os.path.join(os.path.dirname(__file__), "..")
CURATED_DIR   = os.path.join(ROOT, "50_questions_eachsub")
EXTRACTED_DIR = os.path.join(ROOT, "docs", "knowledge-base", "extracted")
APP_DATA_DIR  = os.path.join(ROOT, "src", "content", "subjects")
KB_OUT_DIR    = os.path.join(ROOT, "docs", "knowledge-base", "subjects")

SUBJECT_SLUG_MAP = {
    "prosthodontics":         {"curated": "prostho.json",  "app": "prosthodontics.json",         "extracted": ["prostho.json"]},
    "conservative-dentistry": {"curated": "endo.json",     "app": "conservative-dentistry.json",  "extracted": ["cons-and-endo.json"]},
    "oral-surgery":           {"curated": "omfs.json",     "app": "oral-surgery.json",            "extracted": ["oral-surgery-1.json", "os-notes.json"]},
    "pedodontics":            {"curated": None,            "app": None,                           "extracted": ["pedodontics-iv-bds-brief-notes.json", "pedo.json"]},
    "orthodontics":           {"curated": None,            "app": None,                           "extracted": ["orthodontics-notes.json", "book-4-aug-2024.json"]},
    "public-health-dentistry":{"curated": None,            "app": "public-health-dentistry.json", "extracted": ["phd-notes-1.json", "public-health-vol-1-watermark-1.json", "public-health-vol-2-1-watermark.json"]},
    "periodontics":           {"curated": None,            "app": None,                           "extracted": ["periodontics-notes.json"]},
    "oral-medicine":          {"curated": None,            "app": None,                           "extracted": ["oralmedicine.json", "oral-medicine-notes.json"]},
}

PDF_SOURCE_MAP = {
    "prosthodontics":          ["Prostho.pdf"],
    "conservative-dentistry":  ["cons and endo.pdf"],
    "oral-surgery":            ["oral surgery (1).pdf", "os notes.pdf"],
    "pedodontics":             ["Pedodontics IV BDS brief notes .pdf", "pedo.pdf"],
    "orthodontics":            ["Orthodontics notes.pdf", "Book 4 Aug 2024.pdf"],
    "public-health-dentistry": ["PHD notes (1).pdf", "PUBLIC HEALTH VOL 1_watermark (1).pdf", "PUBLIC HEALTH VOL 2-1_watermark.pdf"],
    "periodontics":            ["Periodontics notes .pdf"],
    "oral-medicine":           ["oral medicine notes.pdf", "ORALMEDICINE.pdf"],
}


def concept_hash(text):
    """Fingerprint for dedup: lowercase, strip punctuation, hash."""
    normalized = re.sub(r'[^a-z0-9\s]', '', text.lower().strip())
    normalized = re.sub(r'\s+', ' ', normalized)
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def load_curated(filename):
    path = os.path.join(CURATED_DIR, filename)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_extracted(filename):
    path = os.path.join(EXTRACTED_DIR, filename)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_key_points(answer_text):
    """Pull numbered/bulleted key points from an answer string."""
    points = []
    for match in re.finditer(r'\((\d+)\)\s*\*\*(.+?)\*\*\s*[-–]?\s*(.+?)(?=,?\s*\(\d+\)|$)', answer_text):
        points.append(f"{match.group(2).strip()}: {match.group(3).strip()}")
    if not points:
        sentences = [s.strip() for s in re.split(r'[.;]', answer_text) if len(s.strip()) > 20]
        points = sentences[:5]
    return points


def extract_bold_terms(text):
    """Extract all **bold** terms as key vocabulary."""
    return list(set(re.findall(r'\*\*(.+?)\*\*', text)))


def question_to_flashcard(q, topic_name):
    """Convert a Q&A entry into one or more flashcards."""
    cards = []
    qtext = q.get("question", "")
    answer = q.get("answer", "")
    bold_terms = extract_bold_terms(answer)

    cards.append({
        "card_id": f"fc-{q['id']}",
        "front": qtext,
        "back": answer[:500] + ("..." if len(answer) > 500 else ""),
        "topic": topic_name,
        "difficulty": q.get("difficulty", "intermediate"),
        "high_yield": q.get("highYield", False),
        "source_question_id": q["id"],
        "concept_hash": concept_hash(qtext),
    })

    for term in bold_terms[:3]:
        if len(term) > 5 and term.lower() not in qtext.lower():
            cards.append({
                "card_id": f"fc-{q['id']}-term-{concept_hash(term)}",
                "front": f"Define: {term}",
                "back": next(
                    (s.strip() for s in re.split(r'[.;]', answer)
                     if term.lower() in s.lower() and len(s.strip()) > 15),
                    f"Key concept in {topic_name}"
                ),
                "topic": topic_name,
                "difficulty": "easy",
                "high_yield": q.get("highYield", False),
                "source_question_id": q["id"],
                "concept_hash": concept_hash(term),
            })

    return cards


def question_to_exam_entry(q, topic_name):
    """Convert Q&A entry into exam-oriented question entries."""
    qtype = q.get("questionType", "short-answer")
    freq = q.get("examFrequency", "moderate")

    exam_types = []
    answer = q.get("answer", "")
    qtext = q.get("question", "")

    if len(answer) > 800 or qtype == "long-answer":
        exam_types.append("long-essay")
    if len(answer) > 200:
        exam_types.append("short-answer")
    exam_types.append("viva")

    entries = []
    for et in exam_types:
        entries.append({
            "exam_q_id": f"eq-{q['id']}-{et}",
            "question": qtext,
            "model_answer": answer,
            "type": et,
            "topic": topic_name,
            "frequency": freq,
            "high_yield": q.get("highYield", False),
            "keywords": q.get("keywords", extract_bold_terms(answer)[:8]),
            "marks_estimate": {"long-essay": 10, "short-answer": 5, "viva": 3}.get(et, 5),
            "source_question_id": q["id"],
        })

    return entries


def build_revision_nodes(questions_by_topic):
    """Build condensed revision nodes per topic from questions."""
    nodes = []
    for topic_name, qs in questions_by_topic.items():
        all_points = []
        all_terms = set()
        clinical_pearls = []
        high_yield_qs = []

        for q in qs:
            answer = q.get("answer", "")
            points = extract_key_points(answer)
            all_points.extend(points)
            all_terms.update(extract_bold_terms(answer))

            for pattern in [r'clinical(?:ly)?\s+(?:important|significant|relevant)',
                            r'most\s+common', r'gold\s+standard', r'treatment\s+of\s+choice']:
                for m in re.finditer(pattern, answer, re.IGNORECASE):
                    start = max(0, m.start() - 40)
                    end = min(len(answer), m.end() + 80)
                    pearl = answer[start:end].strip()
                    if pearl not in clinical_pearls:
                        clinical_pearls.append(pearl)

            if q.get("highYield", False):
                high_yield_qs.append(q["id"])

        seen_hashes = set()
        deduped_points = []
        for pt in all_points:
            h = concept_hash(pt)
            if h not in seen_hashes:
                seen_hashes.add(h)
                deduped_points.append(pt)

        nodes.append({
            "topic": topic_name,
            "total_questions": len(qs),
            "high_yield_question_ids": high_yield_qs,
            "key_points": deduped_points[:25],
            "key_vocabulary": sorted(all_terms)[:30],
            "clinical_pearls": clinical_pearls[:10],
            "revision_time_estimate_minutes": max(5, len(deduped_points) * 2),
        })

    return nodes


def detect_topics_from_text(full_text):
    """Detect topic/chapter headings from extracted PDF text."""
    topics = []
    for match in re.finditer(r'\n([A-Z][A-Z &\-/]{5,})\s*\n', full_text):
        heading = match.group(1).strip()
        if heading and len(heading) < 80 and heading not in ['DEPARTMENT', 'VISHNU DENTAL COLLEGE']:
            topics.append({"name": heading.title(), "pos": match.start()})
    return topics


SECTION_HEADINGS = [
    "definition", "etiology", "clinical features", "classification",
    "treatment", "diagnosis", "investigation", "pathogenesis",
    "histopathology", "radiographic", "differential diagnosis",
    "prognosis", "management", "complications", "prevention",
    "advantages", "disadvantages", "indications", "contraindications",
    "types", "causes", "signs and symptoms", "technique", "procedure",
    "properties", "composition", "mechanism of action", "pharmacology",
    "anatomy", "introduction", "epidemiology",
]

SECTION_TO_QUESTION = {
    "definition": "Define {topic}.",
    "etiology": "What is the etiology of {topic}?",
    "clinical features": "Describe the clinical features of {topic}.",
    "classification": "Classify {topic}.",
    "treatment": "What is the treatment for {topic}?",
    "diagnosis": "How is {topic} diagnosed?",
    "investigation": "What investigations are done for {topic}?",
    "pathogenesis": "Describe the pathogenesis of {topic}.",
    "histopathology": "Describe the histopathology of {topic}.",
    "radiographic": "What are the radiographic features of {topic}?",
    "differential diagnosis": "What is the differential diagnosis of {topic}?",
    "management": "Describe the management of {topic}.",
    "complications": "What are the complications of {topic}?",
    "advantages": "What are the advantages of {topic}?",
    "disadvantages": "What are the disadvantages of {topic}?",
    "indications": "What are the indications for {topic}?",
    "contraindications": "What are the contraindications of {topic}?",
    "types": "What are the types of {topic}?",
    "technique": "Describe the technique for {topic}.",
    "procedure": "Describe the procedure for {topic}.",
    "properties": "What are the properties of {topic}?",
    "composition": "What is the composition of {topic}?",
}


def parse_handwritten_notes(full_text, slug):
    """Parse OCR'd handwritten notes into knowledge entries using section detection."""
    full_text = re.sub(r'^Page \d+ of \d+\s*$', '', full_text, flags=re.MULTILINE)
    full_text = re.sub(r'^\d+\s+of\s+\d+\s*$', '', full_text, flags=re.MULTILINE)

    topic_pattern = re.compile(
        r'(?:^|\n)([A-Z][A-Za-z\s\-/&\'()]+?)(?:\s*[\[\(]\s*\d+\s*M(?:PQ)?\s*[\]\)])?'
        r'\s*(?:\n|$)',
        re.MULTILINE
    )

    sections = []
    current_topic = "General"

    for match in topic_pattern.finditer(full_text):
        heading = match.group(1).strip()
        heading_clean = re.sub(r'\s+', ' ', heading)
        if len(heading_clean) < 3 or len(heading_clean) > 80:
            continue
        word_count = len(heading_clean.split())
        upper_ratio = sum(1 for c in heading_clean if c.isupper()) / max(len(heading_clean.replace(' ', '')), 1)
        if upper_ratio > 0.4 or word_count <= 5:
            sections.append({"heading": heading_clean, "pos": match.start(), "end": match.end()})

    for i, sec in enumerate(sections):
        next_pos = sections[i + 1]["pos"] if i + 1 < len(sections) else len(full_text)
        sec["content"] = full_text[sec["end"]:next_pos].strip()

    mpq_pattern = re.compile(r'[\[\(]\s*(\d+)\s*M(?:PQ|arks?)?\s*[\]\)]', re.IGNORECASE)

    questions = []
    seen_hashes = set()
    q_counter = 0

    for sec in sections:
        heading = sec["heading"]
        content = sec["content"]
        if len(content) < 40:
            continue

        heading_lower = heading.lower().strip()

        is_section_heading = any(sh in heading_lower for sh in SECTION_HEADINGS)

        mpq_match = mpq_pattern.search(heading + " " + content[:100])
        marks = int(mpq_match.group(1)) if mpq_match else 0
        is_high_yield = marks >= 5 or any(kw in content.lower() for kw in [
            'most common', 'gold standard', 'treatment of choice',
            'most important', 'classification',
        ])

        if is_section_heading:
            parent_topic = current_topic
            matched_section = next((sh for sh in SECTION_HEADINGS if sh in heading_lower), "general")
            q_template = SECTION_TO_QUESTION.get(matched_section, "Describe {topic}.")
            question = q_template.format(topic=parent_topic)
        else:
            current_topic = heading
            question = f"Write a short note on {heading}."

        q_hash = re.sub(r'[^a-z0-9]', '', question.lower())[:60]
        if q_hash in seen_hashes:
            content_hash = re.sub(r'[^a-z0-9]', '', content[:100].lower())[:30]
            q_hash = q_hash + content_hash
        if q_hash in seen_hashes:
            continue
        seen_hashes.add(q_hash)

        q_counter += 1
        questions.append({
            "id": f"ocr-{slug}-{q_counter:03d}",
            "topic": re.sub(r'[^a-z0-9]+', '-', current_topic.lower()).strip('-'),
            "questionType": "long-answer" if len(content) > 800 else "short-answer",
            "difficulty": "advanced" if len(content) > 1500 else ("intermediate" if len(content) > 300 else "easy"),
            "examFrequency": "very-high" if marks >= 10 else ("high" if marks >= 5 or is_high_yield else "moderate"),
            "keywords": list(set(re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b', content)))[:8],
            "question": question,
            "answer": content,
            "highYield": is_high_yield,
            "marks_reference": marks if marks > 0 else None,
            "_topic_name": current_topic,
        })

    return questions


def build_from_extracted_pdf(extracted_data, slug):
    """Parse extracted PDF text into Q&A-like entries for pipeline processing."""
    pages = extracted_data.get("pages", [])
    full_text = "\n".join(p.get("text", "") for p in pages)

    full_text = re.sub(r'Department of Pedodontics & Preventive dentistry\s*\n?', '', full_text)
    full_text = re.sub(r'^\d+\s*$', '', full_text, flags=re.MULTILINE)
    full_text = re.sub(r'^Page \d+ of \d+\s*$', '', full_text, flags=re.MULTILINE)

    topics = detect_topics_from_text(full_text)

    def get_topic_at(pos):
        current = "General"
        for t in topics:
            if t["pos"] <= pos:
                current = t["name"]
            else:
                break
        return current

    qa_patterns = [
        re.compile(r'(\d+)\)\s*(.+?\?)\s*\n\s*(?:Ans?:?\s*|A:\s*)(.*?)(?=\n\s*\d+\)\s|\n[A-Z][A-Z ]{5,}\n|\Z)', re.DOTALL),
        re.compile(r'(\d+)\.\s*(.+?\?)\s*\n\s*(?:A:\s*|Ans?:?\s*)(.*?)(?=\n\s*\d+\.\s|\n[A-Z][A-Z ]{5,}\n|\Z)', re.DOTALL),
        re.compile(r'(\d+)\.\s*((?:Define|Describe|Explain|List|Enumerate|Classify|Differentiate|Compare|What|Write|Name|Mention|Discuss|Elaborate).+?[.?])\s*\n(.*?)(?=\n\s*\d+\.\s|\n[A-Z][A-Z ]{5,}\n|\Z)', re.DOTALL),
    ]

    seen_hashes = set()
    questions = []
    q_counter = 0

    for pat in qa_patterns:
        for match in pat.finditer(full_text):
            question = re.sub(r'\s+', ' ', match.group(2).strip())
            answer = match.group(3).strip()
            answer = re.sub(r'\n\s*\n\s*\n+', '\n\n', answer)

            if len(question) < 10 or len(answer) < 30:
                continue

            q_hash = re.sub(r'[^a-z0-9]', '', question.lower())[:60]
            if q_hash in seen_hashes:
                continue
            seen_hashes.add(q_hash)

            q_counter += 1
            topic_name = get_topic_at(match.start())

            is_high_yield = any(kw in answer.lower() for kw in [
                'most common', 'most important', 'gold standard',
                'classification', 'types of', 'treatment of choice'
            ])

            questions.append({
                "id": f"pdf-{slug}-{q_counter:03d}",
                "topic": re.sub(r'[^a-z0-9]+', '-', topic_name.lower()).strip('-'),
                "questionType": "long-answer" if len(answer) > 800 else "short-answer",
                "difficulty": "advanced" if len(answer) > 1500 else ("intermediate" if len(answer) > 300 else "easy"),
                "examFrequency": "high" if is_high_yield else "moderate",
                "keywords": list(set(re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b', answer)))[:8],
                "question": question,
                "answer": answer,
                "highYield": is_high_yield,
                "_topic_name": topic_name,
            })

    if len(questions) < 5 and len(full_text) > 1000:
        handwritten_qs = parse_handwritten_notes(full_text, slug)
        for hq in handwritten_qs:
            h = re.sub(r'[^a-z0-9]', '', hq["question"].lower())[:60]
            if h not in seen_hashes:
                seen_hashes.add(h)
                questions.append(hq)

    return questions


def build_subject(slug):
    """Build complete knowledge base for one subject."""
    config = SUBJECT_SLUG_MAP.get(slug)
    if not config:
        print(f"  Unknown subject slug: {slug}")
        return None

    print(f"\n{'='*60}")
    print(f"  Building: {slug}")
    print(f"{'='*60}")

    all_questions = []
    topic_map = {}
    sources_used = []

    if config["curated"]:
        curated = load_curated(config["curated"])
        if curated:
            for t in curated.get("topics", []):
                topic_map[t["id"]] = t["name"]
            for q in curated.get("questions", []):
                q["_topic_name"] = topic_map.get(q.get("topic", ""), q.get("topic", "General"))
                all_questions.append(q)
            sources_used.append(f"curated:{config['curated']}")
            print(f"  Loaded {len(all_questions)} curated questions from {config['curated']}")

    for ext_file in config.get("extracted", []):
        ext_data = load_extracted(ext_file)
        if ext_data:
            pdf_qs = build_from_extracted_pdf(ext_data, slug)
            all_questions.extend(pdf_qs)
            sources_used.append(f"pdf-extracted:{ext_file}")
            print(f"  Extracted {len(pdf_qs)} Q&A from {ext_file}")

    seen_hashes = set()
    deduped = []
    dup_count = 0
    for q in all_questions:
        h = concept_hash(q.get("question", ""))
        if h not in seen_hashes:
            seen_hashes.add(h)
            deduped.append(q)
        else:
            dup_count += 1
    all_questions = deduped
    if dup_count:
        print(f"  Deduped: removed {dup_count} duplicate questions")

    questions_by_topic = {}
    for q in all_questions:
        tn = q.get("_topic_name", "General")
        questions_by_topic.setdefault(tn, []).append(q)

    print(f"  Topics found: {list(questions_by_topic.keys())}")

    flashcards = []
    exam_bank = []
    for q in all_questions:
        tn = q.get("_topic_name", "General")
        flashcards.extend(question_to_flashcard(q, tn))
        exam_bank.extend(question_to_exam_entry(q, tn))

    fc_hashes = set()
    deduped_fc = []
    for fc in flashcards:
        if fc["concept_hash"] not in fc_hashes:
            fc_hashes.add(fc["concept_hash"])
            deduped_fc.append(fc)
    flashcards = deduped_fc

    revision_nodes = build_revision_nodes(questions_by_topic)

    exam_summary = {
        "long_essay": [e for e in exam_bank if e["type"] == "long-essay"],
        "short_answer": [e for e in exam_bank if e["type"] == "short-answer"],
        "viva": [e for e in exam_bank if e["type"] == "viva"],
    }

    high_yield_count = sum(1 for q in all_questions if q.get("highYield", False))

    kb = {
        "kb_version": "2.0",
        "subject_slug": slug,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sources": sources_used,
        "pdf_sources": PDF_SOURCE_MAP.get(slug, []),

        "stats": {
            "total_questions": len(all_questions),
            "high_yield_questions": high_yield_count,
            "total_flashcards": len(flashcards),
            "total_exam_entries": len(exam_bank),
            "total_revision_nodes": len(revision_nodes),
            "topics_count": len(questions_by_topic),
            "exam_breakdown": {k: len(v) for k, v in exam_summary.items()},
        },

        "topics": [
            {
                "id": re.sub(r'[^a-z0-9]+', '-', tn.lower()).strip('-'),
                "name": tn,
                "question_count": len(qs),
                "high_yield_count": sum(1 for q in qs if q.get("highYield", False)),
            }
            for tn, qs in questions_by_topic.items()
        ],

        "flashcards": flashcards,

        "revision_nodes": revision_nodes,

        "exam_bank": {
            "long_essay": exam_summary["long_essay"],
            "short_answer": exam_summary["short_answer"],
            "viva": exam_summary["viva"],
        },

        "quality_metadata": {
            "curated_qa_available": config["curated"] is not None,
            "pdf_text_extractable": len(config.get("extracted", [])) > 0,
            "pdf_scans_pending_ocr": [
                f for f in PDF_SOURCE_MAP.get(slug, [])
                if f not in [e.replace('.json', '.pdf') for e in config.get("extracted", [])]
            ],
            "dedup_applied": True,
            "concept_hash_algorithm": "md5-12char-normalized",
        },
    }

    return kb


def main():
    parser = argparse.ArgumentParser(description="Build BDS subject knowledge base")
    parser.add_argument("--subject", help="Subject slug to process")
    parser.add_argument("--all", action="store_true", help="Process all subjects")
    args = parser.parse_args()

    os.makedirs(KB_OUT_DIR, exist_ok=True)

    if args.all:
        slugs = list(SUBJECT_SLUG_MAP.keys())
    elif args.subject:
        slugs = [args.subject]
    else:
        print("Usage: --subject <slug> or --all")
        print(f"Available: {', '.join(SUBJECT_SLUG_MAP.keys())}")
        sys.exit(1)

    results = []
    for slug in slugs:
        kb = build_subject(slug)
        if kb:
            out_path = os.path.join(KB_OUT_DIR, f"{slug}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(kb, f, indent=2, ensure_ascii=False)
            print(f"\n  Output → {out_path}")
            print(f"  Stats: {json.dumps(kb['stats'], indent=4)}")
            results.append({"slug": slug, "stats": kb["stats"]})

    if len(results) > 1:
        print(f"\n{'='*60}")
        print(f"  SUMMARY: Processed {len(results)} subjects")
        for r in results:
            s = r["stats"]
            print(f"    {r['slug']}: {s['total_questions']}Q, {s['total_flashcards']}FC, {s['total_exam_entries']}EQ")


if __name__ == "__main__":
    main()
