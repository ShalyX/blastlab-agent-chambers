export type Mode = 'live' | 'scripted';
export type Section = 'control' | 'evidence' | 'architecture';
export type RunEvent = {
  seq: number;
  at: string;
  kind: string;
  title: string;
  category: string;
  description: string;
  generation?: number | null;
  detail: Record<string, any>;
  hash: string;
  visible: boolean;
};
export type RunData = {
  id: string;
  label: string;
  origin: string;
  is_model_driven: boolean;
  is_scripted: boolean;
  provider: string;
  model: string | null;
  timestamp: string;
  mission: string;
  environment: {
    instance_id: string;
    vm_region: string;
    compute: string;
    sandbox: string;
    source: string;
  };
  summary: {
    completed: boolean;
    acceptance_passed: boolean;
    value_cents: number;
    elapsed_ms: number;
    model_calls: number;
    fixture_turns: number;
    denied_actions: number;
    browser_reads: number;
    worker_generations: number;
    destroyed_containers: number;
    reset_verified: boolean;
    supervisor_sentinel_unchanged: boolean;
    event_count: number;
  };
  proof: {
    trace_sha256: string;
    hash_chain_valid: boolean;
    trace_started_at: string;
    trace_finished_at: string;
    security_checks: { label: string; ok: boolean }[];
  };
  events: RunEvent[];
};
