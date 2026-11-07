#!/usr/bin/env bash
set -euo pipefail
indexsha="$1"
proofsha="$2"
root=/var/www/blastlab
archive=/tmp/phase25-hostile-ui.tar.gz
stage=/tmp/phase25-hostile-ui
backup=/opt/blastlab/backups/20261107-phase25-hostile-ui
test -n "$indexsha" && test -n "$proofsha"
test ! -e "$backup"
test -f "$root/index.html" && test -d "$root/assets"
mkdir -p "$stage" "$backup/assets"
tar -xzf "$archive" -C "$stage"
test "$(sha256sum "$stage/index.html" | cut -d ' ' -f1)" = "$indexsha"
test "$(sha256sum "$stage/proof/evidence.json" | cut -d ' ' -f1)" = "$proofsha"
python3 - "$stage/proof/evidence.json" <<'PY'
import json,sys
p=json.load(open(sys.argv[1],encoding="utf8"))
assert p["schema"]=="blastlab.phase24.proof-index.v1"
assert p["status"]=="FOUR_TECHNICAL_PROOFS_VERIFIED"
assert p["claims"]["same_agent"]["metric"]=="3 to 0"
assert p["claims"]["termproof"]["metric"]=="0 to 6"
assert p["claims"]["contained"]["metric"]=="22 / 22"
assert p["claims"]["framework"]["metric"]=="0 to 0"
assert len(p["proof_debts"])>=6
assert not any(s in open(sys.argv[1],encoding="utf8").read().lower() for s in ("join_token","recovery_key","private_key","api_key"))
PY
cp -p "$root/index.html" "$backup/index.html"
cp -a "$root/assets/." "$backup/assets/"
if test -e "$root/proof/evidence.json"; then
  cp -p "$root/proof/evidence.json" "$backup/evidence.json"
fi
rollback(){
 cp -p "$backup/index.html" "$root/index.html"
 if test -f "$backup/evidence.json"; then
   cp -p "$backup/evidence.json" "$root/proof/evidence.json"
 else
   rm -f "$root/proof/evidence.json"
 fi
 echo "PHASE25_PROOF_RELEASE_RESTORED"
}
trap rollback ERR
cp -a "$stage/assets/." "$root/assets/"
install -d -m 0755 "$root/proof"
install -m 0644 "$stage/proof/evidence.json" "$root/proof/evidence.json"
install -m 0644 "$stage/index.html" "$root/index.html"
test "$(sha256sum "$root/index.html" | cut -d ' ' -f1)" = "$indexsha"
test "$(sha256sum "$root/proof/evidence.json" | cut -d ' ' -f1)" = "$proofsha"
curl -fsS --max-time 15 https://blastlab.45-77-138-147.sslip.io/proof | grep -q 'assets/index-'
curl -fsS --max-time 15 https://blastlab.45-77-138-147.sslip.io/proof/evidence.json | grep -q 'FOUR_TECHNICAL_PROOFS_VERIFIED'
curl -fsS --max-time 12 http://127.0.0.1:8123/api/health >/dev/null
curl -fsS --max-time 12 http://127.0.0.1:8123/api/contained-sample/latest | grep -q '"status"'
trap - ERR
echo "PHASE25_PUBLIC_PROOF_RELEASE_PASS"
