/**
 * Ingest subject questions from 50_questions_eachsub/*.json into src/content/subjects/*.json
 *
 * Usage: node scripts/ingest-subject.cjs <source-file> [output-slug]
 *
 * Example: node scripts/ingest-subject.cjs 50_questions_eachsub/omfs.json oral-surgery
 *
 * Source format: topics[].{id, name}, questions[].{id, topic, question, answer, highYield, ...}
 * Output format: slug, questions[].{id, topic (display name), question, answer, highYield, yearsAsked?, analogy?}
 */

const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");

function main() {
  const sourcePath = process.argv[2];
  const outputSlug = process.argv[3];

  if (!sourcePath) {
    console.error("Usage: node scripts/ingest-subject.cjs <source-file> [output-slug]");
    process.exit(1);
  }

  const fullSourcePath = path.isAbsolute(sourcePath)
    ? sourcePath
    : path.join(ROOT, sourcePath);

  if (!fs.existsSync(fullSourcePath)) {
    console.error("Source file not found:", fullSourcePath);
    process.exit(1);
  }

  const raw = JSON.parse(fs.readFileSync(fullSourcePath, "utf8"));

  const topicMap = new Map();
  for (const t of raw.topics || []) {
    if (t.id && t.name) topicMap.set(t.id, t.name);
  }

  const questions = (raw.questions || []).map((q) => {
    const topicName = topicMap.get(q.topic) ?? q.topic;
    const out = {
      id: String(q.id ?? ""),
      topic: topicName,
      question: String(q.question ?? ""),
      answer: String(q.answer ?? ""),
      highYield: q.highYield === true || q.highYield === "true",
      yearsAsked: Array.isArray(q.yearsAsked) ? q.yearsAsked : [],
    };
    if (q.analogy != null) out.analogy = String(q.analogy);
    return out;
  });

  const slugMap = {
    "oral-maxillofacial-surgery": "oral-surgery",
    "conservative-dentistry-endodontics": "conservative-dentistry",
    prosthodontics: "prosthodontics",
  };
  const subjectId = (raw.subjectId || "").toLowerCase().trim();
  const derived =
    slugMap[subjectId] ||
    subjectId.replace(/[^a-z0-9-]/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "") ||
    "unknown";
  const slug = outputSlug || derived;

  const output = {
    slug,
    questions,
    mindMaps: Array.isArray(raw.mindMaps) ? raw.mindMaps : [],
    resources: Array.isArray(raw.resources) ? raw.resources : [],
  };

  const outPath = path.join(ROOT, "src/content/subjects", `${slug}.json`);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2), "utf8");

  console.log(`Ingested ${questions.length} questions → ${outPath}`);
}

main();
