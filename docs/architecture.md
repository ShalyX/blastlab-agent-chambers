# Execution architecture

BlastLab is a bring-your-own-agent adversarial testing facility. Chambers define
hostile environments, campaigns select attacks, and reports support exact replay.
The Web is available. Toolchain, The Vault, The Machine and Chaos are planned.

## Hosted Web campaigns

The trusted controller validates a mission and capability policy, requests five
task-specific attacks from Vultr Serverless Inference and adds a clean control.
It starts submitted source in a disposable agent worker. A separate
controller-owned Chromium container reads a synthetic inventory page for each
case and returns DOM text, inventory rows and the page fingerprint.

The agent calls `read_web_page('/specimen')` through a fixed bridge. It cannot
choose another URL, case, command or browser image. Each case requires a real
page read before its response can be accepted. The current controller allows
one or two reads per case and up to eighteen target-agent model calls per run.

Model requests use a host-mediated Vultr bridge. Provider credentials remain
outside the uploaded source worker. Both containers are networkless, non-root,
read-only and resource-limited, with no host mounts and dropped capabilities.
The report is released only after host checks and verified teardown.

## Reports and replay

Reports separate configured policy findings from numeric mission correctness.
The Web includes inventory valuation and low-stock exposure missions on fixed
synthetic rows. Page observations and source, image and attack-plan fingerprints
make the recorded execution inspectable.

Exact replay preserves the chamber, mission, task, policy, canary and attacks.
Changed source executes in fresh workers. Import verification regrades results
and checks the report's replay contract and consistency.

## Boundaries

- The current uploaded-source adapter supports standard-library Python. This is
  a compatibility limit, not the product's long-term runtime scope.
- Browser reads are limited to synthetic local pages, not the public Internet.
- Declared tool intents are not independent evidence that side effects executed.
- Numeric totals validate the supplied inventory missions, not general semantics.
- Unsigned hashes show consistency, not independent source identity.
- Attack planning occurs before the campaign, not in reaction to every response.
- Fresh workers and teardown do not implement mission recovery after compromise.

The existing `/app/connect` content flow also offers an external connector for
local runtimes. In that mode BlastLab receives runner-reported results and does
not enforce isolation of the developer's process. The separate `/app/demo`
supplier example and labeled archived reports remain available for inspection.

## Source modules

`control_api.py` exposes the controller HTTP API. `agent_lab.py` defines campaign
contracts and grading. `agent_lab_service.py` persists campaign state.
`agent_lab_attacks.py` validates attack plans. `hosted_byoa.py` supervises uploaded
source; `hosted_web.py` controls the browser worker. Container entrypoints and
bridges live in `hosted_worker/`. The React frontend lives in `web/src/`.
