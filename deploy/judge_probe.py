"""Independent judge technical scrutiny. Read-only public test.

Looks for missing proof relationships; it does not trigger billed inference or
new Docker jobs. Failing an assertion is a real judge-facing gap.
"""
import json, urllib.request, copy
import sys
sys.path.insert(0,str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from verify_public_evidence import verify
base='https://blastlab.45-77-138-147.sslip.io'
run_id='scripted-99bb851e7f39b5ba82'
def fetch(path):
  with urllib.request.urlopen(base+path,timeout=25) as r:
    return r.status,json.load(r)
for path in ['/api/health','/api/catalog','/api/history','/api/history/'+run_id,'/api/runs/live']:
  code,body=fetch(path)
  print('GET',path,'status',code,'type',type(body).__name__)
_,data=fetch('/api/history/'+run_id)
print('CASE',data['id'],'scenario',data.get('scenario'),'actor',data['report']['attempted_by_source'],'value',data['summary']['value_cents'],'denials',data['summary']['denied_actions'])
assert verify(data)['verified']
print('PUBLIC_CHAIN_VERIFIED',True,'event_count',len(data['events']))
variants={
  'tampered_event':lambda x:x['events'][3].update({'title':'FORGED AUDIT'}),
  'tampered_value':lambda x:x['summary'].update({'value_cents':99999999}),
  'tampered_verdict':lambda x:x['report'].update({'verdict':'COMPROMISE OBSERVED'}),
  'tampered_mission':lambda x:x.update({'mission_id':'inventory_value'}),
  'tampered_source_hash':lambda x:x['proof'].update({'trace_sha256':'0'*64}),
}
for name,change in variants.items():
   clone=copy.deepcopy(data);change(clone)
   try:verify(clone);accepted=True
   except (ValueError,KeyError):accepted=False
   print('TAMPER_TEST',name,'accepted',accepted)
