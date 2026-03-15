import type { ReactNode } from "react";
import React from "react";

/**
 * Normalize answer text: break before (1) (2) etc. for numbered lists.
 */
export function normalizeAnswerSpacing(text: string): string {
  let out = text;
  out = out.replace(/([:.])\s*(\(\d{1,2}\)\s+)/g, "$1\n\n$2");
  out = out.replace(/\s+(\(\d{1,2}\)\s+)/g, "\n\n$1");
  return out;
}

/** Render one segment with **bold** → <strong>. */
function formatSegment(segment: string, keyPrefix: string): ReactNode {
  if (!segment.trim()) return null;
  const parts: ReactNode[] = [];
  const re = /\*\*([^*]+)\*\*/g;
  let lastIndex = 0;
  let match;
  while ((match = re.exec(segment)) !== null) {
    if (match.index > lastIndex) {
      parts.push(segment.slice(lastIndex, match.index));
    }
    parts.push(<strong key={`${keyPrefix}-b-${match.index}`}>{match[1]}</strong>);
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < segment.length) parts.push(segment.slice(lastIndex));
  return parts.length === 1 && typeof parts[0] === "string" ? parts[0] : parts;
}

/** One paragraph: **bold** and \n as line breaks. */
export function formatParagraph(para: string, keyPrefix: string): ReactNode {
  if (!para.trim()) return null;
  const lines = para.split("\n");
  if (lines.length <= 1) {
    return formatSegment(para, keyPrefix);
  }
  return (
    <span className="block">
      {lines.map((line, i) => (
        <span key={`${keyPrefix}-l-${i}`} className="block mb-1 last:mb-0">
          {formatSegment(line.trim(), `${keyPrefix}-${i}`)}
        </span>
      ))}
    </span>
  );
}

/** Full answer: **bold**, \n\n paragraphs, numbered list spacing. */
export function formatAnswer(text: string): ReactNode {
  if (!text) return null;
  const normalized = normalizeAnswerSpacing(text);
  const paragraphs = normalized.split(/\n\n+/).map((p) => p.trim()).filter(Boolean);
  if (paragraphs.length <= 1) {
    const para = paragraphs[0] ?? text;
    return (
      <div className="answer-body space-y-2">
        <p className="mb-0 leading-relaxed">{formatParagraph(para, "0")}</p>
      </div>
    );
  }
  return (
    <div className="answer-body space-y-4">
      {paragraphs.map((para, i) => (
        <p key={`p-${i}`} className="mb-0 leading-relaxed">
          {formatParagraph(para, `p-${i}`)}
        </p>
      ))}
    </div>
  );
}
