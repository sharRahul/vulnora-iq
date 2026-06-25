import type { CodeBlock } from "@/types";
import { cn } from "@/lib/utils";

interface CodeLinesProps {
  block: CodeBlock;
  /** Accent applied to highlighted lines. */
  accent: "danger" | "success";
}

/** Renders monospaced code with line numbers and soft line highlighting.
 *  Long lines wrap cleanly via the .code-wrap utility. */
export function CodeLines({ block, accent }: CodeLinesProps) {
  const lines = block.code.replace(/\n$/, "").split("\n");
  const startLine = block.startLine ?? 1;
  const highlight = new Set(block.highlightLines ?? []);
  const accentBg =
    accent === "danger"
      ? "bg-[color-mix(in_srgb,var(--sev-high)_12%,transparent)]"
      : "bg-[color-mix(in_srgb,var(--accent-sage)_14%,transparent)]";
  const accentBar =
    accent === "danger" ? "before:bg-severity-high" : "before:bg-[var(--accent-sage)]";

  return (
    <div className="overflow-x-auto scrollbar-thin rounded-md border border-border bg-canvas">
      <pre className="font-mono text-[12.5px] leading-relaxed">
        <code className="block py-2">
          {lines.map((line, i) => {
            const lineNo = startLine + i;
            const isHot = highlight.has(lineNo);
            return (
              <span
                key={i}
                className={cn(
                  "relative flex gap-3 px-3",
                  isHot &&
                    cn(
                      accentBg,
                      "before:absolute before:left-0 before:top-0 before:h-full before:w-[3px]",
                      accentBar,
                    ),
                )}
              >
                <span className="w-8 shrink-0 select-none text-right text-muted-foreground opacity-70">
                  {lineNo}
                </span>
                <span className="code-wrap flex-1 text-foreground">
                  {line || " "}
                </span>
              </span>
            );
          })}
        </code>
      </pre>
    </div>
  );
}
