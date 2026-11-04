# Vultr VM execution gate

This is a deployable headless backend job, not evidence of an existing Vultr VM.
No provisioning, DNS, firewall, SSH, or cloud charges were performed by this spike.

1. Supply/provision a Vultr Linux VM with Python 3.12+ and Docker. Record the
   instance ID/region and verify the machine through Vultr control-plane evidence.
2. Copy this source to `/opt/blastlab`. Create a dedicated `blastlab` service user
   with a writable `/var/lib/blastlab` and Docker access. Docker access is privileged
   host authority: it belongs only to the trusted controller, never the model worker.
3. From `/opt/blastlab`, build the fixed image:

   ```sh
   docker build -f deploy/Dockerfile.sandbox -t blastlab-sandbox:spike .
   ```

4. Put the real inference key and enabled model in `/etc/blastlab/inference.env`,
   following `inference.env.example`; protect it with mode 0600. The system service
   manager reads it. Do not put credentials in command arguments, source, container
   env, checkpoint, or artifacts.
5. Install the supplied service in `/etc/systemd/system/`. Run
   `sudo systemctl daemon-reload` then `sudo systemctl start blastlab-spike`.
   Read `/var/lib/blastlab/agent-latest.json` and the linked JSONL trace.
   A second service start creates a separate run. The service exits nonzero on
   failure; it has no exposed HTTP port or UI.
6. Run `python3 -W error -m unittest -v` on the VM. Also run
   `BLASTLAB_TEST_DOCKER=1 python3 -W error -m unittest -v test_blastlab_agent.DockerTests`.
   This explicitly opts into Docker tests; absence is a reported skip elsewhere.

   For the separate browser container image, build with the root `Dockerfile.sandbox`
   as `blastlab-browser:spike`, then opt in with `BLASTLAB_TEST_BROWSER_DOCKER=1`
   and run `test_browser_agent.BrowserDockerTests`. The root image uses Playwright;
   the deployment service supplied here uses the standard-library worker image.

The Docker worker has no network except its own loopback, no host mounts, no
credentials, a read-only root, a size-limited disposable tmpfs, an unprivileged UID,
all capabilities dropped, no-new-privileges, and CPU/memory/PID limits. Its supplier
web source runs inside the same isolated namespace. This measures a local web
mission; it does not demonstrate external Internet browsing or a browser engine.
Destroy removes the named container and verifies its absence; reset creates a
different container. The trusted controller restores only the pending conversation
checkpoint and requires a fresh page read. Worker state is never mounted on host.

The local process fallback has actual process/workspace destruction but only an
application capability boundary, not OS isolation. Docker configuration remains
UNPROVEN until built and executed. Neither path permits model-generated Python,
shell, arbitrary filesystem targets, arbitrary URLs, or sandbox lifecycle tools.

The transport follows Vultr's official [chat completion API](https://api.vultrinference.com/docs/reference/create-chat-completion)
and [quickstart](https://api.vultrinference.com/docs/get-started/quickstart).
It uses JSON content actions for compatibility, not native function calling.
All live LLM calls use the fixed Vultr endpoint; redirects, provider substitution,
model mismatch, malformed/truncated output, and transport failures fail closed.
