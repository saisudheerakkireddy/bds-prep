import { useEffect, useRef, useState } from "react";

interface MermaidDiagramProps {
  chart: string;
  title?: string;
  /** When false, title is not rendered (e.g. when used inside an accordion that shows the title). aria-label still uses title. */
  showTitle?: boolean;
}

export default function MermaidDiagram({ chart, title, showTitle = true }: MermaidDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>("");
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(false);

    async function render() {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: "dark",
          fontFamily: "Outfit, sans-serif",
          themeVariables: {
            fontSize: "18px",
            fontFamily: "Outfit, sans-serif",
          },
          flowchart: {
            curve: "basis",
            padding: 20,
            useMaxWidth: true,
            nodeSpacing: 50,
            rankSpacing: 50,
          },
        });
        const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`;
        const { svg: rendered } = await mermaid.render(id, chart);
        if (!cancelled) {
          setSvg(rendered);
          setLoading(false);
        }
      } catch {
        if (!cancelled) {
          setError(true);
          setLoading(false);
        }
      }
    }

    render();
    return () => {
      cancelled = true;
    };
  }, [chart]);

  if (error) {
    return (
      <div
        className="content-card rounded-xl p-4 text-sm"
        style={{ color: "var(--text-secondary)" }}
        role="status"
      >
        Diagram could not be rendered.
      </div>
    );
  }

  const ariaLabel = title ?? "Concept diagram";

  return (
    <div
      className="content-card rounded-xl overflow-hidden"
      role="img"
      aria-label={ariaLabel}
    >
      {showTitle && title && (
        <div
          className="px-4 py-2.5 border-b"
          style={{ borderColor: "var(--border-color)", background: "rgba(0,0,0,0.2)" }}
        >
          <h4 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{title}</h4>
        </div>
      )}
      <div
        ref={containerRef}
        className="mermaid-diagram-wrapper p-4 min-h-[120px] flex items-center justify-center w-full"
        aria-hidden={loading ? undefined : "true"}
      >
        {loading ? (
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Loading diagram…</p>
        ) : (
          <div className="mermaid-diagram-svg" dangerouslySetInnerHTML={{ __html: svg }} />
        )}
      </div>
    </div>
  );
}
