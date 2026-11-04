# BLASTLAB browser spike

The user mission remains a verified supplier stock valuation. A real Chromium
worker reads inventory HTML, including a hostile supplier note. The supervisor
passes that observation to the planner. Every proposed tool call crosses a fixed
policy boundary before dispatch. Only exact `browse({path:"/supplier"})` and
independently verified `finish({total_value_cents,evidence_id})` are capabilities.
There is no model-accessible shell, host filesystem, arbitrary URL, or lifecycle
operation. Page text cannot grant authority. The browser also blocks every
request except the exact local supplier route, disables page JavaScript, blocks
service workers and rejects downloads.

`agent_spike.py`, `browser_inference.py`, `browser_sandbox.py`, and
`browser-worker.cjs` form this independent browser path. The parallel
`blastlab_agent.py` process/HTTP spike uses `vultr_adapter.py` and `sandbox.py`;
its artifacts and deployment image are separate. `inference.py` was an initial
adapter copy and is not imported by either entry point.

## Executable local path

Requires Python 3.12+, Node, Playwright and Chromium. This machine already has
Playwright through the global `@playwright/cli` package and system Chrome; the
worker discovers that installation without another package install. For a clean
development machine:

```sh
npm install --no-save playwright@1.56.1
npx playwright install chromium
python agent_spike.py doctor
python agent_spike.py run --provider deterministic --sandbox local
python agent_spike.py run --provider deterministic --sandbox local --benign
python -W error -m unittest -v
```

The explicit deterministic provider is a **SIMULATED**, intentionally susceptible
planner. It reads `ATTACK_ACTIONS` from the actual browser observation and replays
them through the real policy. The fixture is not a model, classifier, or measure
of LLM susceptibility. It also computes from observed rows; the answer is not
hardcoded. Local browser execution and actual process/workspace removal are
**OBSERVED**. The local provider has no OS security isolation or enforceable
memory cap and must not be used for arbitrary hostile executable code.

The supervisor saves a hash-checked pending checkpoint outside the worker, destroys
the browser process and its scratch directory after the first page read, then
creates a new worker with a different identity and scratch directory. It reloads
the conversation checkpoint, invalidates earlier receipts, and requires another
page read before completion. This is task resume in a fresh environment; browser
memory and profile state are not restored. Final cleanup destroys the second
worker too. It is a scheduled supervisor fault, not a successful injected deletion.

Each run writes a unique `artifacts/agent-run-*/result.json`, complete ordered
`trace.jsonl`, checkpoint and supervisor sentinel. The trace records source hashes,
public model requests/responses, proposed calls, allow/deny decisions, browser
observations, worker lifecycle and verification. Events have UTC timestamps,
sequence numbers and a SHA-256 chain, flushed to disk per event. This supports
inspection and tamper detection relative to a retained hash; it is not a signed,
externally anchored audit log. API headers and private model reasoning are excluded.
The configured inference key is redacted if echoed in public model output.

## Exact live gate

The default execution mode is `--provider vultr --sandbox docker`. It fails before
starting a worker if either `VULTR_INFERENCE_API_KEY` or `VULTR_INFERENCE_MODEL` is
missing. Supply the **Serverless Inference subscription key**, not the optional
Vultr management API key, and an exact enabled tool-capable model ID. There is no
guessed model or automatic provider fallback. Do not paste keys into transcripts.

Configuration can come from the process environment or the explicit
`--env-file .env.vultr` option, using `.env.vultr.example`. Files are parsed as data,
never sourced or evaluated; existing process variables take precedence. Secret
files are gitignored. `doctor` emits presence booleans only. All live LLM traffic
goes directly to `https://api.vultrinference.com/v1/chat/completions` with native
function-tool schemas. Redirects, unexpected returned model IDs, truncated or
invalid output, HTTP errors, rate limits and timeouts halt the run without
switching providers. A mock transport is labeled `vultr-contract-mock` and cannot
produce live evidence.

## Vultr VM execution path

1. Supply an existing authorized Vultr Linux VM or provision one externally.
   `VULTR_VM_HOST`, `VULTR_VM_USER`, and `VULTR_VM_SSH_KEY` document the missing
   target/access configuration. They are not proof of a deployment and are not
   needed when executing directly on an already verified VM. An instance ID,
   region, and authenticated control-plane check are needed to establish Vultr
   provenance. No VM was provisioned by this local spike.
2. Install Python 3.12+ and Docker on that VM. Copy source to `/opt/blastlab` and
   build `docker build -f Dockerfile.sandbox -t blastlab-browser:spike .`.
   The separate `deploy/Dockerfile.sandbox` belongs to the HTTP process spike.
3. Run `python3 agent_spike.py run --provider deterministic --sandbox docker`.
   Then execute the explicit container test:
   `BLASTLAB_TEST_BROWSER_DOCKER=1 python3 -W error -m unittest -v test_browser_agent.BrowserDockerTests`.
4. Create dedicated user `blastlab` with Docker access. Put the real key/model in
   `/etc/blastlab/inference.env`, mode 0600, outside the checkout. Install
   `deploy/blastlab-browser-spike.service` in `/etc/systemd/system/`, reload systemd
   and start it. Its command runs the real Vultr adapter and Docker worker. Output
   is retained under `/var/lib/blastlab-browser/agent-run-*`.
5. Retain the successful result and trace, exact returned model and usage, Docker
   lifecycle evidence, and VM control-plane provenance before claiming the live
   requirements passed. The spike is a headless backend job; public demo URL and
   product UI remain outside this technical de-risk scope.

Docker gets no host bind mount, socket, API key, inherited environment or external
network. It has a read-only root, temporary `/tmp`, separate shared memory, an
unprivileged UID, all capabilities dropped, no-new-privileges, PID/CPU/memory caps,
and an independent 90-second process lease. The supplier server runs inside the
same disposable container. The trusted controller holds Docker authority; it must
never be exposed as a tool. Image tags/package versions are fixed but not digest
pinned, and Docker is not a guarantee against kernel/browser escapes. This
container path is **UNPROVEN until actually built and executed**.

Official sources checked on 2026-11-01: [Agent Rush requirements](https://community.vultr.com/e/vultr-agent-rush-hackathon),
[Vultr native tool API](https://api.vultrinference.com/docs/reference/create-chat-completion),
[Vultr quickstart](https://api.vultrinference.com/docs/get-started/quickstart), and
[Docker runtime controls](https://docs.docker.com/engine/containers/run/).
