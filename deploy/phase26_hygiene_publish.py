"""Safe static Phase26 launch hygiene release: BYOA metadata, current screenshot, accessible UI."""
from __future__ import annotations
import hashlib
import subprocess
import tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"web/dist"
KEY=Path.home()/".ssh"/"blastlab_vultr_2026"
HOST="root@45.77.138.147"
ARCHIVE=ROOT/"artifacts/phase26-hygiene.tar.gz"
INSTALL=ROOT/"artifacts/phase26-hygiene-install.lf.sh"
OPTS=["-i",str(KEY),"-o","BatchMode=yes","-o","IdentitiesOnly=yes",
      "-o","ConnectTimeout=14","-o","ConnectionAttempts=1",
      "-o","StrictHostKeyChecking=accept-new"]
def run(stage,argv,timeout=80):
    print("PHASE26_RELEASE_STEP",stage,flush=True)
    p=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True,timeout=timeout)
    if p.returncode:
        print(p.stdout[-1000:],p.stderr[-1000:],flush=True)
        raise RuntimeError(stage+" failure; inspect remote backup before repeating")
    print("PHASE26_RELEASE_OK",stage,p.stdout.strip()[-350:],flush=True)

assert KEY.is_file()
index=DIST/"index.html"
og=DIST/"og-card.png"
proof=DIST/"proof/evidence.json"
icon=DIST/"favicon.svg"
assets=list((DIST/"assets").iterdir())
assert all(p.is_file() for p in [index,og,proof,icon])
assert assets and all(p.is_file() for p in assets)
assert b"Bring Your Own Agent Security Testing" in index.read_bytes()
assert og.read_bytes()[:8]==bytes([137,80,78,71,13,10,26,10])
# PNG source is an actual browser screenshot, not an invented outcome.
with tarfile.open(ARCHIVE,"w:gz") as tar:
    for p,target in [(index,"index.html"),(og,"og-card.png"),(proof,"proof/evidence.json"),(icon,"favicon.svg")]:
        tar.add(p,arcname=target)
    for p in assets:
        tar.add(p,arcname="assets/"+p.name)
INSTALL.write_bytes((ROOT/"deploy/phase26_hygiene_install.sh").read_bytes().replace(b"\r\n",b"\n"))
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in (index,og,proof,icon)]
print("PHASE26_RELEASE_INPUTS",ARCHIVE.stat().st_size,hashes,flush=True)
run("preflight",["ssh",*OPTS,HOST,
    "test ! -e /opt/blastlab/backups/20261107-phase26-hygiene && systemctl is-active --quiet blastlab-control-api.service && test -f /var/www/blastlab/og-card.png && echo READY"])
run("transfer",["scp",*OPTS,str(ARCHIVE),str(INSTALL),HOST+":/tmp/"])
run("install_and_health",["ssh",*OPTS,HOST,
    "bash /tmp/phase26-hygiene-install.lf.sh "+" ".join(hashes)])
print("PHASE26_HYGIENE_PUBLIC_DEPLOYMENT_VERIFIED",flush=True)
