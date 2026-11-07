"""Red Team regression. Run real tests in independent Python processes on Windows."""
from pathlib import Path
import json,re,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"artifacts/phase25-redteam-regression"
OUT.mkdir(parents=True,exist_ok=True)
modules=sorted(p.stem for p in ROOT.glob("test_*.py"))
support={"test_support_agent_plan","test_support_retest_server"}
assert support.issubset(set(modules))
count=0;skipped=0;fail=[]
began=time.monotonic()
for index,name in enumerate(modules,1):
 if name in support:
  print("SUPPORT_ONLY",name,flush=True)
  continue
 try:
  p=subprocess.run([sys.executable,"-m","unittest","-q",name],cwd=ROOT,
    text=True,capture_output=True,timeout=120,encoding="utf8",errors="replace")
  output=p.stdout+"\n"+p.stderr
 except subprocess.TimeoutExpired:
  fail.append({"module":name,"error":"timeout"});print("FAIL",name,"timeout",flush=True);continue
 (OUT/(name+".log")).write_text(output,encoding="utf8")
 counts=re.findall(r"Ran (\d+) tests? in [\d.]+s",output)
 if p.returncode!=0 or not counts or int(counts[-1])<=0:
  fail.append({"module":name,"exit":p.returncode,"tail":output[-950:]})
  print("FAIL",name,"exit",p.returncode,flush=True)
  continue
 n=int(counts[-1]);count+=n
 sk=re.findall(r"OK \(skipped=(\d+)\)",output)
 skipped+=int(sk[-1]) if sk else 0
 print("PASS",f"{index}/{len(modules)}",name,"count",n,flush=True)
summary={"modules":len(modules)-len(support),"tests":count,"skipped":skipped,
 "failures":fail,"duration_seconds":round(time.monotonic()-began,2),
 "method":"Every test module executed in a separate process, no test assertions mocked or bypassed"}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf8")
print("PHASE25_FULL_REGRESSION",json.dumps(summary),flush=True)
raise SystemExit(0 if not fail else 2)
