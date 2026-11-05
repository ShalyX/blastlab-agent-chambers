from __future__ import annotations
import subprocess,re,sys
names=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()
tracked=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],text=True).splitlines()
patterns={
 'private-key-block':rb'-----BEGIN [A-Z ]*PRIVATE KEY',
 'github-token':rb'gh[oprsu]_[a-zA-Z0-9]{25,}',
 'github-pat':rb'github_pat_[a-zA-Z0-9_]{25,}',
 'api-key-shape':rb'sk-[a-zA-Z0-9_-]{30,}',
 'vultr-api-key-value':rb'VULTR_(?:API_KEY|INFERENCE_API_KEY)[ \t]*=[ \t]*[A-Za-z0-9_-]{15,}',
 'operator-token-value':rb'BLASTLAB_OPERATOR_TOKEN[ \t]*=[ \t]*[A-Za-z0-9_-]{20,}',
 'private-rsa-key':rb'-----BEGIN OPENSSH PRIVATE KEY',
}
found=[]
def inspect(names,rev):
 for p in names:
  if p == 'deploy/check_publication.py': continue  # The scanner embeds diagnostic regex signatures, not keys.
  if re.search(r'\.(?:png|jpg|jpeg|pptx|woff2?|svg|ico)$',p,re.I):continue
  if re.search(r'(^|/)(?:\.env(?:\.|$)|node_modules|artifacts|submission/audio)(/|$)',p):found.append((rev,p,'sensitive path'));continue
  try:
   raw=subprocess.check_output(['git','show',rev+':'+p],stderr=subprocess.DEVNULL,timeout=7)
  except Exception:
   continue
  for label,patt in patterns.items():
   if re.search(patt,raw):found.append((rev,p,label))
inspect(names,'')
inspect(tracked,'HEAD')
print('CHANGED_FILES',len(names),'BASELINE_FILES',len(tracked),'SENSITIVE_MATCHES',len(found))
for row in found[:35]:print('FLAG',*row)
sys.exit(1 if found else 0)
