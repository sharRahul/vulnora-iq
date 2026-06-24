import { useEffect, useMemo, useRef, useState } from "react";
import { MousePointerSquareDashed, ScanSearch } from "lucide-react";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ToastProvider, useToast } from "@/components/ui/toast";
import { AppShell } from "@/components/AppShell";
import type { ConsoleView } from "@/components/HeaderBar";
import { WorkspaceLayout } from "@/components/WorkspaceLayout";
import { EmptyState } from "@/components/EmptyState";
import { DashboardOverview } from "@/components/dashboard/DashboardOverview";
import { AssetNavigationPane } from "@/components/navigation/AssetNavigationPane";
import { AnalysisWorkspace } from "@/components/workspace/AnalysisWorkspace";
import { IntelligencePanel } from "@/components/intelligence/IntelligencePanel";
import { TargetsManager } from "@/components/targets/TargetsManager";
import { useTheme } from "@/hooks/useTheme";
import type {
  Asset,
  BackendFinding,
  DashboardMetrics,
  Finding,
  FindingHistoryEntry,
  FindingMutationState,
  FindingStatus,
  ScanEvent,
  ScanJob,
  Severity,
  SeverityDistributionPoint,
  VulnerabilityTrendPoint,
} from "@/types";

const SCAN_EVENT_TYPES = [
  "scan_queued",
  "scan_started",
  "target_validated",
  "phase_started",
  "check_started",
  "check_completed",
  "finding_created",
  "evidence_saved",
  "report_written",
  "scan_completed",
  "scan_failed",
  "heartbeat",
];

const SEVERITIES: Severity[] = ["critical", "high", "medium", "low", "info"];
const EMPTY_TREND: VulnerabilityTrendPoint[] = [];

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, { credentials: "same-origin", ...options });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}

async function csrfToken(): Promise<string> {
  const data = await api<{ csrf_token: string }>("/api/csrf-token");
  return data.csrf_token;
}

function normaliseSeverity(value: unknown): Severity {
  const severity = String(value || "info").toLowerCase();
  return ["critical", "high", "medium", "low", "info"].includes(severity) ? (severity as Severity) : "info";
}

function normaliseStatus(value: unknown): FindingStatus {
  const status = String(value || "open").toLowerCase();
  const allowed: FindingStatus[] = [
    "open",
    "pending_review",
    "auto_fix_available",
    "triaged",
    "in_progress",
    "accepted_risk",
    "false_positive",
    "fixed",
    "wont_fix",
  ];
  return allowed.includes(status as FindingStatus) ? (status as FindingStatus) : "open";
}

function isPendingReviewStatus(status: FindingStatus): boolean {
  return status === "pending_review" || status === "auto_fix_available" || status === "triaged" || status === "in_progress";
}

function riskScoreFromFinding(finding: BackendFinding, severity: Severity): number {
  if (typeof finding.score === "number") {
    const score = finding.score <= 1 ? finding.score * 100 : finding.score;
    return Math.max(0, Math.min(100, Math.round(score)));
  }
  return { critical: 95, high: 82, medium: 58, low: 32, info: 10 }[severity];
}

function liveAssetId(scanId: string): string {
  return `scan-${scanId}`;
}

function backendFindingId(finding: BackendFinding, index: number): string {
  return String(finding.id || finding.owasp_id || `finding-${index + 1}`);
}

function formatEvidence(evidence: unknown): string {
  if (!evidence || (typeof evidence === "object" && Object.keys(evidence as Record<string, unknown>).length === 0)) {
    return "No structured evidence was returned for this finding. Review the generated report artifacts for additional context.";
  }
  return JSON.stringify(evidence, null, 2);
}

function backendFindingToConsoleFinding(finding: BackendFinding, scanId: string, index: number): Finding {
  const id = backendFindingId(finding, index);
  const severity = normaliseSeverity(finding.severity);
  const state = finding.remediation_state;
  const affectedComponent = finding.affected_component || "assessment target";
  const recommendation = finding.recommendation || "Review the evidence, confirm applicability, and record the remediation decision.";
  const owaspLabel = finding.owasp_id || "AITG";
  const mitreAtlas = Array.isArray(finding.mitre_atlas) ? finding.mitre_atlas.join(", ") : "";

  return {
    id,
    assetId: liveAssetId(scanId),
    title: finding.title || `${id} finding`,
    severity,
    riskScore: riskScoreFromFinding(finding, severity),
    status: normaliseStatus(state?.status || finding.status || "open"),
    affectedPath: affectedComponent,
    aiSummary: finding.description || recommendation,
    vulnerableCode: {
      language: "json",
      filename: `${id}-evidence.json`,
      code: formatEvidence(finding.evidence),
    },
    remediation: {
      summary: recommendation,
      rationale: recommendation,
      confidence: state?.status === "fixed" ? 95 : 70,
      secureCode: {
        language: "text",
        filename: `${id}-remediation.txt`,
        code: recommendation,
      },
    },
    cve: { id: null, description: "Framework finding generated from the active VulnoraIQ scan." },
    cwe: {
      id: "N/A",
      name: "AI security assessment finding",
      description: "Review the mapped OWASP/MITRE context and generated evidence before closure.",
    },
    intelligence: {
      owaspLlm: owaspLabel,
      mitreAtlas,
      exploitability: "theoretical",
      affectedComponent,
      recommendedPriority: severity,
      policyStatus: state?.status === "fixed" ? "pass" : "manual_review",
      complianceTags: [],
    },
    report: [
      { title: "Evidence", body: formatEvidence(finding.evidence) },
      { title: "Recommendation", body: recommendation },
      {
        title: "Review status",
        body: state
          ? `Status: ${state.status}. Updated by ${state.updated_by || "unknown"} at ${state.updated_at || "unknown"}.`
          : "No remediation state has been recorded yet.",
      },
    ],
  };
}

function scanAsset(scan: ScanJob, findings: Finding[]): Asset {
  const highest = findings.reduce<Severity>((current, finding) => {
    const order: Record<Severity, number> = { critical: 4, high: 3, medium: 2, low: 1, info: 0 };
    return order[finding.severity] > order[current] ? finding.severity : current;
  }, "info");
  return {
    id: liveAssetId(scan.id),
    name: `${scan.target} · ${scan.profile}`,
    type: "ai_agent",
    locator: `scan:${scan.id}`,
    vulnerabilityCount: findings.length,
    highestSeverity: highest,
    riskScore: findings.reduce((max, finding) => Math.max(max, finding.riskScore), 0),
    lastScanned: scan.completed_at || scan.started_at || scan.created_at || new Date().toISOString(),
    findingIds: findings.map((finding) => finding.id),
  };
}

function scanTime(scan: ScanJob): number {
  return Date.parse(scan.completed_at || scan.started_at || scan.created_at || "") || 0;
}

function selectLatestScan(scans: ScanJob[]): ScanJob | null {
  return [...scans].sort((a, b) => scanTime(b) - scanTime(a))[0] || null;
}

function dashboardMetrics(findings: Finding[], activeScan: ScanJob | null): DashboardMetrics {
  const counts = Object.fromEntries(SEVERITIES.map((severity) => [severity, 0])) as Record<Severity, number>;
  findings.forEach((finding) => {
    counts[finding.severity] += 1;
  });
  const fixed = findings.filter((finding) => finding.status === "fixed").length;
  const pendingReviews = findings.filter((finding) => isPendingReviewStatus(finding.status)).length;

  return {
    totalScanned: activeScan ? 1 : 0,
    critical: counts.critical,
    high: counts.high,
    medium: counts.medium,
    low: counts.low,
    autoRemediationRate: findings.length ? Math.round((fixed / findings.length) * 100) : 0,
    pendingReviews,
    meanTimeToRemediateHours: 0,
    trend: {
      critical: 0,
      high: 0,
      autoRemediationRate: 0,
      pendingReviews: 0,
    },
  };
}

function severityDistribution(findings: Finding[]): SeverityDistributionPoint[] {
  const counts = Object.fromEntries(SEVERITIES.map((severity) => [severity, 0])) as Record<Severity, number>;
  findings.forEach((finding) => {
    counts[finding.severity] += 1;
  });
  return SEVERITIES.map((severity) => ({ severity, count: counts[severity] })).filter((point) => point.count > 0);
}

function ConsoleInner() {
  const { theme, toggleTheme } = useTheme();
  const { notify } = useToast();
  const scanSourceRef = useRef<EventSource | null>(null);

  const [view, setView] = useState<ConsoleView>("overview");
  const [selectedFindingId, setSelectedFindingId] = useState<string | null>(null);
  const [scanning, setScanning] = useState(false);
  const [dashboardLoading, setDashboardLoading] = useState(false);
  const [activeScan, setActiveScan] = useState<ScanJob | null>(null);
  const [runtimeFindings, setRuntimeFindings] = useState<Finding[]>([]);
  const [findingHistories, setFindingHistories] = useState<Record<string, FindingHistoryEntry[]>>({});
  const [liveScanEvents, setLiveScanEvents] = useState<ScanEvent[]>([]);
  const [scanProgressPercent, setScanProgressPercent] = useState(0);
  const [scanPhase, setScanPhase] = useState("Idle");
  const [liveFindingCount, setLiveFindingCount] = useState(0);

  const displayFindings = runtimeFindings;
  const displayAssets = activeScan ? [scanAsset(activeScan, runtimeFindings)] : [];
  const metrics = useMemo(() => dashboardMetrics(runtimeFindings, activeScan), [activeScan, runtimeFindings]);
  const distribution = useMemo(() => severityDistribution(runtimeFindings), [runtimeFindings]);

  const findingsById = useMemo<Record<string, Finding>>(
    () => Object.fromEntries(displayFindings.map((f) => [f.id, f])),
    [displayFindings],
  );

  const selectedFinding = selectedFindingId ? findingsById[selectedFindingId] : null;
  const selectedAsset = selectedFinding
    ? displayAssets.find((a) => a.id === selectedFinding.assetId)
    : undefined;
  const selectedFindingHistory = selectedFindingId ? findingHistories[selectedFindingId] || [] : [];

  useEffect(() => {
    void loadExistingScanState();
    return () => {
      scanSourceRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelectFinding = (id: string) => {
    setSelectedFindingId(id);
    setView("workspace");
  };

  async function refreshFindingHistory(scanId: string, findingId: string): Promise<void> {
    const data = await api<{ history: FindingHistoryEntry[] }>(
      `/api/scans/${encodeURIComponent(scanId)}/findings/${encodeURIComponent(findingId)}/history`,
    );
    setFindingHistories((prev) => ({ ...prev, [findingId]: data.history || [] }));
  }

  async function refreshScanFindings(scanId: string, scan?: ScanJob | null, preferredFindingId?: string): Promise<void> {
    const findingsPayload = await api<{ findings: BackendFinding[] }>(`/api/scans/${encodeURIComponent(scanId)}/findings`);
    const scanRecord = scan || activeScan || (await api<ScanJob>(`/api/scans/${encodeURIComponent(scanId)}`));
    const nextFindings = (findingsPayload.findings || []).map((finding, index) =>
      backendFindingToConsoleFinding(finding, scanId, index),
    );
    setActiveScan(scanRecord);
    setRuntimeFindings(nextFindings);
    if (nextFindings.length) {
      const nextSelected = nextFindings.find((finding) => finding.id === preferredFindingId) || nextFindings[0];
      setSelectedFindingId(nextSelected.id);
      setView("workspace");
      await refreshFindingHistory(scanId, nextSelected.id);
    } else {
      setSelectedFindingId(null);
    }
  }

  async function loadExistingScanState(): Promise<void> {
    setDashboardLoading(true);
    try {
      const data = await api<{ jobs: ScanJob[] }>("/api/scans");
      const scan = selectLatestScan(data.jobs || []);
      if (scan) {
        await refreshScanFindings(scan.id, scan);
      } else {
        setActiveScan(null);
        setRuntimeFindings([]);
        setSelectedFindingId(null);
      }
    } catch (exc) {
      setActiveScan(null);
      setRuntimeFindings([]);
      setSelectedFindingId(null);
      notify(exc instanceof Error ? `Unable to load saved scans: ${exc.message}` : "Unable to load saved scans", "error");
    } finally {
      setDashboardLoading(false);
    }
  }

  function connectScanEvents(scan: ScanJob) {
    scanSourceRef.current?.close();
    setLiveScanEvents([]);
    setLiveFindingCount(0);
    setScanProgressPercent(0);
    setScanPhase("Queued");
    const source = new EventSource(`/api/scans/${encodeURIComponent(scan.id)}/events`, { withCredentials: true });
    scanSourceRef.current = source;

    const onEvent = (event: MessageEvent) => {
      const payload = JSON.parse(event.data) as ScanEvent;
      setLiveScanEvents((prev) => {
        const next = [...prev.slice(-49), payload];
        setLiveFindingCount(next.filter((item) => item.type === "finding_created").length);
        return next;
      });
      setScanPhase(payload.phase || payload.type);
      setScanProgressPercent(payload.progress?.percent || 0);

      if (payload.type === "scan_completed" || payload.type === "scan_failed") {
        setScanning(false);
        setDashboardLoading(false);
        source.close();
        scanSourceRef.current = null;
        if (payload.type === "scan_completed") {
          notify("Scan complete — findings refreshed from backend");
          void refreshScanFindings(scan.id, { ...scan, status: "completed" });
        } else {
          notify("Scan failed — check backend logs and scan artifacts", "error");
        }
      }
    };

    SCAN_EVENT_TYPES.forEach((type) => source.addEventListener(type, onEvent));
    source.onerror = () => {
      if (scanSourceRef.current === source) {
        setScanPhase("SSE connection interrupted");
      }
    };
  }

  async function handleToggleScan() {
    if (scanning) return;
    setScanning(true);
    setDashboardLoading(true);
    setScanPhase("Creating scan");
    setScanProgressPercent(0);
    setLiveFindingCount(0);
    setRuntimeFindings([]);
    setFindingHistories({});
    setSelectedFindingId(null);
    try {
      const token = await csrfToken();
      const job = await api<ScanJob>("/api/scans", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
        body: JSON.stringify({ target: "demo", profile: "baseline", authorised: false }),
      });
      setActiveScan(job);
      notify(`Scan ${job.id} queued — streaming live backend progress`, "info");
      connectScanEvents(job);
    } catch (exc) {
      setScanning(false);
      setDashboardLoading(false);
      setScanPhase("Scan start failed");
      notify(exc instanceof Error ? exc.message : String(exc), "error");
    }
  }

  async function persistFindingState(finding: Finding, patch: Partial<FindingMutationState> & { note?: string }) {
    if (!activeScan) {
      notify("Run a backend scan first, then update findings from the refreshed scan results.", "info");
      return;
    }
    try {
      const token = await csrfToken();
      await api<{ finding_state: FindingMutationState }>(
        `/api/scans/${encodeURIComponent(activeScan.id)}/findings/${encodeURIComponent(finding.id)}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
          body: JSON.stringify(patch),
        },
      );
      await refreshScanFindings(activeScan.id, activeScan, finding.id);
      await refreshFindingHistory(activeScan.id, finding.id);
      notify(`Finding ${finding.id} updated and persisted`);
    } catch (exc) {
      notify(exc instanceof Error ? exc.message : String(exc), "error");
    }
  }

  const handleApplyFix = (finding: Finding) =>
    persistFindingState(finding, {
      status: "fixed",
      remediation_note: "Fix applied from the WebUI remediation panel.",
      note: "Fix applied from WebUI.",
    });

  const handleMarkForReview = (finding: Finding) =>
    persistFindingState(finding, {
      status: "triaged",
      remediation_note: "Marked for reviewer validation from the WebUI remediation panel.",
      note: "Marked for review from WebUI.",
    });

  const navPane = (
    <AssetNavigationPane
      assets={displayAssets}
      findingsById={findingsById}
      selectedFindingId={selectedFindingId}
      onSelectFinding={handleSelectFinding}
    />
  );

  const middlePane = selectedFinding ? (
    <AnalysisWorkspace
      finding={selectedFinding}
      asset={selectedAsset}
      applied={selectedFinding.status === "fixed"}
      history={selectedFindingHistory}
      onApplyFix={() => handleApplyFix(selectedFinding)}
      onMarkForReview={() => handleMarkForReview(selectedFinding)}
    />
  ) : (
    <EmptyState
      icon={MousePointerSquareDashed}
      title="No scan finding selected"
      description="Run a scan or open a saved scan result. Clean workspaces show no sample findings or dummy assets."
    />
  );

  const intelPane = selectedFinding ? (
    <IntelligencePanel finding={selectedFinding} />
  ) : (
    <EmptyState
      icon={ScanSearch}
      title="No finding selected"
      description="Vulnerability intelligence and the Ask VulnorAIQ assistant appear here after a real backend finding is selected."
    />
  );

  return (
    <AppShell
      view={view}
      onChangeView={setView}
      theme={theme}
      onToggleTheme={toggleTheme}
      scanning={scanning}
      scanStatusLabel={scanPhase}
      scanProgressPercent={scanProgressPercent}
      scanFindingCount={liveFindingCount}
      onToggleScan={handleToggleScan}
    >
      {view === "targets" ? (
        <TargetsManager />
      ) : view === "overview" ? (
        <div className="h-full overflow-y-auto scrollbar-thin p-4 sm:p-6">
          <div className="mx-auto max-w-[1400px]">
            <DashboardOverview
              metrics={metrics}
              trend={EMPTY_TREND}
              distribution={distribution}
              loading={dashboardLoading}
            />
            {!dashboardLoading && !activeScan ? (
              <section className="mt-4 rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground shadow-card">
                <p className="text-xs font-bold uppercase tracking-wide">Clean workspace</p>
                <h2 className="mt-1 text-lg font-extrabold text-foreground">No scans yet</h2>
                <p className="mt-2 max-w-3xl">
                  VulnoraIQ does not show sample assets, mock findings, or dummy dashboard data. Run a scan from the header or configure an authorised target to populate this dashboard with your own evidence.
                </p>
              </section>
            ) : null}
            {activeScan && !runtimeFindings.length && !dashboardLoading ? (
              <section className="mt-4 rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground shadow-card">
                <p className="text-xs font-bold uppercase tracking-wide">Latest scan</p>
                <h2 className="mt-1 text-lg font-extrabold text-foreground">No findings returned</h2>
                <p className="mt-2 max-w-3xl">
                  The latest saved scan is loaded, but it did not return findings. Reports and artifacts remain available through the backend output directory.
                </p>
              </section>
            ) : null}
            {liveScanEvents.length ? (
              <section className="mt-4 rounded-xl border border-border bg-card p-4 shadow-card" aria-live="polite">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wide text-muted-foreground">Live backend scan</p>
                    <h2 className="mt-1 text-lg font-extrabold">{scanPhase}</h2>
                  </div>
                  <p className="text-sm font-semibold text-muted-foreground">
                    {Math.round(scanProgressPercent)}% · {liveFindingCount} findings
                  </p>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded bg-muted">
                  <div className="h-full bg-[var(--accent-sage)]" style={{ width: `${scanProgressPercent}%` }} />
                </div>
                <ol className="mt-3 max-h-48 space-y-1 overflow-auto text-xs text-muted-foreground">
                  {liveScanEvents.slice(-10).map((event, index) => (
                    <li key={`${event.event_id}-${index}`}>{event.type}: {event.message}</li>
                  ))}
                </ol>
              </section>
            ) : null}
          </div>
        </div>
      ) : (
        <WorkspaceLayout left={navPane} middle={middlePane} right={intelPane} />
      )}
    </AppShell>
  );
}

export default function App() {
  return (
    <TooltipProvider delayDuration={200}>
      <ToastProvider>
        <ConsoleInner />
      </ToastProvider>
    </TooltipProvider>
  );
}
