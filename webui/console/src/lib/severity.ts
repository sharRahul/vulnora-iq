import type { FindingStatus, Severity } from "@/types";

interface SeverityStyle {
  label: string;
  /** Tailwind text colour token. */
  text: string;
  /** Tailwind border colour token. */
  border: string;
  /** Solid background for badges. */
  solid: string;
  /** Tinted background for soft chips. */
  soft: string;
  cssVar: string;
}

export const SEVERITY_ORDER: Record<Severity, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
  info: 0,
};

export const severityStyles: Record<Severity, SeverityStyle> = {
  critical: {
    label: "Critical",
    text: "text-severity-critical",
    border: "border-severity-critical",
    solid: "bg-severity-critical text-white",
    soft: "bg-[color-mix(in_srgb,var(--sev-critical)_14%,transparent)] text-severity-critical",
    cssVar: "var(--sev-critical)",
  },
  high: {
    label: "High",
    text: "text-severity-high",
    border: "border-severity-high",
    solid: "bg-severity-high text-white",
    soft: "bg-[color-mix(in_srgb,var(--sev-high)_14%,transparent)] text-severity-high",
    cssVar: "var(--sev-high)",
  },
  medium: {
    label: "Medium",
    text: "text-severity-medium",
    border: "border-severity-medium",
    solid: "bg-severity-medium text-[#231a06]",
    soft: "bg-[color-mix(in_srgb,var(--sev-medium)_16%,transparent)] text-severity-medium",
    cssVar: "var(--sev-medium)",
  },
  low: {
    label: "Low",
    text: "text-severity-low",
    border: "border-severity-low",
    solid: "bg-severity-low text-white",
    soft: "bg-[color-mix(in_srgb,var(--sev-low)_14%,transparent)] text-severity-low",
    cssVar: "var(--sev-low)",
  },
  info: {
    label: "Info",
    text: "text-severity-info",
    border: "border-severity-info",
    solid: "bg-severity-info text-white",
    soft: "bg-[color-mix(in_srgb,var(--sev-info)_16%,transparent)] text-severity-info",
    cssVar: "var(--sev-info)",
  },
};

export function riskTier(score: number): Severity {
  if (score >= 90) return "critical";
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  if (score >= 15) return "low";
  return "info";
}

export const statusStyles: Record<
  FindingStatus,
  { label: string; className: string }
> = {
  open: {
    label: "Open",
    className:
      "bg-[color-mix(in_srgb,var(--sev-high)_12%,transparent)] text-severity-high border-severity-high",
  },
  pending_review: {
    label: "Pending Review",
    className:
      "bg-[color-mix(in_srgb,var(--sev-medium)_14%,transparent)] text-severity-medium border-severity-medium",
  },
  auto_fix_available: {
    label: "Auto-Fix Available",
    className:
      "bg-[color-mix(in_srgb,var(--accent-slate)_16%,transparent)] text-slate border-slate",
  },
  triaged: {
    label: "Triaged",
    className:
      "bg-[color-mix(in_srgb,var(--sev-medium)_14%,transparent)] text-severity-medium border-severity-medium",
  },
  in_progress: {
    label: "In Progress",
    className:
      "bg-[color-mix(in_srgb,var(--accent-slate)_16%,transparent)] text-slate border-slate",
  },
  accepted_risk: {
    label: "Accepted Risk",
    className:
      "bg-[color-mix(in_srgb,var(--sev-low)_14%,transparent)] text-severity-low border-severity-low",
  },
  false_positive: {
    label: "False Positive",
    className:
      "bg-[color-mix(in_srgb,var(--sev-info)_16%,transparent)] text-severity-info border-severity-info",
  },
  fixed: {
    label: "Fixed",
    className:
      "bg-[color-mix(in_srgb,var(--sev-low)_14%,transparent)] text-severity-low border-severity-low",
  },
  wont_fix: {
    label: "Won't Fix",
    className:
      "bg-[color-mix(in_srgb,var(--muted)_22%,transparent)] text-muted-foreground border-border",
  },
};
