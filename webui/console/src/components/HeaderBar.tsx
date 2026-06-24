import {
  LayoutDashboard,
  Loader2,
  Moon,
  PanelsTopLeft,
  Server,
  Play,
  ShieldHalf,
  Sun,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type ConsoleView = "overview" | "workspace" | "targets";

interface HeaderBarProps {
  view: ConsoleView;
  onChangeView: (view: ConsoleView) => void;
  theme: "light" | "dark";
  onToggleTheme: () => void;
  scanning: boolean;
  scanStatusLabel?: string;
  scanProgressPercent?: number;
  scanFindingCount?: number;
  onToggleScan: () => void;
}

export function HeaderBar({
  view,
  onChangeView,
  theme,
  onToggleTheme,
  scanning,
  scanStatusLabel,
  scanProgressPercent = 0,
  scanFindingCount = 0,
  onToggleScan,
}: HeaderBarProps) {
  const scanLabel = scanning
    ? `${scanStatusLabel || "Scan running"} · ${Math.round(scanProgressPercent)}% · ${scanFindingCount} findings`
    : "Idle";

  return (
    <header className="flex h-14 shrink-0 items-center gap-3 border-b border-border bg-card px-3 sm:px-4">
      <div className="flex items-center gap-2">
        <span className="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
          <ShieldHalf className="size-5" />
        </span>
        <div className="leading-none">
          <p className="font-sans text-sm font-extrabold tracking-tight text-foreground">
            VulnorAIQ
          </p>
          <p className="hidden text-[10px] font-medium uppercase tracking-wide text-muted-foreground sm:block">
            AI Security Operations
          </p>
        </div>
      </div>

      <nav className="ml-2 flex items-center gap-1 rounded-md border border-border bg-muted p-0.5">
        <ViewTab
          active={view === "overview"}
          onClick={() => onChangeView("overview")}
          icon={<LayoutDashboard className="size-4" />}
          label="Overview"
        />
        <ViewTab
          active={view === "workspace"}
          onClick={() => onChangeView("workspace")}
          icon={<PanelsTopLeft className="size-4" />}
          label="Workspace"
        />
        <ViewTab
          active={view === "targets"}
          onClick={() => onChangeView("targets")}
          icon={<Server className="size-4" />}
          label="Targets"
        />
      </nav>

      <div className="ml-auto flex items-center gap-2">
        <span className="hidden max-w-[340px] items-center gap-1.5 truncate rounded-md border border-border bg-canvas px-2 py-1 text-[11px] font-semibold text-muted-foreground md:inline-flex">
          <span
            className={cn(
              "size-1.5 shrink-0 rounded-full",
              scanning ? "animate-pulse bg-[var(--accent-sage)]" : "bg-muted-foreground/50",
            )}
          />
          <span className="truncate">{scanLabel}</span>
        </span>

        <Button variant="primary" size="sm" onClick={onToggleScan} disabled={scanning}>
          {scanning ? (
            <>
              <Loader2 className="size-4 animate-spin" /> Scanning…
            </>
          ) : (
            <>
              <Play className="size-4" /> Run Scan
            </>
          )}
        </Button>

        <Button
          variant="secondary"
          size="icon"
          onClick={onToggleTheme}
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
        >
          {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
        </Button>
      </div>
    </header>
  );
}

function ViewTab({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        "inline-flex items-center gap-1.5 rounded px-2.5 py-1.5 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        active
          ? "bg-card text-foreground shadow-card"
          : "text-muted-foreground hover:text-foreground",
      )}
    >
      {icon}
      <span className="hidden sm:inline">{label}</span>
    </button>
  );
}
