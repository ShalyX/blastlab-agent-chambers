"""Publish UI-only clarity fixes; preserve live contained worker backend and evidence."""
import hashlib,subprocess,tarfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
KEY=Path.home()/'.ssh'/'blastlab_vultr_2026'
HOST='root@45.77.138.147'
DIST=ROOT/'web/dist'
ARCHIVE=ROOT/'artifacts/phase23-fresh-ui-polish.tar.gz'
INSTALL=ROOT/'artifacts/phase23_fresh_ui_polish_install.lf.sh'
OPTS=['-i',str(KEY),'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','ConnectTimeout=12','-o','ConnectionAttempts=1','-o','StrictHostKeyChecking=accept-new']
def run(name,cmd,retries=1):
 for i in range(1,retries+1):
  print('STEP',name,'ATTEMPT',i,flush=True)
  try:p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=65)
  except subprocess.TimeoutExpired:
   if i==retries:raise
  else:
   if p.returncode==0:
    print('STEP_PASS',name,p.stdout.strip()[-350:],flush=True)
    return
   print('STEP_FAIL',name,p.returncode,p.stderr[-350:],flush=True)
   if i==retries:raise RuntimeError(name+' failed; inspect live host before retrying')
  time.sleep(i*3)
assert KEY.is_file()
index=DIST/'index.html'
assets=list((DIST/'assets').iterdir())
assert index.is_file() and assets and all(x.is_file() for x in assets)
with tarfile.open(ARCHIVE,'w:gz') as tf:
 tf.add(index,arcname='index.html')
 for f in assets:tf.add(f,arcname='assets/'+f.name)
INSTALL.write_bytes((ROOT/'deploy/phase23_fresh_ui_polish_install.sh').read_bytes().replace(b'\r\n',b'\n'))
assert b'\r' not in INSTALL.read_bytes()
sha=hashlib.sha256(index.read_bytes()).hexdigest()
print('UI_ONLY_BUNDLE',ARCHIVE.stat().st_size,'bytes',sha,flush=True)
run('preflight',['ssh',*OPTS,HOST,"test ! -e /opt/blastlab/backups/20261107-phase23-fresh-ui-polish && test -f /var/www/blastlab/index.html && echo READY"],3)
run('stage',['scp',*OPTS,str(ARCHIVE),str(INSTALL),HOST+':/tmp/'],3)
run('install',['ssh',*OPTS,HOST,'bash /tmp/phase23_fresh_ui_polish_install.lf.sh '+sha])
print('PRODUCTION_UI_CLARITY_VERIFIED',flush=True)
