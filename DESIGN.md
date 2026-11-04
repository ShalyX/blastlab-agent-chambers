# DESIGN | BlastLab control room composition lock
Updated 2026-11-04. Art direction LOCKED; screenshot QA pending.

Product reality: buyer is an AI engineer/security reviewer. Task is proving prompt-injection handling on a browser agent with bounded tool access, real worker destruction and restart. First 30 seconds must communicate the verified host/worker boundary and resumed $72 mission. Product surfaces required: public landing/header/footer; Control Room; Evidence; Architecture; owner-run auth; errors/loading/success; mobile; reduced-motion. No OAuth or wallet in this product.

## Three distinct visual directions explored
A. Forensic newspaper: warm paper incident report, annotated code as exhibits, editorial scroll. Great for archive, but weak as interactive execution rig. REJECT.
B. Containment switchboard: dark debugger-inspired test rig, wide horizontal filmstrip split by signal-orange rupture at hard kill, right forensic inspector, tactile playback scrubber, evidence strip. Cause-and-effect is self-evident; no invented numbers. SELECT.
C. Cutaway test facility: diagram-first axonometric 3D Docker test chamber, drag inputs through boundaries. Memorable but burdensome 3D and weak raw-trace readability; risky for reliable live demo. REJECT.

## Composition target: landing desktop (1440x900)
72px utility header; left containment bracket mark and wordmark; right clear Open control room action.
Hero left 48%: INDEX / TEST BENCH eyebrow, oversized editorial line breaks: Your agent read the attack. / The boundary held. Then 2 short explanation lines and CTA. Hero right 52%: actual proof-driven diagram of untrusted document entering hard-edge Docker chamber; big signal-orange severed instruction line and mint verification state; labels/connector hairlines, crisp measured grid. Not a generic floating screenshot or gradient blob.
Lower fold: genuine proof stat strip; flip to parchment for narrative/architecture; clear limitations; footer.
Mobile: single-column no clipping; diagram compresses vertically preserving actual boundary.

## Composition target: control room desktop
Left 224px rail: brand, Control Room, Evidence, Architecture and sponsor/provider footer. Right: breadcrumbs and source provenance, run-mode selector and owner action.
Big mission headline anchors main stage; beneath it a singular wide execution-track filmstrip, gen 01 -> sharp orange kill seam -> gen 02, with playhead and click/keyboard controls.
Under track left 60% supplier document (inventory table and orange-highlighted untrusted content), right 40% action/policy inspector that changes per selected trace event. Bottom concise evidence strip with correct model, worker, checksum, proof.
Scripted mode is persistently labeled SCRIPTED FIXTURE / NOT LIVE MODEL. Live mode is labeled LIVE VULTR MODEL; zero live denied actions is displayed truthfully.
On narrow screens rail collapses to top nav and columns stack; timeline scrolls. Focus visible and reduced-motion behavior mandatory.

## Signature interaction
Every scrub step corresponds to a real normalized trace record. At trusted_interruption / sandbox_destroyed playhead reaches orange rupture, showing worker 01 destroyed, container absent, workspace gone. At sandbox_created / mission_resumed show worker 02 with new ID and checkpoint restored. The supervisor initiates teardown, not the model.
Animation is causal, not decorative. Playhead progresses with restrained 240ms transitions; orange pulse only on actual teardown; reduced-motion disables pulse.

## Assets and proof
Primary assets: actual trace records, original supplier page text, worker IDs, SHA-256 evidence, custom SVG emblem; no stock/generative art required. Make browser-safe sanitized data but never silently modify claims. Display live/simulated source distinction at all times.
Hard veto: generic SaaS dashboard grid, no hostile input viewer, four scripted denials shown as real LLM, missing landing/header/footer, broken mobile, dummy buttons, unprotected run trigger, claiming visual pass without actual screenshots.

Gate: A/B/C explored, B selected and frozen for implementation. Rendered Visual QA NOT VERIFIED until desktop/mobile screenshots and interaction-state inspection.
