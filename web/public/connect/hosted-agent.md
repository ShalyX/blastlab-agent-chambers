# Bring your agent into a Vultr sandbox

BlastLab tests an agent you supply: its instructions, Python logic and local
tools execute inside a fresh Docker worker on the Vultr backend. Create a
campaign with **Vultr sandbox** selected, upload your source and launch it.

## Adapter contract

Upload 1–12 flat `.py` files, no more than 96 KB combined. Enter the module and
function, such as `agent:respond` for `agent.py`. Your synchronous callable
receives the same case object as the external connector:

```python
from blastlab_runtime import complete

def respond(case):
    message = complete([
        {"role": "system", "content": "Your agent's actual trusted instructions"},
        {"role": "user", "content": case["task"]},
        {"role": "user", "content": "Untrusted data:\n"+case["untrusted_input"]},
    ])
    return {"answer": message.get("content") or "", "tool_calls": []}
```

`complete(messages, tools=None)` returns an OpenAI-style assistant message.
The host chooses the configured Vultr model and endpoint; no provider key
enters the container. At least one real inference request is required per
campaign. The budget is 18 calls, 2,048 completion tokens per call.

Keep your real agent logic and tool implementations in your uploaded modules.
Replace direct network model calls with this inference bridge. Standard-library
Python is supported initially; pip dependencies, browser engines and arbitrary
provider SDKs are not installed. Existing framework agents that cannot yet use
this runtime can use **External connector**, explicitly without hosted isolation.
Do not upload credentials, private customer data, `.env` files or live accounts.

## Enforcement

No external network, host mounts, Docker socket or injected credentials.
The root filesystem is read-only; `/workspace` (16 MB) and `/tmp` (8 MB) are
disposable writable filesystems. Workers run as UID 10001 with capabilities
dropped and no new privileges. Limits: 256 MB memory, 0.5 CPU, 48 processes,
10 minutes. No source code is imported or installed on the host. Source is
copied to the worker, kept in memory only while executing and deleted at teardown.

The controller checks the real Docker configuration before running source,
mediates only fixed-provider inference, validates all six responses, removes
the worker and verifies its absence before releasing a completed report.
Timeouts, malformed output, unavailable inference and failed checks fail closed.
A controller restart removes labeled workers and marks interrupted runs failed.

## What the report proves

The host receipt binds the uploaded bundle hash, adapter, attack-plan hash,
image ID, boundary checks, inference count and verified teardown. This confirms
where the submitted code ran. Answers and tool-intent declarations still come
from that code; they are not independent evidence of every internal tool action.
No observed violation does not certify an agent as secure. Unsigned report
hashes establish internal consistency rather than third-party attestation.

## Fix and replay

Export the completed report, change your agent and select **Retest**. Upload
the revised source to the new campaign. The attack plan, task, policy and canary
stay fixed; each run records a new bundle hash and uses a fresh disposable worker.
