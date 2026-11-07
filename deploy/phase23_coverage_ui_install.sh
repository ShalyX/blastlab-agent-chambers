#!/usr/bin/env bash
set -euo pipefail
expected="$1"
root=/var/www/blastlab
archive=/tmp/phase23-coverage-ui.tar.gz
stage=/tmp/phase23-coverage-ui
backup=/opt/blastlab/backups/20261107-phase23-coverage-ui
test -n "$expected"
test ! -e "$backup"
test -f "$root/index.html" && test -d "$root/assets"
mkdir -p "$stage" "$backup/assets"
tar -xzf "$archive" -C "$stage"
test "$(sha256sum "$stage/index.html" | cut -d ' ' -f1)" = "$expected"
cp -p "$root/index.html" "$backup/index.html"
cp -a "$root/assets/." "$backup/assets/"
rollback(){
 cp -p "$backup/index.html" "$root/index.html"
 echo "COVERAGE_UI_RESTORED_INDEX"
}
trap rollback ERR
cp -a "$stage/assets/." "$root/assets/"
install -m 0644 "$stage/index.html" "$root/index.html"
test "$(sha256sum "$root/index.html" | cut -d ' ' -f1)" = "$expected"
curl -fsS --max-time 15 https://blastlab.45-77-138-147.sslip.io/contained-sample | grep -q 'assets/index-'
curl -fsS --max-time 12 http://127.0.0.1:8123/api/health >/dev/null
curl -fsS --max-time 12 http://127.0.0.1:8123/api/contained-sample/latest | grep -q 'complete'
trap - ERR
echo "COVERAGE_UI_RELEASE_PASS"
