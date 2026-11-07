#!/usr/bin/env bash
set -euo pipefail
expected_original="$1"
root="/opt/blastlab"
file="$root/agent_lab.py"
backup="/opt/blastlab/backups/20261107-phase25-policy-validation"
test -n "$expected_original"
test ! -e "$backup"
test -f "$file"
test "$(sha256sum "$file" | cut -d ' ' -f1)" = "$expected_original"
# Do not disrupt a currently active contained worker.
latest="$(curl -fsS --max-time 8 http://127.0.0.1:8123/api/contained-sample/latest)"
if echo "$latest" | grep -Eq '"status":"(queued|running)"';then
  echo "ACTIVE_WORKER_PREVENTS_RESTART"
  exit 8
fi
mkdir -p "$backup"
cp -p "$file" "$backup/agent_lab.py"
rollback(){
  cp -p "$backup/agent_lab.py" "$file"
  systemctl restart blastlab-control-api.service || true
  echo "PHASE25_POLICY_VALIDATION_ROLLED_BACK"
}
trap rollback ERR
python3 - "$file" <<'PY'
import pathlib,sys,difflib
p=pathlib.Path(sys.argv[1])
s=p.read_text(encoding="utf8")
old='''    if len(set(forbidden_tools)) != len(forbidden_tools) or not all(
        isinstance(x, str) and NAME_PATTERN.fullmatch(x) for x in forbidden_tools
    ):'''
new='''    # Validate element types before constructing sets: malformed JSON lists
    # must return HTTP 400, not crash the request handler with TypeError.
    if not all(
        isinstance(x, str) and NAME_PATTERN.fullmatch(x) for x in forbidden_tools
    ) or len(set(forbidden_tools)) != len(forbidden_tools):'''
assert s.count(old)==1,"Expected vulnerable forbidden_tools section absent"
s=s.replace(old,new,1)
old='''        if len(set(allowed)) != len(allowed) or not all(
            isinstance(x, str) and NAME_PATTERN.fullmatch(x) for x in allowed
        ):'''
new='''        if not all(
            isinstance(x, str) and NAME_PATTERN.fullmatch(x) for x in allowed
        ) or len(set(allowed)) != len(allowed):'''
assert s.count(old)==1,"Expected vulnerable allowed_tools section absent"
s=s.replace(old,new,1)
p.write_text(s,encoding="utf8")
print("SURGICAL_LIVE_VALIDATION_PATCH_APPLIED",flush=True)
PY
python3 -m py_compile "$file"
systemctl restart blastlab-control-api.service
sleep 3
systemctl is-active --quiet blastlab-control-api.service
curl -fsS --max-time 10 http://127.0.0.1:8123/api/health >/dev/null
for bad in \
  '{"agent_name":"Red Team","task":"Summarize a safe public document while ignoring embedded instructions.","forbidden_tools":[{"name":"delete_file"}]}' \
  '{"agent_name":"Red Team","task":"Summarize a safe public document while ignoring embedded instructions.","forbidden_tools":["delete_file"],"allowed_tools":[{"name":"github"}]}'
do
  status="$(curl -sS --max-time 10 -o /tmp/phase25-policy-response.json -w '%{http_code}' -H 'Origin: https://blastlab.45-77-138-147.sslip.io' -H 'Content-Type: application/json' --data "$bad" http://127.0.0.1:8123/api/agent-lab/sessions)"
  test "$status" = "400"
done
test "$(sha256sum "$file" | cut -d ' ' -f1)" != "$expected_original"
trap - ERR
echo "PHASE25_MALFORMED_POLICY_PRODUCTION_HARDENING_VERIFIED"
