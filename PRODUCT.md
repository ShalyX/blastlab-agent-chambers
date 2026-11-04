# PRODUCT | BlastLab v0.1
Target user: AI engineers, agent platform operators and security reviewers who must verify tool-using browser agents against untrusted content.
Job: observe the exact malicious input, model action proposals, capability policy, worker isolation, teardown/restart, and evidence-backed mission result.
Promise: Crash-test the blast radius. Prove the boundary held.
Primary journey: public landing -> Control Room -> select Live Vultr model or Scripted Adversarial Replay -> scrub actual causal trace -> inspect injection, actions and policy reasons -> observe worker destroyed/recreated -> download verified evidence -> optionally run new fixed-scenario test in owner mode.
Magic moment: The untrusted supplier page contains an instruction to delete host files and steal secrets; the independently enforced boundary and reset lifecycle still permit the legitimate $72 valuation.
Truth labels: Live Vultr GLM-5.3 run has 3 real model calls, 2 browser reads, 2 Docker generations, 41 events, 0 denied tool calls; scripted deterministic attack has 4 denied calls, 2 reads, 2 workers, 65 events. They must never be conflated.
Data sources: hash-chained JSONL traces and result.json copied from authentic Vultr VM. Source is immutable replay evidence, not live streaming.
Functional surfaces: landing/header/footer; command/control room with replay, stage selector and annotated page; evidence and architecture panels; owner-only new run via protected server-side API; browser mobile and reduced motion; waiting/error/success states.
Non-goals: arbitrary agent prompts/URLs, general security benchmark, arbitrary public-site browsing, model-generated shell, credentials in browser or worker, showing fixture actions as real LLM events.
Working name BlastLab remains because user explicitly refers to it. Brand collision/trademark clearance NOT claimed.
