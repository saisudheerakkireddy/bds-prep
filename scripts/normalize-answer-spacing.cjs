/**
 * Normalize answer spacing in subject JSON files.
 * Inserts \n\n before numbered list items " (1) " " (2) " ... so paragraphs render clearly.
 * Conservative: only matches space + (N) + space where N is 1-2 digits (avoids breaking ratios like 1:1).
 */
const fs = require("fs");
const path = require("path");

const SUBJECTS_DIR = path.join(__dirname, "../src/content/subjects");
const FILES = [
  "prosthodontics.json",
  "conservative-dentistry.json",
  "oral-surgery.json",
  "public-health-dentistry.json",
];

function normalizeAnswer(text) {
  if (!text || typeof text !== "string") return text;
  let out = text;
  // Insert paragraph break before " (1) " " (2) " ... " (99) " (space, open paren, 1-2 digits, close paren, space)
  // So "intro (1) first (2) second" -> "intro\n\n(1) first\n\n(2) second"
  out = out.replace(/\s+(\(\d{1,2}\)\s+)/g, "\n\n$1");
  // Collapse any triple+ newlines back to double
  out = out.replace(/\n{3,}/g, "\n\n");
  return out.trim();
}

let total = 0;
for (const file of FILES) {
  const filePath = path.join(SUBJECTS_DIR, file);
  if (!fs.existsSync(filePath)) continue;
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
  if (!Array.isArray(data.questions)) continue;
  let count = 0;
  for (const q of data.questions) {
    if (q.answer) {
      const before = q.answer;
      q.answer = normalizeAnswer(q.answer);
      if (q.answer !== before) count++;
    }
  }
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf8");
  console.log(`${file}: normalized ${count} answers (${data.questions.length} total)`);
  total += data.questions.length;
}
console.log(`Done. Total questions across files: ${total}`);
