#!/usr/bin/env bash
set -euo pipefail
expected="$1"
archive_expected="$2"
site=/var/www/blastlab
root=/opt/blastlab
backup=/opt/blastlab/backups/20261107-phase23-fresh-sample
stage=/tmp/blastlab-phase23-fresh-sample
archive=/tmp/phase23-fresh-sample.tar.gz
test -n "$expected" && test -n "$archive_expected"
test ! -e "$backup"
test -f "$site/index.html" && test -f "$root/control_api.py"
test "$(sha256sum "$archive" | cut -d' ' -f1)" = "$archive_expected"
mkdir -p "$stage" "$backup/assets" "$backup/experiments"
tar -xzf "$archive" -C "$stage"
test "$(sha256sum "$stage/web/index.html" | cut -d' ' -f1)" = "$expected"
python3 -m py_compile "$stage/backend/control_api.py" "$stage/backend/contained_sample_service.py" "$stage/backend/experiments/byoa-containment/host_supervisor.py" "$stage/backend/experiments/byoa-containment/verify_run.py"
cp -p "$root/control_api.py" "$backup/control_api.py"
cp -p "$root/experiments/byoa-containment/host_supervisor.py" "$backup/experiments/host_supervisor.py"
cp -p /etc/systemd/system/blastlab-control-api.service "$backup/blastlab-control-api.service"
cp -p "$site/index.html" "$backup/index.html"
cp -a "$site/assets/." "$backup/assets/"
if test -f "$root/contained_sample_service.py" || test -f "$root/experiments/byoa-containment/verify_run.py"; then echo "UNCERTAIN_EXISTING_NEW_SOURCE"; exit 5; fi
rollback(){
 echo "FRESH_SAMPLE_RELEASE_ROLLBACK"
 cp -p "$backup/control_api.py" "$root/control_api.py"
 cp -p "$backup/experiments/host_supervisor.py" "$root/experiments/byoa-containment/host_supervisor.py"
 cp -p "$backup/blastlab-control-api.service" /etc/systemd/system/blastlab-control-api.service
 cp -p "$backup/index.html" "$site/index.html"
 rm -f "$site/connect/independent-tester.md"
 rm -f "$root/contained_sample_service.py" "$root/experiments/byoa-containment/verify_run.py"
 systemctl daemon-reload
 systemctl restart blastlab-control-api.service || true
}
trap rollback ERR
install -m 0644 "$stage/backend/control_api.py" "$root/control_api.py"
install -m 0644 "$stage/backend/contained_sample_service.py" "$root/contained_sample_service.py"
install -m 0644 "$stage/backend/experiments/byoa-containment/host_supervisor.py" "$root/experiments/byoa-containment/host_supervisor.py"
install -m 0644 "$stage/backend/experiments/byoa-containment/verify_run.py" "$root/experiments/byoa-containment/verify_run.py"
install -m 0644 "$stage/systemd/blastlab-control-api.service" /etc/systemd/system/blastlab-control-api.service
mkdir -p -m 0700 /var/lib/blastlab/sample-jobs
cp -a "$stage/web/assets/." "$site/assets/"
install -m 0644 "$stage/web/index.html" "$site/index.html"
install -m 0644 "$stage/web/connect/independent-tester.md" "$site/connect/independent-tester.md"
systemctl daemon-reload
systemctl restart blastlab-control-api.service
sleep 3
systemctl is-active --quiet blastlab-control-api.service
test -d /run/blastlab
curl -fsS --max-time 12 http://127.0.0.1:8123/api/health >/dev/null
curl -fsS --max-time 12 http://127.0.0.1:8123/api/contained-sample/latest | grep -q '"status"'
test "$(sha256sum "$site/index.html" | cut -d' ' -f1)" = "$expected"
curl -fsS --max-time 12 https://blastlab.45-77-138-147.sslip.io/contained-sample | grep -q "assets/index-"
trap - ERR
echo "PHASE23_FRESH_SAMPLE_RELEASE_VERIFIED"
