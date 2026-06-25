import { FileWarning } from "lucide-react";
import type { CodeBlock } from "@/types";
import { CodeLines } from "./CodeLines";

export function VulnerableCodeBlock({ block }: { block: CodeBlock }) {
  return (
    <section className="overflow-hidden rounded-lg border border-severity-high/40 bg-card shadow-card">
      <header className="flex items-center gap-2 border-b border-border bg-[color-mix(in_srgb,var(--sev-high)_8%,transparent)] px-3 py-2">
        <FileWarning className="size-4 text-severity-high" />
        <span className="text-xs font-bold uppercase tracking-wide text-severity-high">
          Vulnerable Code
        </span>
        {block.language && (
          <span className="rounded border border-border bg-card/80 px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
            {block.language}
          </span>
        )}
        <span className="ml-auto truncate font-mono text-[11px] text-muted-foreground">
          {block.filename}
        </span>
      </header>
      <div className="p-3">
        <CodeLines block={block} accent="danger" />
      </div>
    </section>
  );
}
