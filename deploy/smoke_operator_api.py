"""Exercise the deployed fixed-scenario owner API from inside the Vultr VM.

Reads the operator token only on the server. Prints proof status, never secrets.
"""
import argparse
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE='http://127.0.0.1:8123'
ORIGIN='https://blastlab.45-77-138-147.sslip.io'

def request(method,path,token,body=None):
    headers={'Authorization':'Bearer '+token,'Origin':ORIGIN,'Content-Type':'application/json'}
    data=json.dumps(body).encode() if body is not None else None
    req=Request(BASE+path,data=data,headers=headers,method=method)
    with urlopen(req,timeout=20) as response:
        return response.status,json.load(response)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['live','scripted'],required=True)
    args=parser.parse_args()
    token=Path('/etc/blastlab/operator.token').read_text(encoding='utf-8').strip()
    if len(token)<25: raise SystemExit('Operator key unavailable')
    status,payload=request('POST','/api/runs',token,{'mode':args.mode})
    assert status==202 and payload.get('job_id'),(status,payload)
    id=payload['job_id']
    print(json.dumps({'mode':args.mode,'request_http':status,'job_id':id}),flush=True)
    last=''
    for attempt in range(110):
        time.sleep(2)
        code,body=request('GET','/api/jobs/'+id,token)
        state=body.get('status')
        if state!=last:
            print(json.dumps({'poll':attempt+1,'http':code,'status':state,'error':body.get('error')}),flush=True)
            last=state
        if state=='complete':
            proof_code,run=request('GET','/api/runs/'+args.mode,token)
            passed=proof_code==200 and run['summary']['acceptance_passed'] and run['proof']['hash_chain_valid'] and run['summary']['value_cents']==7200 and run['summary']['reset_verified']
            if args.mode=='live':passed=passed and run['is_model_driven'] and run['summary']['model_calls']>=1
            else:passed=passed and run['is_scripted'] and run['summary']['denied_actions']>=4
            print(json.dumps({'done':passed,'mode':args.mode,'source':run['origin'],'trace_sha256':run['proof']['trace_sha256'],'denials':run['summary']['denied_actions'],'generation_count':run['summary']['worker_generations']}),flush=True)
            raise SystemExit(0 if passed else 2)
        if state=='failed':
            print(json.dumps({'done':False,'failure':body.get('error')}),flush=True)
            raise SystemExit(3)
    raise SystemExit('TIMEOUT')

if __name__=='__main__':main()
