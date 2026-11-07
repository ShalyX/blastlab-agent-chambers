"""Publish only static Phase25 proof UI + sanitized index, with rollback backup."""
from __future__ import annotations
import hashlib
import json
import subprocess
import tarfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"web/dist"
KEY=Path.home()/".ssh"/"blastlab_vultr_2026"
HOST="root@45.77.138.147"
ARCHIVE=ROOT/"artifacts/phase25-hostile-ui.tar.gz"
INSTALL=ROOT/"artifacts/phase25-hostile-ui-install.lf.sh"
OPTS=["-i",str(KEY),"-o","BatchMode=yes","-o","IdentitiesOnly=yes",
      "-o","ConnectTimeout=14","-o","ConnectionAttempts=1",
      "-o","StrictHostKeyChecking=accept-new"]

def execute(label,argv,attempts=1):
    for i in range(attempts):
        print("PHASE25_STEP",label,"ATTEMPT",i+1,flush=True)
        try:
            p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=75)
        except subprocess.TimeoutExpired:
            if i==attempts-1:raise RuntimeError(label+" timeout; inspect host before retry")
        else:
            if p.returncode==0:
                print("PHASE25_STEP_PASS",label,p.stdout.strip()[-280:],flush=True)
                return
            print("PHASE25_STEP_FAIL",label,p.returncode,p.stdout[-350:],p.stderr[-350:],flush=True)
            if i==attempts-1:raise RuntimeError(label+" failed; inspect host before retry")
        time.sleep(3*(i+1))

assert KEY.is_file()
index=DIST/"index.html"
proof=DIST/"proof/evidence.json"
assets=list((DIST/"assets").iterdir())
assert index.is_file() and proof.is_file() and assets
data=json.loads(proof.read_text(encoding="utf8"))
assert data["status"]=="FOUR_TECHNICAL_PROOFS_VERIFIED"
assert data["claims"]["termproof"]["metric"]=="0 to 6"
assert data["claims"]["same_agent"]["metric"]=="3 to 0"
assert all(x.is_file() for x in assets)
with tarfile.open(ARCHIVE,"w:gz") as tar:
    tar.add(index,arcname="index.html")
    tar.add(proof,arcname="proof/evidence.json")
    for a in assets:tar.add(a,arcname="assets/"+a.name)
INSTALL.write_bytes((ROOT/"deploy/phase25_hostile_ui_install.sh").read_bytes().replace(b"\r\n",b"\n"))
assert b"\r" not in INSTALL.read_bytes()
indexsha=hashlib.sha256(index.read_bytes()).hexdigest()
proofsha=hashlib.sha256(proof.read_bytes()).hexdigest()
print("PROOF_RELEASE_STAGED",json.dumps({"bytes":ARCHIVE.stat().st_size,
      "index_sha256":indexsha,"proof_sha256":proofsha}),flush=True)
execute("preflight",["ssh",*OPTS,HOST,
  "test ! -e /opt/blastlab/backups/20261107-phase25-hostile-ui && test -f /var/www/blastlab/index.html && systemctl is-active --quiet blastlab-control-api.service && echo READY"],3)
execute("stage",["scp",*OPTS,str(ARCHIVE),str(INSTALL),HOST+":/tmp/"],3)
execute("install",["ssh",*OPTS,HOST,"bash /tmp/phase25-hostile-ui-install.lf.sh "+indexsha+" "+proofsha],1)
print("PHASE25_PROOF_DEPLOYED",flush=True)
