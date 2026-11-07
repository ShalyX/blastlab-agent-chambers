"""Deploy a bounded fixed-worker API + visual control, without modifying customer sessions.

No side effect is retried automatically after a disconnect. VM has an archive backup.
Unix LF unit and installer are created explicitly, avoiding Windows CRLF issues.
"""
from __future__ import annotations
import hashlib
import subprocess
import tarfile
import time
from io import BytesIO
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
KEY=Path.home()/'.ssh'/'blastlab_vultr_2026'
HOST='root@45.77.138.147'
OUT=ROOT/'artifacts/phase23-fresh-sample.tar.gz'
INSTALL=ROOT/'artifacts/phase23-fresh-sample-install.lf.sh'
OPTS=['-i',str(KEY),'-o','BatchMode=yes','-o','IdentitiesOnly=yes',
      '-o','ConnectTimeout=14','-o','ConnectionAttempts=1',
      '-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','-o','StrictHostKeyChecking=accept-new']

def task(name,args,retries=1):
    for n in range(1,retries+1):
        print('STAGE',name,'ATTEMPT',n,flush=True)
        try:
            p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=65)
        except subprocess.TimeoutExpired:
            print('TIMEOUT',name,flush=True)
            if n==retries:raise
        else:
            if p.returncode==0:
                print('PASS',name,p.stdout.strip()[-400:],flush=True)
                return
            print('FAILED',name,'EXIT',p.returncode,'STDOUT',p.stdout[-280:],'STDERR',p.stderr[-300:],flush=True)
            if n==retries:raise RuntimeError(name+' failed; verify remote state before retrying')
        time.sleep(3*n)

def write_from_bytes(tar,name,body,mode=0o644):
    info=tarfile.TarInfo(name)
    info.size=len(body)
    info.mode=mode
    tar.addfile(info,BytesIO(body))

assert KEY.is_file()
files={
  'backend/control_api.py':ROOT/'control_api.py',
  'backend/contained_sample_service.py':ROOT/'contained_sample_service.py',
  'backend/experiments/byoa-containment/host_supervisor.py':ROOT/'experiments/byoa-containment/host_supervisor.py',
  'backend/experiments/byoa-containment/verify_run.py':ROOT/'experiments/byoa-containment/verify_run.py',
  'systemd/blastlab-control-api.service':ROOT/'deploy/blastlab-control-api.service',
  'web/index.html':ROOT/'web/dist/index.html',
  'web/connect/independent-tester.md':ROOT/'web/public/connect/independent-tester.md'
}
for f in (ROOT/'web/dist/assets').iterdir():
    if f.is_file():files['web/assets/'+f.name]=f
assert len(files)>=8 and all(p.is_file() for p in files.values())
with tarfile.open(OUT,'w:gz') as tar:
    for name,p in files.items():
        body=p.read_bytes()
        if name.startswith('systemd/'):body=body.replace(b'\r\n',b'\n')
        write_from_bytes(tar,name,body)
u=ROOT/'deploy/phase23_fresh_sample_install.sh'
INSTALL.write_bytes(u.read_bytes().replace(b'\r\n',b'\n'))
assert b'\r' not in INSTALL.read_bytes()
indexsha=hashlib.sha256(files['web/index.html'].read_bytes()).hexdigest()
archivesha=hashlib.sha256(OUT.read_bytes()).hexdigest()
print('BUNDLE_READY','bytes',OUT.stat().st_size,'index',indexsha,'archive',archivesha,flush=True)
task('readonly-preflight',['ssh',*OPTS,HOST,
     'test -f /opt/blastlab/control_api.py && test ! -e /opt/blastlab/backups/20261107-phase23-fresh-sample && systemctl is-active --quiet blastlab-control-api.service && echo READY'],3)
task('stage-release',['scp',*OPTS,str(OUT),str(INSTALL),HOST+':/tmp/'],3)
# shell staged as /tmp/phase23-fresh-sample-install.lf.sh
task('install-and-verify',['ssh',*OPTS,HOST,
      'bash /tmp/phase23-fresh-sample-install.lf.sh '+indexsha+' '+archivesha],1)
print('PHASE23_FRESH_SAMPLE_DEPLOYED',flush=True)
