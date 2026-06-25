import { useEffect, useState } from "react";
import {
  AlertTriangle,
  Box,
  CheckCircle2,
  Cpu,
  Eye,
  Loader2,
  Play,
  Plus,
  RefreshCw,
  Server,
  Square,
  Terminal,
  Trash2,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface AgentRecord {
  container_id: string;
  id: string;
  image: string;
  status: string;
  ports: string;
}

interface AgentTemplate {
  display_name: string;
  description: string;
}

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, { credentials: "same-origin", ...options });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<T>;
}

async function csrfToken(): Promise<string> {
  const data = await api<{ csrf_token: string }>("/api/csrf-token");
  return data.csrf_token;
}

function statusColor(status: string): string {
  const s = status.toLowerCase();
  if (s.includes("up") || s.includes("healthy")) return "text-[var(--sev-low)]";
  if (s.includes("exited") || s.includes("dead")) return "text-[var(--sev-high)]";
  return "text-[var(--sev-medium)]";
}

function statusIcon(status: string) {
  const s = status.toLowerCase();
  if (s.includes("up") || s.includes("healthy")) return <CheckCircle2 className="size-4 text-[var(--sev-low)]" />;
  if (s.includes("exited") || s.includes("dead")) return <XCircle className="size-4 text-[var(--sev-high)]" />;
  return <Loader2 className="size-4 animate-spin text-[var(--sev-medium)]" />;
}

export function AgentHost() {
  const [agents, setAgents] = useState<AgentRecord[]>([]);
  const [templates, setTemplates] = useState<Record<string, AgentTemplate>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deploying, setDeploying] = useState(false);
  const [logsFor, setLogsFor] = useState<string | null>(null);
  const [logs, setLogs] = useState("");
  const [customImage, setCustomImage] = useState("");
  const [customEnv, setCustomEnv] = useState("");

  async function loadAgents() {
    setLoading(true);
    setError(null);
    try {
      const data = await api<{ agents: AgentRecord[]; templates: Record<string, AgentTemplate> }>("/api/agents");
      setAgents(data.agents || []);
      setTemplates(data.templates || {});
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setLoading(false);
    }
  }

  async function deployAgent(agentId: string, templateKey?: string) {
    setDeploying(true);
    setError(null);
    try {
      const token = await csrfToken();
      const body: Record<string, unknown> = { id: agentId };
      if (templateKey) {
        body.template = templateKey;
      } else {
        body.image = customImage;
        if (customEnv.trim()) {
          const env: Record<string, string> = {};
          customEnv.split("\n").filter(Boolean).forEach((line) => {
            const [k, ...v] = line.split("=");
            if (k) env[k.trim()] = v.join("=").trim();
          });
          body.env = env;
        }
      }
      await api("/api/agents/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
        body: JSON.stringify(body),
      });
      await loadAgents();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setDeploying(false);
      setCustomImage("");
      setCustomEnv("");
    }
  }

  async function agentAction(agentId: string, action: "start" | "stop" | "remove") {
    setError(null);
    try {
      const token = await csrfToken();
      await api(`/api/agents/${encodeURIComponent(agentId)}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": token },
        body: "{}",
      });
      if (action === "remove") setLogsFor(null);
      await loadAgents();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
  }

  async function loadLogs(agentId: string) {
    try {
      const data = await api<{ logs: string }>(`/api/agents/${encodeURIComponent(agentId)}/logs`);
      setLogs(data.logs || "");
    } catch {
      setLogs("(unable to retrieve logs)");
    }
  }

  useEffect(() => {
    void loadAgents();
  }, []);

  return (
    <div className="h-full overflow-y-auto p-4 scrollbar-thin sm:p-6">
      <div className="mx-auto max-w-[1400px] space-y-4">
        <div className="rounded-xl border border-border bg-card p-4 shadow-card">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-xs font-bold uppercase tracking-wide text-muted-foreground">Container Management</p>
              <h1 className="mt-1 ui-title-row text-2xl font-extrabold">
                <Cpu className="size-6" /> <span>Hosted Agents</span>
              </h1>
              <p className="mt-1 max-w-3xl text-sm text-muted-foreground">Deploy, manage, and monitor AI agent containers directly from the WebUI. Agents are auto-registered as scan targets.</p>
            </div>
            <Button variant="secondary" onClick={() => void loadAgents()} className="shrink-0"><RefreshCw /> <span>Refresh</span></Button>
          </div>
          {error ? <div className="mt-4 rounded-lg border border-[var(--sev-high)] bg-[var(--sev-high)]/10 p-3 text-sm"><p className="ui-title-row font-bold"><AlertTriangle className="size-4 shrink-0 text-[var(--sev-high)]" /> <span>{error}</span></p></div> : null}
        </div>

        <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(300px,400px)]">
          <section className="space-y-3">
            <h2 className="text-lg font-extrabold">Running Agents ({agents.length})</h2>
            {loading ? <p className="text-sm text-muted-foreground">Loading agents…</p> : null}
            {!loading && agents.length === 0 ? (
              <div className="rounded-xl border border-border bg-card p-8 text-center shadow-card">
                <Server className="mx-auto mb-3 size-10 text-muted-foreground opacity-50" />
                <p className="text-sm text-muted-foreground">No agents deployed. Use the panel on the right to deploy from a template or custom image.</p>
              </div>
            ) : null}
            <div className="space-y-2">
              {agents.map((agent) => (
                <div key={agent.id} className="rounded-xl border border-border bg-card p-4 shadow-card">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div className="min-w-0">
                      <span className="ui-title-row font-bold"><Box className="size-4" /> <span>{agent.id}</span></span>
                      <p className="mt-0.5 text-xs text-muted-foreground font-mono">{agent.image}</p>
                      <p className="text-xs text-muted-foreground">{agent.container_id?.substring(0, 12)} · {agent.ports}</p>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className={cn("flex items-center gap-1 rounded px-2 py-0.5 text-[10px] font-bold uppercase", statusColor(agent.status))}>
                        {statusIcon(agent.status)} <span>{agent.status.split("(")[0].trim()}</span>
                      </span>
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {agent.status.toLowerCase().includes("up") ? (
                      <Button size="sm" variant="secondary" onClick={() => agentAction(agent.id, "stop")}><Square className="size-3.5" /> <span>Stop</span></Button>
                    ) : (
                      <Button size="sm" variant="secondary" onClick={() => agentAction(agent.id, "start")}><Play className="size-3.5" /> <span>Start</span></Button>
                    )}
                    <Button size="sm" variant="ghost" onClick={() => { setLogsFor(logsFor === agent.id ? null : agent.id); if (logsFor !== agent.id) void loadLogs(agent.id); }}><Eye className="size-3.5" /> <span>Logs</span></Button>
                    <Button size="sm" variant="danger" onClick={() => agentAction(agent.id, "remove")}><Trash2 className="size-3.5" /> <span>Remove</span></Button>
                  </div>
                  {logsFor === agent.id ? (
                    <pre className="mt-3 max-h-48 overflow-auto rounded-lg bg-muted p-3 text-[11px] leading-relaxed text-muted-foreground font-mono scrollbar-thin">{logs || "(no logs)"}</pre>
                  ) : null}
                </div>
              ))}
            </div>
          </section>

          <aside className="space-y-4">
            <div className="rounded-xl border border-border bg-card p-4 shadow-card">
              <h3 className="ui-title-row font-bold"><Plus className="size-4" /> <span>Deploy from Template</span></h3>
              <p className="mt-1 text-xs text-muted-foreground">Pre-defined agent images with auto-registered scan targets.</p>
              <div className="mt-3 space-y-2">
                {Object.entries(templates).map(([key, tmpl]) => (
                  <div key={key} className="rounded-lg border border-border bg-canvas p-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="font-semibold text-sm">{tmpl.display_name}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">{tmpl.description}</p>
                      </div>
                      <Button size="sm" variant="primary" disabled={deploying} onClick={() => deployAgent(key, key)}>
                        {deploying ? <Loader2 className="size-3.5 animate-spin" /> : <Plus className="size-3.5" />}
                        <span>Deploy</span>
                      </Button>
                    </div>
                  </div>
                ))}
                {Object.keys(templates).length === 0 ? <p className="text-xs text-muted-foreground">No templates configured. Add them to config/agent_templates.yaml.</p> : null}
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card p-4 shadow-card">
              <h3 className="ui-title-row font-bold"><Server className="size-4" /> <span>Deploy Custom Image</span></h3>
              <p className="mt-1 text-xs text-muted-foreground">Deploy any Docker image as a hosted agent.</p>
              <div className="mt-3 space-y-3">
                <label className="block">
                  <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Docker image</span>
                  <input value={customImage} onChange={(e) => setCustomImage(e.target.value)} className="input mt-1 font-mono text-sm" placeholder="my-agent:latest" />
                </label>
                <label className="block">
                  <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Environment variables (KEY=VALUE, one per line)</span>
                  <textarea value={customEnv} onChange={(e) => setCustomEnv(e.target.value)} className="input mt-1 min-h-20 font-mono text-xs" placeholder="OPENAI_API_KEY=sk-..." />
                </label>
                <Button variant="success" className="w-full" disabled={deploying || !customImage.trim()} onClick={() => deployAgent(customImage.trim().replace(/[^a-zA-Z0-9_-]/g, "-"))}>
                  {deploying ? <Loader2 className="size-4 animate-spin" /> : <Terminal className="size-4" />}
                  <span>Deploy</span>
                </Button>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
