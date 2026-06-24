import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Filter,
  Loader2,
  PlayCircle,
  Plus,
  RefreshCw,
  Save,
  Search,
  Server,
  ShieldCheck,
  Trash2,
  Wifi,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import type { ConnectivityResult, ScanJob, TargetConfig, TargetRecord } from "@/types";
import { cn } from "@/lib/utils";

const TARGET_TYPES = ["http_json", "chat_completions", "ollama_generate", "webhook_json", "rag_query", "agent_tool_loop"];
const ENVIRONMENTS = ["local", "lab", "internal", "production-like"];
const SCAN_PROFILES = ["baseline", "agent_readiness", "rag_readiness", "owasp_llm_2025"];

const defaultTarget = (): TargetConfig => ({
  name: "New authorised AI target",
  type: "http_json",
  base_url: "http://127.0.0.1:9090",
  endpoint_path: "/agent",
  method: "POST",
  headers: { "Content-Type": "application/json" },
  request_body_template: { prompt: "{{prompt}}" },
  response_extraction_path: "response",
  timeout: 10,
  retry: { attempts: 2, backoff_seconds: 0.2 },
  rate_limit: { requests_per_second: 1 },
  authorisation_required: true,
  safety_profile: "local_lab_safe",
  tags: ["local", "authorised"],
  owner: { name: "", contact: "" },
  environment: "local",
  allow_external: false,
});

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, { credentials: "same-origin", ...options });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}

async function csrfToken(): Promise<string> {
  const data = await api<{ csrf_token: string }>("/api/csrf-token");
  return data.csrf_token;
}

function parseJsonField(value: string, fallback: unknown): unknown {
  if (!value.trim()) return fallback;
  return JSON.parse(value);
}

function targetHealth(target: TargetRecord): "ready" | "needs-owner" | "needs-auth" | "external" {
  if (target.config.allow_external) return "external";
  if (!target.config.owner?.contact) return "needs-owner";
  if (target.config.authorisation_required === false) return "needs-auth";
  return "ready";
}

function endpointLabel(target: TargetConfig): string {
  return target.base_url || target.endpoint || "No endpoint configured";
}

export function TargetsManager() {
  const [targets, setTargets] = useState<TargetRecord[]>([]);
  const [selectedId, setSelectedId] = useState("local_mock_agent");
  const [draftId, setDraftId] = useState("local_mock_agent");
  const [draft, setDraft] = useState<TargetConfig>(defaultTarget());
  const [headersText, setHeadersText] = useState("{}");
  const [bodyText, setBodyText] = useState(JSON.stringify(defaultTarget().request_body_template, null, 2));
  const [connectivity, setConnectivity] = useState<ConnectivityResult | null>(null);
  const [jobs, setJobs] = useState<ScanJob[]>([]);
  const [scanProfile, setScanProfile] = useState("baseline");
  const [query, setQuery] = useState("");
  const [environmentFilter, setEnvironmentFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selected = useMemo(() => targets.find((target) => target.id === selectedId), [selectedId, targets]);
  const filteredTargets = useMemo(() => {
    const q = query.trim().toLowerCase();
    return targets.filter((target) => {
      const envMatch = environmentFilter === "all" || (target.config.environment || "local") === environmentFilter;
      const searchText = [target.id, target.config.name, target.config.type, target.config.base_url, target.config.endpoint, target.config.owner?.contact, ...(target.config.tags || [])]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return envMatch && (!q || searchText.includes(q));
    });
  }, [environmentFilter, query, targets]);
  const latestJobs = useMemo(() => jobs.filter((job) => job.target === draftId).slice(0, 5), [draftId, jobs]);
  const readyCount = useMemo(() => targets.filter((target) => targetHealth(target) === "ready").length, [targets]);

  async function loadTargets() {
    setLoading(true);
    setError(null);
    try {
      const data = await api<{ targets: Record<string, TargetConfig> }>("/api/targets");
      const records = Object.entries(data.targets || {}).map(([id, config]) => ({ id, config }));
      setTargets(records);
      const next = records.find((record) => record.id === selectedId) || records[0];
      if (next) selectTarget(next);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setLoading(false);
    }
  }

  async function loadJobs() {
    try {
      const data = await api<{ jobs: ScanJob[] }>("/api/scans");
      setJobs(data.jobs || []);
    } catch {
      // Older or unauthenticated deployments can still manage targets without scan history.
    }
  }

  function selectTarget(record: TargetRecord) {
    setSelectedId(record.id);
    setDraftId(record.id);
    setDraft({ ...defaultTarget(), ...record.config });
    setHeadersText(JSON.stringify(record.config.headers || {}, null, 2));
    setBodyText(JSON.stringify(record.config.request_body_template || defaultTarget().request_body_template, null, 2));
    setConnectivity(null);
  }

  function newTarget() {
    const next = defaultTarget();
    setSelectedId("");
    setDraftId("new_authorised_target");
    setDraft(next);
    setHeadersText(JSON.stringify(next.headers, null, 2));
    setBodyText(JSON.stringify(next.request_body_template, null, 2));
    setConnectivity(null);
  }

  function buildTarget(): TargetConfig {
    return {
      ...draft,
      headers: parseJsonField(headersText, {}) as Record<string, string>,
      request_body_template: parseJsonField(bodyText, { prompt: "{{prompt}}" }),
      tags: typeof draft.tags === "string" ? String(draft.tags).split(",").map((tag) => tag.trim()).filter(Boolean) : draft.tags,
    };
  }

  async function saveTarget() {
    setSaving(true);
    setError(null);
    try {
      const token = await csrfToken();
      const target = buildTarget();
      await api("/api/targets/save", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
        body: JSON.stringify({ id: draftId, target }),
      });
      await loadTargets();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setSaving(false);
    }
  }

  async function deleteTarget() {
    if (!window.confirm(`Delete runtime target '${draftId}'? Built-in targets are not removed.`)) return;
    setSaving(true);
    setError(null);
    try {
      const token = await csrfToken();
      await api("/api/targets/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
        body: JSON.stringify({ id: draftId }),
      });
      await loadTargets();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setSaving(false);
    }
  }

  async function testConnectivity() {
    setTesting(true);
    setError(null);
    setConnectivity(null);
    try {
      if (!targets.some((target) => target.id === draftId)) await saveTarget();
      const token = await csrfToken();
      const data = await api<ConnectivityResult>(`/api/targets/${encodeURIComponent(draftId)}/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
        body: JSON.stringify({}),
      });
      setConnectivity(data);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setTesting(false);
    }
  }

  async function startScan() {
    setScanning(true);
    setError(null);
    try {
      const token = await csrfToken();
      await api<ScanJob>("/api/scans", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
        body: JSON.stringify({ target: draftId, profile: scanProfile, authorised: draftId !== "demo" }),
      });
      await loadJobs();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setScanning(false);
    }
  }

  useEffect(() => {
    void loadTargets();
    void loadJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isExternal = draft.allow_external === true;
  const isDemo = draftId === "demo" || draft.type === "echo";
  const safetyChecklist = [
    { label: "Authorisation gate", ok: isDemo || draft.authorisation_required !== false },
    { label: "Owner contact", ok: Boolean(draft.owner?.contact) || isDemo },
    { label: "Bounded rate limit", ok: Number(draft.rate_limit?.requests_per_second || 0) > 0 },
    { label: "Safety profile", ok: Boolean(draft.safety_profile) },
  ];

  return (
    <div className="grid h-full grid-cols-[380px_minmax(0,1fr)] overflow-hidden bg-canvas">
      <aside className="overflow-y-auto border-r border-border bg-card p-4 scrollbar-thin">
        <div className="mb-4 flex items-center justify-between gap-2">
          <div>
            <h2 className="text-lg font-extrabold">Targets</h2>
            <p className="text-xs text-muted-foreground">Manage authorised AI systems and scan readiness.</p>
          </div>
          <Button size="sm" variant="primary" onClick={newTarget}><Plus className="size-4" /> Add</Button>
        </div>
        <div className="mb-4 grid grid-cols-3 gap-2 text-center text-xs">
          <Metric label="Total" value={targets.length} />
          <Metric label="Ready" value={readyCount} />
          <Metric label="Jobs" value={jobs.length} />
        </div>
        <div className="mb-3 space-y-2">
          <div className="relative"><Search className="pointer-events-none absolute left-2 top-2.5 size-4 text-muted-foreground" /><input value={query} onChange={(e) => setQuery(e.target.value)} className="input pl-8 text-sm" placeholder="Search targets, owners, tags…" /></div>
          <div className="relative"><Filter className="pointer-events-none absolute left-2 top-2.5 size-4 text-muted-foreground" /><select value={environmentFilter} onChange={(e) => setEnvironmentFilter(e.target.value)} className="input pl-8 text-sm"><option value="all">All environments</option>{ENVIRONMENTS.map((env) => <option key={env}>{env}</option>)}</select></div>
        </div>
        {loading ? <p className="text-sm text-muted-foreground">Loading targets…</p> : null}
        <div className="space-y-2">
          {filteredTargets.map((target) => <TargetListItem key={target.id} target={target} active={selectedId === target.id} onClick={() => selectTarget(target)} />)}
          {!loading && filteredTargets.length === 0 ? <p className="rounded-lg border border-border bg-canvas p-3 text-sm text-muted-foreground">No targets match the current filters.</p> : null}
        </div>
      </aside>

      <section className="overflow-y-auto p-5 scrollbar-thin">
        <div className="mx-auto max-w-6xl space-y-4">
          <div className="rounded-xl border border-border bg-card p-4 shadow-card">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-wide text-muted-foreground">Target management workspace</p>
                <h1 className="mt-1 flex items-center gap-2 text-2xl font-extrabold"><Server className="size-6" /> {draft.name || draftId}</h1>
                <p className="mt-1 max-w-3xl text-sm text-muted-foreground">Create, edit, validate, and launch authorised scans for local/internal AI targets from one operational cockpit.</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button variant="secondary" onClick={() => void loadJobs()}><RefreshCw /> Refresh jobs</Button>
                <Button variant="secondary" onClick={testConnectivity} disabled={testing || isDemo}>{testing ? <Loader2 className="animate-spin" /> : <Wifi />} Test connectivity</Button>
                <Button variant="primary" onClick={saveTarget} disabled={saving || isDemo}>{saving ? <Loader2 className="animate-spin" /> : <Save />} Save</Button>
                <Button variant="danger" onClick={deleteTarget} disabled={saving || isDemo}><Trash2 /> Delete</Button>
              </div>
            </div>
            {selected ? null : <p className="mt-2 text-xs text-muted-foreground">Creating a new runtime target.</p>}
            {isDemo ? <Warning title="Demo target" body="The in-memory demo target is read-only. Add a new authorised target to edit real configurations." /> : null}
            {isExternal ? <Warning title="External host override enabled" body="Only enable allow_external for systems you own or are explicitly authorised to assess. The backend still requires the normal non-demo authorisation confirmation before scans." /> : null}
            {error ? <Warning title="Target error" body={error} danger /> : null}
          </div>

          <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
            <div className="space-y-4">
              <div className="grid gap-4 lg:grid-cols-2">
                <Field label="Target ID"><input value={draftId} onChange={(e) => setDraftId(e.target.value)} className="input" disabled={isDemo} /></Field>
                <Field label="Display name"><input value={draft.name || ""} onChange={(e) => setDraft({ ...draft, name: e.target.value })} className="input" /></Field>
                <Field label="Type"><select value={draft.type} onChange={(e) => setDraft({ ...draft, type: e.target.value })} className="input">{TARGET_TYPES.map((type) => <option key={type}>{type}</option>)}</select></Field>
                <Field label="Environment"><select value={draft.environment || "local"} onChange={(e) => setDraft({ ...draft, environment: e.target.value })} className="input">{ENVIRONMENTS.map((env) => <option key={env}>{env}</option>)}</select></Field>
                <Field label="Base URL"><input value={draft.base_url || ""} onChange={(e) => setDraft({ ...draft, base_url: e.target.value })} className="input font-mono" placeholder="http://127.0.0.1:9090" /></Field>
                <Field label="Endpoint path"><input value={draft.endpoint_path || ""} onChange={(e) => setDraft({ ...draft, endpoint_path: e.target.value })} className="input font-mono" placeholder="/agent" /></Field>
                <Field label="HTTP method"><select value={draft.method || "POST"} onChange={(e) => setDraft({ ...draft, method: e.target.value })} className="input"><option>POST</option><option>GET</option></select></Field>
                <Field label="Response extraction path"><input value={draft.response_extraction_path || ""} onChange={(e) => setDraft({ ...draft, response_extraction_path: e.target.value })} className="input font-mono" placeholder="choices.0.message.content" /></Field>
                <Field label="Auth token env var"><input value={draft.auth_token_env || draft.token_env_var || ""} onChange={(e) => setDraft({ ...draft, auth_token_env: e.target.value, token_env_var: undefined })} className="input font-mono" placeholder="LLM_VAPT_TARGET_TOKEN" /></Field>
                <Field label="Safety profile"><input value={draft.safety_profile || ""} onChange={(e) => setDraft({ ...draft, safety_profile: e.target.value })} className="input" /></Field>
                <Field label="Timeout seconds"><input type="number" value={draft.timeout || 30} onChange={(e) => setDraft({ ...draft, timeout: Number(e.target.value) })} className="input" /></Field>
                <Field label="Rate limit / second"><input type="number" step="0.1" value={draft.rate_limit?.requests_per_second || 1} onChange={(e) => setDraft({ ...draft, rate_limit: { requests_per_second: Number(e.target.value) } })} className="input" /></Field>
              </div>
              <div className="grid gap-4 lg:grid-cols-2">
                <Field label="Headers JSON"><textarea value={headersText} onChange={(e) => setHeadersText(e.target.value)} className="input min-h-32 font-mono text-xs" /></Field>
                <Field label="Request body template JSON"><textarea value={bodyText} onChange={(e) => setBodyText(e.target.value)} className="input min-h-32 font-mono text-xs" /></Field>
              </div>
              <div className="grid gap-4 lg:grid-cols-3">
                <Toggle checked={draft.authorisation_required !== false} onChange={(checked) => setDraft({ ...draft, authorisation_required: checked })} title="Authorisation required" body="Required for all non-demo real targets." />
                <Toggle checked={draft.allow_external === true} onChange={(checked) => setDraft({ ...draft, allow_external: checked })} title="Allow external host" body="Overrides the loopback/internal host guard for authorised scopes." icon={<ExternalLink className="size-4" />} />
                <Field label="Owner/contact"><input value={draft.owner?.contact || ""} onChange={(e) => setDraft({ ...draft, owner: { ...(draft.owner || {}), contact: e.target.value } })} className="input" placeholder="team@example.com" /></Field>
              </div>
            </div>

            <aside className="space-y-4">
              <Panel title="Readiness guardrails" icon={<ShieldCheck className="size-4" />}>
                <div className="space-y-2">{safetyChecklist.map((item) => <ChecklistItem key={item.label} {...item} />)}</div>
              </Panel>
              <Panel title="Launch scan" icon={<PlayCircle className="size-4" />}>
                <select value={scanProfile} onChange={(e) => setScanProfile(e.target.value)} className="input text-sm">{SCAN_PROFILES.map((profile) => <option key={profile}>{profile}</option>)}</select>
                <Button className="mt-3 w-full" variant="success" onClick={startScan} disabled={scanning || (!isDemo && draft.authorisation_required === false)}>{scanning ? <Loader2 className="animate-spin" /> : <PlayCircle />} Start authorised scan</Button>
                <p className="mt-2 text-xs text-muted-foreground">Non-demo scans are sent with an explicit authorised flag and still pass backend permission checks.</p>
              </Panel>
              <Panel title="Recent jobs" icon={<RefreshCw className="size-4" />}>
                <div className="space-y-2">{latestJobs.length ? latestJobs.map((job) => <JobRow key={job.id} job={job} />) : <p className="text-sm text-muted-foreground">No scan jobs for this target yet.</p>}</div>
              </Panel>
              {connectivity ? <Panel title="Connectivity result" icon={connectivity.ready ? <CheckCircle2 className="size-4 text-[var(--sev-low)]" /> : <AlertTriangle className="size-4 text-[var(--sev-high)]" />}><pre className="code-wrap max-h-80 overflow-auto rounded-lg bg-muted p-3 text-xs">{JSON.stringify(connectivity, null, 2)}</pre></Panel> : null}
            </aside>
          </div>
        </div>
      </section>
    </div>
  );
}

function TargetListItem({ target, active, onClick }: { target: TargetRecord; active: boolean; onClick: () => void }) {
  const health = targetHealth(target);
  return <button onClick={onClick} className={cn("w-full rounded-lg border p-3 text-left transition-colors", active ? "border-primary bg-muted" : "border-border bg-canvas hover:bg-muted")}><div className="flex items-center justify-between gap-2"><span className="font-semibold">{target.config.name || target.id}</span><StatusPill status={health} /></div><p className="mt-1 truncate text-xs text-muted-foreground">{target.id} · {target.config.type} · {target.config.environment || "local"}</p><p className="mt-1 truncate font-mono text-[11px] text-muted-foreground">{endpointLabel(target.config)}</p></button>;
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block rounded-xl border border-border bg-card p-3 text-sm font-semibold shadow-card"><span className="mb-1 block text-xs uppercase tracking-wide text-muted-foreground">{label}</span>{children}</label>;
}

function Toggle({ checked, onChange, title, body, icon }: { checked: boolean; onChange: (checked: boolean) => void; title: string; body: string; icon?: React.ReactNode }) {
  return <button type="button" onClick={() => onChange(!checked)} className={cn("rounded-xl border p-3 text-left shadow-card", checked ? "border-primary bg-muted" : "border-border bg-card")}><span className="flex items-center gap-2 font-bold">{icon}{title}</span><span className="mt-1 block text-xs text-muted-foreground">{body}</span><span className="mt-3 inline-flex rounded px-2 py-1 text-xs font-bold" style={{ background: checked ? "var(--accent-sage)" : "var(--muted)" }}>{checked ? "Enabled" : "Disabled"}</span></button>;
}

function Warning({ title, body, danger = false }: { title: string; body: string; danger?: boolean }) {
  return <div className={cn("mt-4 rounded-lg border p-3 text-sm", danger ? "border-[var(--sev-high)] bg-[var(--sev-high)]/10" : "border-[var(--sev-medium)] bg-[var(--sev-medium)]/10")}><p className="flex items-center gap-2 font-bold"><AlertTriangle className="size-4" /> {title}</p><p className="mt-1 text-muted-foreground">{body}</p></div>;
}

function Metric({ label, value }: { label: string; value: number }) {
  return <div className="rounded-lg border border-border bg-canvas p-2"><p className="text-lg font-extrabold">{value}</p><p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p></div>;
}

function Panel({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return <div className="rounded-xl border border-border bg-card p-4 shadow-card"><h3 className="mb-3 flex items-center gap-2 font-bold">{icon}{title}</h3>{children}</div>;
}

function ChecklistItem({ label, ok }: { label: string; ok: boolean }) {
  return <div className="flex items-center justify-between rounded-lg border border-border bg-canvas px-3 py-2 text-sm"><span>{label}</span>{ok ? <CheckCircle2 className="size-4 text-[var(--sev-low)]" /> : <AlertTriangle className="size-4 text-[var(--sev-medium)]" />}</div>;
}

function StatusPill({ status }: { status: ReturnType<typeof targetHealth> }) {
  const labels = { ready: "ready", "needs-owner": "owner", "needs-auth": "auth", external: "external" };
  return <span className={cn("rounded px-2 py-0.5 text-[10px] font-bold uppercase", status === "ready" ? "bg-[var(--accent-sage)] text-[#1b2110]" : "bg-muted text-muted-foreground")}>{labels[status]}</span>;
}

function JobRow({ job }: { job: ScanJob }) {
  return <div className="rounded-lg border border-border bg-canvas p-3 text-sm"><div className="flex items-center justify-between gap-2"><span className="font-mono text-xs">{job.id}</span><span className="rounded bg-muted px-2 py-0.5 text-[10px] font-bold uppercase text-muted-foreground">{job.status}</span></div><p className="mt-1 text-xs text-muted-foreground">{job.profile}{job.error ? ` · ${job.error}` : ""}</p></div>;
}
