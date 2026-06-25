import { useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  PanelLeftClose,
  PanelRightClose,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface WorkspaceLayoutProps {
  left: React.ReactNode;
  middle: React.ReactNode;
  right: React.ReactNode;
}

type MobileTab = "nav" | "analysis" | "intel";

export function WorkspaceLayout({ left, middle, right }: WorkspaceLayoutProps) {
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);
  const [mobileTab, setMobileTab] = useState<MobileTab>("analysis");

  return (
    <div className="h-full">
      {/* Desktop / tablet tri-pane */}
      <div className="hidden h-full md:flex">
        {/* Left pane */}
        {leftOpen ? (
          <aside className="flex w-[300px] shrink-0 flex-col border-r border-border bg-canvas xl:w-[340px]">
            <div className="flex-1 overflow-hidden">{left}</div>
            <PaneFooter
              label="Collapse navigator"
              icon={<PanelLeftClose className="size-4" />}
              onClick={() => setLeftOpen(false)}
            />
          </aside>
        ) : (
          <RailExpand
            side="left"
            label="Assets"
            onClick={() => setLeftOpen(true)}
          />
        )}

        {/* Middle pane */}
        <section className="min-w-0 flex-1 overflow-hidden bg-canvas">{middle}</section>

        {/* Right pane */}
        {rightOpen ? (
          <aside className="flex w-[340px] shrink-0 flex-col border-l border-border bg-canvas xl:w-[380px]">
            <div className="flex-1 overflow-hidden">{right}</div>
            <PaneFooter
              label="Collapse intelligence"
              icon={<PanelRightClose className="size-4" />}
              onClick={() => setRightOpen(false)}
            />
          </aside>
        ) : (
          <RailExpand
            side="right"
            label="Intel"
            onClick={() => setRightOpen(true)}
          />
        )}
      </div>

      {/* Mobile: stacked tabbed panes */}
      <div className="flex h-full flex-col md:hidden">
        <div className="grid shrink-0 grid-cols-3 gap-1 border-b border-border bg-card p-1.5">
          <MobileTabButton active={mobileTab === "nav"} onClick={() => setMobileTab("nav")}>
            Assets
          </MobileTabButton>
          <MobileTabButton active={mobileTab === "analysis"} onClick={() => setMobileTab("analysis")}>
            Analysis
          </MobileTabButton>
          <MobileTabButton active={mobileTab === "intel"} onClick={() => setMobileTab("intel")}>
            Intel
          </MobileTabButton>
        </div>
        <div className="min-h-0 flex-1 overflow-hidden">
          {mobileTab === "nav" && left}
          {mobileTab === "analysis" && middle}
          {mobileTab === "intel" && right}
        </div>
      </div>
    </div>
  );
}

function PaneFooter({
  label,
  icon,
  onClick,
}: {
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <div className="shrink-0 border-t border-border bg-muted p-1.5">
      <Button
        variant="ghost"
        size="sm"
        className="w-full justify-start gap-2 text-xs text-muted-foreground hover:text-foreground"
        onClick={onClick}
      >
        {icon}
        <span>{label}</span>
      </Button>
    </div>
  );
}

function RailExpand({
  side,
  label,
  onClick,
}: {
  side: "left" | "right";
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      aria-label={`Expand ${label} pane`}
      className={cn(
        "flex w-10 shrink-0 flex-col items-center gap-2 bg-canvas py-3 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        side === "left" ? "border-r border-border" : "border-l border-border",
      )}
    >
      {side === "left" ? (
        <ChevronRight className="size-4" />
      ) : (
        <ChevronLeft className="size-4" />
      )}
      <span
        className="text-[11px] font-bold uppercase tracking-wide"
        style={{ writingMode: "vertical-rl" }}
      >
        {label}
      </span>
    </button>
  );
}

function MobileTabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        "rounded px-2 py-1.5 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        active
          ? "bg-primary text-primary-foreground"
          : "text-muted-foreground hover:bg-muted",
      )}
    >
      {children}
    </button>
  );
}
