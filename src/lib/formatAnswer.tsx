import type { ReactNode } from "react";
import React from "react";
import { spellCheckDental } from "./dentalSpellCheck";

interface ParsedBlock {
  type: "heading" | "subheading" | "numbered" | "bullet" | "clinical-pearl" | "paragraph";
  text: string;
  indent?: number;
}

const CLINICAL_PEARL_KEYWORDS = [
  "most common", "gold standard", "treatment of choice", "drug of choice",
  "most important", "pathognomonic", "hallmark", "diagnostic feature",
  "first line", "investigation of choice",
];

const HEADING_PATTERNS = [
  /^[A-Z][A-Z\s&\-/]{4,}$/,
  /^[A-Z][A-Z\s&\-/]{2,}\s*[:–-]\s*$/,
];

const SUBHEADING_PATTERNS = [
  /^[A-Z][a-z]+(?:\s+[A-Za-z]+){0,4}\s*[:–-]\s*/,
  /^(?:Types?|Causes?|Features?|Signs?|Symptoms?|Treatment|Management|Diagnosis|Etiology|Classification|Advantages?|Disadvantages?|Indications?|Contraindications?|Properties|Composition|Technique|Procedure|Prognosis|Complications?|Prevention)\s*[:–-]?\s*$/i,
];

function classifyLine(line: string): ParsedBlock {
  const trimmed = line.trim();

  if (!trimmed) return { type: "paragraph", text: "" };

  if (HEADING_PATTERNS.some((p) => p.test(trimmed))) {
    return { type: "heading", text: trimmed.replace(/[:–-]\s*$/, "").trim() };
  }

  if (SUBHEADING_PATTERNS.some((p) => p.test(trimmed))) {
    return { type: "subheading", text: trimmed.replace(/[:–-]\s*$/, "").trim() };
  }

  const numberedMatch = trimmed.match(
    /^(?:(\d{1,2})\)|(\d{1,2})\.\s|\((\d{1,2})\)\s|([a-z])\)\s|\(([a-z])\)\s|([ivx]+)\)\s)/i
  );
  if (numberedMatch) {
    const label = (numberedMatch[1] || numberedMatch[2] || numberedMatch[3] ||
      numberedMatch[4] || numberedMatch[5] || numberedMatch[6] || "").trim();
    const content = trimmed.slice(numberedMatch[0].length).trim();
    const subMatch = label.match(/^[a-z]$/i) || label.match(/^[ivx]+$/i);
    return {
      type: "numbered",
      text: content,
      indent: subMatch ? 2 : 1,
    };
  }

  if (/^[>•\-–→▸]\s/.test(trimmed)) {
    const content = trimmed.replace(/^[>•\-–→▸]\s*/, "").trim();
    return { type: "bullet", text: content };
  }

  if (/^[-–]\s/.test(trimmed)) {
    return { type: "bullet", text: trimmed.replace(/^[-–]\s*/, "").trim() };
  }

  const isClinicalPearl = CLINICAL_PEARL_KEYWORDS.some(
    (kw) => trimmed.toLowerCase().includes(kw)
  );
  if (isClinicalPearl) {
    return { type: "clinical-pearl", text: trimmed };
  }

  return { type: "paragraph", text: trimmed };
}

function renderBoldText(text: string, keyPrefix: string): ReactNode {
  const parts: ReactNode[] = [];
  const re = /\*\*([^*]+)\*\*/g;
  let lastIndex = 0;
  let match;
  while ((match = re.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    parts.push(
      <strong key={`${keyPrefix}-b-${match.index}`} className="answer-bold">
        {match[1]}
      </strong>
    );
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) parts.push(text.slice(lastIndex));
  return parts.length === 1 && typeof parts[0] === "string" ? parts[0] : <>{parts}</>;
}

function renderBlock(block: ParsedBlock, index: number): ReactNode {
  const key = `block-${index}`;

  switch (block.type) {
    case "heading":
      return (
        <h4 key={key} className="answer-heading">
          {renderBoldText(block.text, key)}
        </h4>
      );

    case "subheading":
      return (
        <h5 key={key} className="answer-subheading">
          {renderBoldText(block.text, key)}
        </h5>
      );

    case "numbered":
      return (
        <div
          key={key}
          className={`answer-numbered ${block.indent === 2 ? "answer-numbered-sub" : ""}`}
        >
          <span className="answer-bullet-marker">
            {block.indent === 2 ? "◦" : "●"}
          </span>
          <span>{renderBoldText(block.text, key)}</span>
        </div>
      );

    case "bullet":
      return (
        <div key={key} className="answer-bullet">
          <span className="answer-bullet-marker">▸</span>
          <span>{renderBoldText(block.text, key)}</span>
        </div>
      );

    case "clinical-pearl":
      return (
        <div key={key} className="answer-clinical-pearl">
          <span className="answer-pearl-icon">💎</span>
          <span>{renderBoldText(block.text, key)}</span>
        </div>
      );

    case "paragraph":
    default:
      if (!block.text) return null;
      return (
        <p key={key} className="answer-paragraph">
          {renderBoldText(block.text, key)}
        </p>
      );
  }
}

export function normalizeAnswerSpacing(text: string): string {
  let out = text;
  out = out.replace(/([:.])\s*(\(\d{1,2}\)\s+)/g, "$1\n\n$2");
  out = out.replace(/\s+(\(\d{1,2}\)\s+)/g, "\n\n$1");
  return out;
}

export function formatParagraph(para: string, keyPrefix: string): ReactNode {
  if (!para.trim()) return null;
  const corrected = spellCheckDental(para);
  const lines = corrected.split("\n");
  if (lines.length <= 1) {
    return renderBoldText(corrected, keyPrefix);
  }
  return (
    <span className="block">
      {lines.map((line, i) => (
        <span key={`${keyPrefix}-l-${i}`} className="block mb-1 last:mb-0">
          {renderBoldText(line.trim(), `${keyPrefix}-${i}`)}
        </span>
      ))}
    </span>
  );
}

export function formatAnswer(text: string): ReactNode {
  if (!text) return null;

  const corrected = spellCheckDental(text);
  const normalized = normalizeAnswerSpacing(corrected);
  const lines = normalized.split("\n");

  const blocks: ParsedBlock[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    blocks.push(classifyLine(trimmed));
  }

  if (blocks.length === 0) return null;

  if (blocks.length === 1 && blocks[0].type === "paragraph") {
    return (
      <div className="answer-body">
        <p className="answer-paragraph">{renderBoldText(blocks[0].text, "0")}</p>
      </div>
    );
  }

  return (
    <div className="answer-body">
      {blocks.map((block, i) => renderBlock(block, i))}
    </div>
  );
}
