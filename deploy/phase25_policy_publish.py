"""Deploy surgical Phase25 validation fix; preserve all other live VM source."""
from pathlib import Path
import subprocess
import time
ROOT=Path(__file__).resolve().parents[1]
KEY=Path.home()/".ssh"/"blastlab_vultr_2026"
SRC=ROOT/"deploy/phase25_policy_install.sh"
COPY=ROOT/"artifacts/phase25-policy-install.lf.sh"
HOST="root@45.77.138.147"
SHA_ORIGINAL="363a688bd963e7c6330abc1e6ebad670d1b760cb465d48725a6a3d2f59e680d3"
OPTS=["-i",str(KEY),"-o","BatchMode=yes","-o","IdentitiesOnly=yes",
      "-o","ConnectTimeout=12","-o","ConnectionAttempts=1",
      "-o","StrictHostKeyChecking=accept-new"]
def cmd(stage,args,retries=1):
    for i in range(retries):
        print("PHASE25_RELEASE",stage,"ATTEMPT",i+1,flush=True)
        try:p=subprocess.run(args,capture_output=True,text=True,timeout=75,cwd=ROOT)
        except subprocess.TimeoutExpired:
            if i==retries-1:raise RuntimeError(stage+" timed out")
        else:
            if p.returncode==0:
                print("PHASE25_RELEASE_PASS",stage,p.stdout.strip()[-350:],flush=True)
                return
            print("PHASE25_RELEASE_FAIL",stage,p.returncode,p.stderr[-250:],flush=True)
            if i==retries-1:raise RuntimeError(stage+" returned nonzero; verify server state")
        time.sleep(3*(i+1))
assert KEY.is_file() and SRC.is_file()
COPY.parent.mkdir(parents=True,exist_ok=True)
COPY.write_bytes(SRC.read_bytes().replace(b"\r\n",b"\n"))
assert b"\r" not in COPY.read_bytes()
cmd("preflight",["ssh",*OPTS,HOST,
   "test \"$(sha256sum /opt/blastlab/agent_lab.py | cut -d' ' -f1)\" = \""+SHA_ORIGINAL+"\" && systemctl is-active --quiet blastlab-control-api.service && echo READY"],2)
cmd("stage",["scp",*OPTS,str(COPY),HOST+":/tmp/phase25-policy-install.lf.sh"],2)
cmd("install",["ssh",*OPTS,HOST,"bash /tmp/phase25-policy-install.lf.sh "+SHA_ORIGINAL])
print("PHASE25_POLICY_PRODUCTION_PASS",flush=True)
