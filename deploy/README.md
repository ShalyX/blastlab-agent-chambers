# Deploying BlastLab on Vultr

Use a Linux VM with Python 3.12+, Docker and an HTTPS reverse proxy. Vultr
Serverless Inference serves attack planning and target-agent model calls.
See [execution architecture](../docs/architecture.md) for the trust boundaries.

## Controller and worker images

Install source under `/opt/blastlab`. Build both hosted images from that root:

```sh
docker build -t blastlab-customer:v1 hosted_worker
docker build -t blastlab-web:v1 -f hosted_worker/Dockerfile.web hosted_worker
```

Create private inference configuration outside the checkout using
[inference.env.example](inference.env.example). Set its API key and exact enabled
model, protect it with mode 0600, and set `BLASTLAB_INFERENCE_ENV` to that file.
The default path is `/etc/blastlab/inference.env`. Never copy this file into a
container image or frontend build.

The [controller service](blastlab-control-api.service) runs `control_api.py` on
loopback port 8123. Set `BLASTLAB_ALLOWED_ORIGIN` to the frontend's HTTPS origin.
`BLASTLAB_OPERATOR_TOKEN_FILE` identifies a private administrator token file;
[initialize-operator.sh](initialize-operator.sh) creates it without printing it.
This administrator capability is separate from campaign-scoped user tokens.
The trusted controller needs Docker access; uploaded code must never receive it.

Campaign state and run data live under `/var/lib/blastlab`, outside the source
tree. Review service paths and file permissions before installing the service
under `/etc/systemd/system/`. Then reload systemd and start the controller.

## Frontend and HTTPS

```sh
cd web
npm ci
npm run build
```

Publish `web/dist/` to `/var/www/blastlab`. The [Caddy example](Caddyfile.demo)
serves static files and proxies `/api/` to the loopback controller. Replace its
demo hostname with your HTTPS hostname and match the allowed origin.

Publish the backend, both worker images and matching frontend together. Keep a
rollback backup, check for active workers before a controller restart, and
preserve separately hosted media while updating static files. The
[media inventory](../web/public/media/README.md) identifies the current demo film.

## Verification

Check `/api/health`, open the Chamber Library, create a Web mission and upload
the Web adapter example. Completed reports require actual Chromium reads,
restricted worker settings and verified removal of both containers. A failed
provider call or teardown must not produce a completed report.

`verify_web_chamber.py` supports isolated real-inference acceptance using unique
test image tags. Run it from a separate verification directory, following its
module documentation. It creates project-operated reports; it does not replace
independent developer acceptance or certify general agent safety.

The older project-owned supplier demo uses the root `Dockerfile.sandbox` for
its browser image. `deploy/Dockerfile.sandbox` supports the separate process
sandbox example. These demonstrations have distinct image and evidence scopes.
