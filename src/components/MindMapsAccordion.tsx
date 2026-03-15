import { useState, useId } from "react";
import MermaidDiagram from "./MermaidDiagram";

export interface MindMapItem {
  id: string;
  title: string;
  mermaid: string;
  relatedQuestionIds?: string[];
}

interface MindMapsAccordionProps {
  mindMaps: MindMapItem[];
}

export default function MindMapsAccordion({ mindMaps }: MindMapsAccordionProps) {
  const [openId, setOpenId] = useState<string | null>(null);
  const baseId = useId();

  if (!mindMaps.length) return null;

  return (
    <div className="space-y-3" role="region" aria-label="Mind maps">
      {mindMaps.map((mm) => {
        const isOpen = openId === mm.id;
        const panelId = `${baseId}-mm-${mm.id}`;
        const triggerId = `${baseId}-trigger-${mm.id}`;

        return (
          <div
            key={mm.id}
            className="content-card overflow-hidden transition-all duration-200 ease-out"
            style={{
              borderColor: isOpen ? "rgba(88, 166, 255, 0.3)" : "var(--border-color)",
            }}
          >
            <button
              type="button"
              onClick={() => setOpenId(isOpen ? null : mm.id)}
              className="w-full text-left px-4 sm:px-5 py-4 flex items-center gap-3 min-h-[44px] touch-manipulation"
              aria-expanded={isOpen}
              aria-controls={panelId}
              id={triggerId}
              style={{ color: "var(--text-primary)" }}
            >
              <span
                className={`shrink-0 text-xs transition-transform duration-200 ease-out ${isOpen ? "rotate-90" : ""}`}
                style={{ color: "var(--accent-1)" }}
                aria-hidden
              >
                ▶
              </span>
              <span className="text-sm sm:text-base font-semibold leading-snug">
                {mm.title}
              </span>
            </button>

            <div
              id={panelId}
              role="region"
              aria-labelledby={triggerId}
              className="grid transition-[grid-template-rows] duration-300 ease-out"
              style={{
                gridTemplateRows: isOpen ? "1fr" : "0fr",
              }}
            >
              <div className="min-h-0 overflow-hidden">
                <div
                  className="border-t px-4 sm:px-5 pb-4 pt-2 transition-opacity duration-200"
                  style={{
                    borderColor: "var(--border-color)",
                    opacity: isOpen ? 1 : 0,
                  }}
                >
                  {isOpen && (
                    <MermaidDiagram chart={mm.mermaid} title={mm.title} showTitle={false} />
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
