# BlastLab | Visual and Interaction QA
November 4, 2026. Local Chrome desktop 1440x900 and mobile 390x844, reduced-motion captures.
Local captures (ignored by Git): web/qa/landing-desktop.png, control-desktop.png, evidence-desktop.png, architecture-desktop.png, control-scripted-stage.png, landing-mobile.png, control-mobile.png.

## Issues found and fixed
1. Mobile Control Room topbar + button extended beyond viewport. Fixed flexible, ellipsized breadcrumb and bounded action controls; final width 390/390.
2. Landing art shadow caused 7px mobile overflow. Clipped x overflow in mobile mode; final width 390/390.
3. Replay initially began with a blank specimen. Default starts at genuine hostile page for live model and first denial for scripted stress case, immediately showing the causal evidence.

## Actual interaction tests passed
- Live to adversarial source switch retains visible SCRIPTED FIXTURE designation and shows policy DENIED state/execute_shell proposal.
- Runtime inspector tab changes view.
- Evidence and Architecture navigation.
- New Test Run modal refuses blank owner token.
- Mobile navigation to Evidence.
- Local browser interaction suite emitted zero JavaScript page errors.
- The deployed production owner API passed fresh scripted and real-model starts and completed VM Docker runs.

## Caveats
The local Vite proxy returned HTTP 500 for optional /api calls while development API was not connected, but authentic bundled evidence fallback remained usable; production API returned 200. During a public multi-page Chrome screenshot sweep, the PC experienced temporary network/DNS changes; repeated public curl tests later returned 200/valid TLS across routes, and local mobile QA passed. No formal WCAG or independent pentest completed.
