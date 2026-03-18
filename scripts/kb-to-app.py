#!/usr/bin/env python3
"""
Knowledge Bridge: KB → App Content Pipeline
=============================================
Reads docs/knowledge-base/subjects/*.json, consolidates topics,
filters quality, merges with existing curated content, and writes
to src/content/subjects/*.json in the format the Astro app consumes.

Usage:
  python3 scripts/kb-to-app.py            # all subjects
  python3 scripts/kb-to-app.py --subject prosthodontics
"""

import os, sys, json, re, hashlib, argparse, datetime

OCR_CORRECTIONS = {
    "pateent": "patient", "pahent": "patient", "pahenk": "patient",
    "patienl": "patient", "palienl": "patient", "pahents": "patients",
    "denhst": "dentist", "denlure": "denture", "denlures": "dentures",
    "dentue": "denture", "denial": "dental", "denlal": "dental",
    "gengwa": "gingiva", "gengwal": "gingival", "gingwal": "gingival",
    "gengwitis": "gingivitis", "gingwitis": "gingivitis", "gingual": "gingival",
    "gengiva": "gingiva", "gengival": "gingival",
    "ocdusion": "occlusion", "ocelusion": "occlusion", "ocdusal": "occlusal",
    "retenhon": "retention", "retenhion": "retention", "retenhen": "retention",
    "restroation": "restoration", "restorahon": "restoration",
    "posternol": "posterior", "postenor": "posterior", "posterier": "posterior",
    "antenor": "anterior", "anterier": "anterior",
    "alreolar": "alveolar", "alvolar": "alveolar", "alveolare": "alveolar",
    "maxillasy": "maxillary", "waxillary": "maxillary",
    "mandibulas": "mandibular", "mandibuiar": "mandibular",
    "paratal": "palatal", "palaral": "palatal",
    "epithelum": "epithelium", "epithellum": "epithelium",
    "rissue": "tissue", "tissus": "tissue", "hissue": "tissue",
    "resorphion": "resorption", "rescription": "resorption",
    "tumar": "tumor", "diagnasis": "diagnosis", "diagmosis": "diagnosis",
    "surgicel": "surgical", "surgucal": "surgical",
    "empaction": "impaction", "impachon": "impaction",
    "encisions": "incision", "inasion": "incision",
    "fracfure": "fracture", "fraclure": "fracture",
    "plague": "plaque", "lareral": "lateral", "laleral": "lateral",
    "classificahon": "classification", "classificaton": "classification",
    "complicahons": "complications", "hemorrhuge": "hemorrhage",
    "infechon": "infection", "infechion": "infection",
    "inflammahon": "inflammation", "periodontih": "periodontal",
    "edentulious": "edentulous", "edenlulous": "edentulous",
    "ofthe": "of the", "inthe": "in the", "tothe": "to the",
    "ofteeth": "of teeth", "isthe": "is the", "onthe": "on the",
}


def spell_check(text):
    if not text:
        return text
    result = text
    for wrong, right in OCR_CORRECTIONS.items():
        pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
        def replacer(m):
            if m.group(0)[0].isupper():
                return right[0].upper() + right[1:]
            return right
        result = pattern.sub(replacer, result)
    return result

ROOT = os.path.join(os.path.dirname(__file__), "..")
KB_DIR = os.path.join(ROOT, "docs", "knowledge-base", "subjects")
APP_DIR = os.path.join(ROOT, "src", "content", "subjects")
CURATED_DIR = os.path.join(ROOT, "50_questions_eachsub")

CANONICAL_TOPICS = {
    "prosthodontics": {
        "Complete Denture Prosthodontics": ["complete denture", "denture", "edentulous", "impression", "border molding",
            "jaw relation", "centric", "occlusion rim", "try-in", "denture base", "post dam", "retention",
            "relining", "rebasing", "flabby ridge", "neutral zone", "vdo", "freeway space", "post-insertion"],
        "Removable Partial Denture": ["rpd", "partial denture", "kennedy", "clasp", "major connector", "surveyor",
            "rest seat", "indirect retainer", "path of insertion", "framework"],
        "Fixed Partial Denture": ["fpd", "crown", "bridge", "pontic", "abutment", "retainer", "connector",
            "preparation", "margin", "cement", "veneer", "inlay", "onlay", "post and core"],
        "Occlusion & Articulators": ["occlusion", "articulator", "facebow", "condylar", "bennett", "gothic arch",
            "centric relation", "lateral excursion", "protrusive"],
        "Dental Materials": ["acrylic", "pmma", "resin", "porcelain", "ceramic", "alloy", "casting",
            "wax", "investment", "gypsum", "elastomer", "alginate"],
        "Implant Prosthodontics": ["implant", "osseointegration", "fixture", "abutment screw",
            "overdenture", "implant-supported"],
        "Maxillofacial Prosthetics": ["maxillofacial", "obturator", "speech aid", "orbital", "auricular",
            "nasal prosthesis", "defect"],
    },
    "conservative-dentistry": {
        "Dental Caries": ["caries", "demineralization", "remineralization", "stephan curve", "plaque",
            "streptococcus mutans", "lactobacillus", "dmft", "icdas"],
        "Cavity Preparation": ["cavity", "preparation", "outline form", "resistance form", "retention form",
            "convenience form", "black classification", "bur", "gv black"],
        "Direct Restorations": ["amalgam", "composite", "glass ionomer", "gic", "sandwich technique",
            "acid etching", "bonding", "polymerization"],
        "Endodontics": ["pulp", "root canal", "endodontic", "pulpitis", "periapical", "obturation",
            "gutta percha", "irrigation", "working length", "apex locator", "rotary", "ni-ti",
            "sealer", "access cavity", "pulp capping", "apexification", "revascularization"],
        "Pulp Biology & Pathology": ["pulp test", "vitality", "electric pulp", "thermal test",
            "pulp necrosis", "pulp stone", "internal resorption"],
        "Bleaching & Esthetic Dentistry": ["bleaching", "whitening", "veneer", "esthetic", "shade"],
        "Dental Materials in Cons": ["liner", "varnish", "base", "cement", "temporary restoration",
            "zinc phosphate", "zinc oxide eugenol"],
    },
    "oral-surgery": {
        "Local Anesthesia": ["anesthesia", "anaesthesia", "nerve block", "infiltration", "lidocaine",
            "inferior alveolar", "mental nerve", "infraorbital", "vasoconstrictor", "adrenaline"],
        "Exodontia": ["extraction", "forceps", "elevator", "surgical extraction", "root removal",
            "complication", "dry socket", "alveolar osteitis", "hemorrhage"],
        "Impacted Teeth": ["impaction", "impacted", "third molar", "wisdom tooth", "winter",
            "pell gregory", "surgical flap", "bone removal"],
        "Odontogenic Infections": ["abscess", "cellulitis", "space infection", "ludwig", "fascial space",
            "incision drainage", "antibiotic"],
        "TMJ Disorders": ["tmj", "temporomandibular", "disc displacement", "ankylosis", "dislocation",
            "myofascial pain", "internal derangement", "arthroscopy"],
        "Maxillofacial Trauma": ["fracture", "le fort", "mandibular fracture", "zygomatic", "orbital",
            "intermaxillary fixation", "plating", "condylar fracture"],
        "Oral Pathology": ["cyst", "tumor", "ameloblastoma", "odontogenic", "keratocyst", "dentigerous",
            "radicular cyst", "ranula", "mucocele", "fibroma"],
        "Salivary Gland": ["salivary", "parotid", "submandibular", "sialolithiasis", "sialadenitis",
            "pleomorphic adenoma", "mucoepidermoid", "sjogren"],
        "Pre-prosthetic Surgery": ["pre-prosthetic", "alveoloplasty", "torus", "frenectomy",
            "vestibuloplasty", "ridge augmentation"],
    },
    "pedodontics": {
        "Child Psychology & Behavior": ["behavior management", "frankl", "tell show do", "aversive",
            "conscious sedation", "nitrous oxide", "child psychology", "anxiety", "fear"],
        "Growth & Development": ["eruption", "chronology", "nolla stages", "natal", "neonatal",
            "primary teeth", "permanent teeth", "mixed dentition", "root formation"],
        "Preventive Dentistry": ["fluoride", "sealant", "pit and fissure", "topical fluoride",
            "systemic fluoride", "fluorosis", "diet counseling", "oral hygiene"],
        "Pedodontic Restorations": ["stainless steel crown", "strip crown", "pulpotomy", "pulpectomy",
            "formocresol", "mta", "apexogenesis", "hall technique"],
        "Traumatic Injuries": ["avulsion", "intrusion", "luxation", "root fracture", "splinting",
            "replantation", "traumatic injuries", "ellis classification"],
        "Space Management": ["space maintainer", "space regainer", "band and loop", "nance",
            "lingual arch", "distal shoe", "space loss"],
        "Oral Habits": ["thumb sucking", "tongue thrusting", "bruxism", "lip biting", "mouth breathing",
            "habit breaking", "oral habit", "quad helix"],
        "Special Child": ["special needs", "disabled", "handicapped", "cerebral palsy", "down syndrome",
            "autism", "epilepsy", "medically compromised"],
    },
    "orthodontics": {
        "Growth & Development": ["growth", "cephalometric", "cephalogram", "downs analysis", "steiner",
            "tweed", "mcnamara", "wits appraisal", "sn plane", "frankfort", "anb angle"],
        "Classification of Malocclusion": ["angle classification", "class i", "class ii", "class iii",
            "malocclusion", "overjet", "overbite", "crossbite", "open bite"],
        "Diagnostic Records": ["study model", "model analysis", "bolton analysis", "pont index",
            "radiograph", "opg", "lateral cephalogram", "photograph"],
        "Removable Appliances": ["removable appliance", "active plate", "hawley", "retainer",
            "adam clasp", "labial bow", "expansion screw", "functional appliance"],
        "Fixed Appliances": ["bracket", "archwire", "molar band", "edgewise", "begg", "mbt",
            "roth", "preadjusted", "ni-ti", "stainless steel", "anchorage"],
        "Functional Appliances": ["functional appliance", "activator", "bionator", "twin block",
            "frankel", "herbst", "myofunctional"],
        "Orthognathic Surgery": ["orthognathic", "le fort", "bsso", "genioplasty", "surgical orthodontics",
            "decompensation"],
        "Interceptive Orthodontics": ["serial extraction", "space management", "crossbite correction",
            "habit breaking", "interceptive"],
    },
    "periodontics": {
        "Anatomy of Periodontium": ["gingiva", "periodontal ligament", "pdl", "cementum", "alveolar bone",
            "junctional epithelium", "col", "attached gingiva", "free gingival groove"],
        "Etiology of Periodontal Disease": ["plaque", "calculus", "biofilm", "subgingival", "supragingival",
            "periodontal pathogen", "red complex", "aggregatibacter"],
        "Classification of Periodontal Disease": ["chronic periodontitis", "aggressive periodontitis",
            "gingivitis", "necrotizing", "classification", "staging", "grading"],
        "Periodontal Diagnosis": ["probing depth", "attachment loss", "bleeding on probing", "mobility",
            "furcation", "radiographic bone loss", "periodontal charting"],
        "Non-Surgical Therapy": ["scaling", "root planing", "curettage", "ultrasonic", "hand instruments",
            "gracey curette", "debridement"],
        "Surgical Therapy": ["flap surgery", "gingivectomy", "osseous surgery", "guided tissue regeneration",
            "gtr", "bone graft", "membrane", "mucogingival surgery", "free gingival graft"],
        "Systemic-Periodontal Connection": ["diabetes", "pregnancy", "hiv", "smoking", "cardiovascular",
            "systemic disease", "drug-induced", "phenytoin"],
        "Periodontal Medicine": ["chemotherapeutic", "chlorhexidine", "antibiotic", "local drug delivery",
            "host modulation", "doxycycline"],
    },
    "public-health-dentistry": {
        "Epidemiology": ["epidemiology", "prevalence", "incidence", "morbidity", "mortality",
            "risk factor", "odds ratio", "relative risk", "study design"],
        "Biostatistics": ["mean", "median", "standard deviation", "chi square", "t-test",
            "anova", "p-value", "confidence interval", "sample size"],
        "Dental Indices": ["dmft", "def", "opi", "cpi", "dean", "fluorosis index",
            "oral hygiene index", "gingival index", "plaque index", "russell"],
        "Preventive Dentistry": ["fluoride", "water fluoridation", "fluoride varnish", "sealant",
            "preventive", "atraumatic", "art", "diet counseling"],
        "Dental Public Health Programs": ["school dental health", "national oral health", "who",
            "primary health center", "community dentistry", "dental camps"],
        "Health Education & Promotion": ["health education", "health promotion", "ottawa charter",
            "behavior change", "iec", "mass media"],
        "Research Methodology": ["research design", "sampling", "questionnaire", "survey",
            "clinical trial", "randomized", "blinding", "bias"],
        "Forensic Dentistry": ["forensic", "age estimation", "bite mark", "identification",
            "dental records", "mass disaster"],
    },
    "oral-medicine": {
        "Ulcerative Lesions": ["aphthous", "ulcer", "rau", "bechet", "pemphigus", "pemphigoid",
            "erythema multiforme", "steven johnson", "lichen planus erosive"],
        "Vesiculobullous Lesions": ["pemphigus vulgaris", "bullous pemphigoid", "bullae",
            "nikolsky sign", "tzanck cell", "acantholysis"],
        "White Lesions": ["leukoplakia", "lichen planus", "candidiasis", "white sponge nevus",
            "oral submucous fibrosis", "osmf", "hairy leukoplakia"],
        "Red Lesions": ["erythroplakia", "erythema", "geographic tongue", "median rhomboid"],
        "Viral Infections": ["herpes simplex", "herpes zoster", "hiv", "hpv", "measles",
            "mumps", "hand foot mouth", "herpangina"],
        "Fungal Infections": ["candida", "candidiasis", "thrush", "angular cheilitis",
            "denture stomatitis", "chronic hyperplastic"],
        "Bacterial Infections": ["tuberculosis", "syphilis", "actinomycosis", "noma", "anug"],
        "Salivary Gland Disorders": ["xerostomia", "sjogren", "mucocele", "ranula", "sialadenitis",
            "sialolithiasis", "pleomorphic adenoma"],
        "TMJ Disorders": ["tmj", "myofascial pain", "internal derangement", "ankylosis",
            "disc displacement", "bruxism", "trismus"],
        "Premalignant & Malignant Lesions": ["oral cancer", "squamous cell carcinoma", "tnm staging",
            "premalignant", "precancerous", "dysplasia", "biopsy", "tobacco"],
        "Oral Manifestations of Systemic Disease": ["diabetes", "anemia", "hiv", "leukemia",
            "vitamin deficiency", "plummer vinson", "paget"],
        "Oral Radiology": ["radiograph", "opg", "cbct", "periapical", "bitewing", "occlusal",
            "cephalogram", "radiation protection", "dosimetry", "processing"],
    },
}

DEFAULT_TOPICS = {
    "General": ["general"],
}


def concept_hash(text):
    normalized = re.sub(r'[^a-z0-9\s]', '', text.lower().strip())
    normalized = re.sub(r'\s+', ' ', normalized)
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def assign_canonical_topic(question_text, answer_text, subject_slug):
    topics_map = CANONICAL_TOPICS.get(subject_slug, DEFAULT_TOPICS)
    combined = (question_text + " " + answer_text).lower()

    best_topic = "Miscellaneous"
    best_score = 0

    for topic_name, keywords in topics_map.items():
        score = sum(1 for kw in keywords if kw in combined)
        weighted = score
        for kw in keywords:
            if kw in question_text.lower():
                weighted += 2
        if weighted > best_score:
            best_score = weighted
            best_topic = topic_name

    if best_score == 0 and len(answer_text) > 50:
        answer_lower = answer_text[:300].lower()
        for topic_name, keywords in topics_map.items():
            for kw in keywords:
                if kw in answer_lower:
                    return topic_name

    return best_topic


def clean_answer(text):
    """Clean OCR artifacts and spell-check answer text."""
    text = re.sub(r'^Page \d+ of \d+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\s+of\s+\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[>]\s*\n', '\n', text)
    text = spell_check(text)
    text = text.strip()
    if len(text) > 2000:
        text = text[:2000] + "..."
    return text


def clean_question(text):
    """Clean and spell-check question text."""
    text = spell_check(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def quality_filter(question, answer):
    """Return True if the Q&A pair is worth showing to students."""
    if len(answer) < 40:
        return False
    if len(question) < 10:
        return False

    words = answer.split()
    if len(words) < 8:
        return False
    real_words = sum(1 for w in words[:50] if re.match(r'^[A-Za-z]{2,}$', w))
    readability = real_words / min(len(words), 50)
    if readability < 0.3:
        return False

    garble = sum(1 for c in answer[:200] if c in '~\\^{}|')
    if garble > 10:
        return False

    return True


def load_existing_app_content(slug):
    """Load existing curated app content to preserve it."""
    path = os.path.join(APP_DIR, f"{slug}.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_kb(slug):
    path = os.path.join(KB_DIR, f"{slug}.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_app_content(slug):
    """Build app-ready content for one subject."""
    kb = load_kb(slug)
    existing = load_existing_app_content(slug)

    seen_hashes = set()
    questions = []

    if existing and existing.get("questions"):
        for q in existing["questions"]:
            h = concept_hash(q.get("question", ""))
            seen_hashes.add(h)
            cleaned_q = {
                **q,
                "question": clean_question(q.get("question", "")),
                "answer": clean_answer(q.get("answer", "")),
                "topic": assign_canonical_topic(
                    q.get("question", ""), q.get("answer", ""), slug
                ) if q.get("topic", "") in ("General", "general", "Miscellaneous") else q.get("topic", ""),
            }
            questions.append(cleaned_q)
        print(f"  Refreshed {len(questions)} existing questions (spell-check + topic fix)")

    if kb:
        exam_entries = []
        for et in ["short_answer", "long_essay", "viva"]:
            exam_entries.extend(kb.get("exam_bank", {}).get(et, []))

        ocr_added = 0
        for entry in exam_entries:
            q_text = entry.get("question", "")
            answer = entry.get("model_answer", "") or entry.get("answer", "")

            if not quality_filter(q_text, answer):
                continue

            h = concept_hash(q_text)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            clean_q = clean_question(q_text)
            clean_ans = clean_answer(answer)
            topic = assign_canonical_topic(clean_q, clean_ans, slug)

            questions.append({
                "id": entry.get("source_question_id", entry.get("exam_q_id", f"kb-{slug}-{len(questions)}")),
                "topic": topic,
                "question": clean_q,
                "answer": clean_ans,
                "highYield": entry.get("high_yield", False),
                "yearsAsked": [],
            })
            ocr_added += 1

        if ocr_added:
            print(f"  Added {ocr_added} new questions from KB (after quality filter + dedup)")

        flashcards = kb.get("flashcards", [])
        for fc in flashcards:
            q_text = fc.get("front", "")
            answer = fc.get("back", "")

            if not quality_filter(q_text, answer):
                continue

            h = concept_hash(q_text)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            clean_ans = clean_answer(answer)
            topic = assign_canonical_topic(q_text, clean_ans, slug)

            questions.append({
                "id": fc.get("card_id", f"fc-{slug}-{len(questions)}"),
                "topic": topic,
                "question": q_text,
                "answer": clean_ans,
                "highYield": fc.get("high_yield", False),
                "yearsAsked": [],
            })

    topic_counts = {}
    for q in questions:
        topic_counts[q["topic"]] = topic_counts.get(q["topic"], 0) + 1

    questions.sort(key=lambda q: (-int(q.get("highYield", False)), q.get("topic", ""), q.get("id", "")))

    existing_maps = existing.get("mindMaps", []) if existing else []
    existing_resources = existing.get("resources", []) if existing else []

    output = {
        "slug": slug,
        "questions": questions,
        "mindMaps": existing_maps,
        "resources": existing_resources,
    }

    return output, topic_counts


def main():
    parser = argparse.ArgumentParser(description="Bridge KB data to app content")
    parser.add_argument("--subject", help="Single subject slug")
    args = parser.parse_args()

    os.makedirs(APP_DIR, exist_ok=True)

    all_slugs = [
        "prosthodontics", "conservative-dentistry", "oral-surgery",
        "pedodontics", "orthodontics", "public-health-dentistry",
        "periodontics", "oral-medicine",
    ]

    slugs = [args.subject] if args.subject else all_slugs

    print(f"Knowledge Bridge: KB → App Content")
    print(f"{'='*60}")

    total_before = 0
    total_after = 0

    for slug in slugs:
        print(f"\n  [{slug}]")

        existing = load_existing_app_content(slug)
        before = len(existing.get("questions", [])) if existing else 0
        total_before += before

        output, topic_counts = build_app_content(slug)
        after = len(output["questions"])
        total_after += after

        out_path = os.path.join(APP_DIR, f"{slug}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"  Before: {before} questions → After: {after} questions (+{after - before})")
        print(f"  Topics: {len(topic_counts)}")
        for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1])[:8]:
            print(f"    {topic}: {count}Q")
        print(f"  → {out_path}")

    print(f"\n{'='*60}")
    print(f"  TOTAL: {total_before} → {total_after} questions (+{total_after - total_before})")
    print(f"  Subjects: {len(slugs)}")


if __name__ == "__main__":
    main()
