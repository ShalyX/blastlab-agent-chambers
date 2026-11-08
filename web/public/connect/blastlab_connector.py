"""BlastLab external agent connector: developer runs this on their own machine.
Adapter signature: run(case: dict) -> {"answer": str, "tool_calls": [{"name": str, "arguments": dict}]}
The connector reports proposed actions. Never run real destructive tools inside an evaluation adapter.
"""
import argparse, importlib, json, os, sys
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlsplit

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args):
        raise RuntimeError("Redirects are prohibited")

def get_or_post(base,path,token,body=None):
    data=json.dumps(body).encode("utf-8") if body is not None else None
    headers={"Authorization":"Bearer "+token}
    if body is not None:headers["Content-Type"]="application/json"
    req=Request(base+path,data=data,headers=headers,method="POST" if data else "GET")
    try:
        with build_opener(NoRedirect()).open(req,timeout=25) as result:
            raw=result.read(64001)
            if len(raw)>64000:raise ValueError("Server response too large")
            return json.loads(raw)
    except HTTPError as exc:
        code=exc.code;exc.close()
        raise RuntimeError("BlastLab server rejected request ("+str(code)+")") from None

def run(base,session,adapter,token):
    url=urlsplit(base)
    if url.scheme!="https" and not(url.scheme=="http" and url.hostname in ("localhost","127.0.0.1")):
        raise ValueError("HTTPS BlastLab URL required")
    if len(token)<24:raise ValueError("Set BLASTLAB_SESSION_TOKEN environment variable")
    if ":" not in adapter:raise ValueError("Adapter must be module:function")
    module,func=adapter.rsplit(":",1)
    if not all(part.isidentifier() for part in module.split(".")) or not func.isidentifier():
        raise ValueError("Invalid adapter identifier")
    # User adapters live in the developer's working directory, not beside this downloaded connector.
    sys.path.insert(0,os.getcwd())
    handler=getattr(importlib.import_module(module),func)
    if not callable(handler):raise ValueError("Adapter must be callable")
    root="/api/agent-lab/sessions/"+session
    base=base.rstrip("/")
    for count in range(6):
        item=get_or_post(base,root+"/next",token)
        if item.get("complete"):break
        case=item["case"]
        answer=handler(case)
        if not isinstance(answer,dict):raise TypeError("Agent callback must return dict")
        result={
            "case_id":case["case_id"],
            "answer":answer.get("answer",""),
            "tool_calls":answer.get("tool_calls",[]),
        }
        accepted=get_or_post(base,root+"/response",token,result)
        print("CASE",case["case_id"],accepted["observed_verdict"],
              str(accepted["completed"])+"/"+str(accepted["total"]),flush=True)
    finished=get_or_post(base,root+"/report",token)
    print(json.dumps({"status":finished["status"],"completed":finished["tests_completed"],
                      "breaches":finished["breached"],"source":finished["source_type"]},indent=2))
    return finished

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--session",required=True)
    parser.add_argument("--adapter",required=True,help="user_agent_module:function")
    parser.add_argument("--base",default="https://blastlab.45-77-138-147.sslip.io")
    opts=parser.parse_args()
    try:run(opts.base,opts.session,opts.adapter,os.environ.get("BLASTLAB_SESSION_TOKEN",""))
    except Exception as exc:
        print("CONNECTOR_ERROR:",type(exc).__name__,str(exc),file=sys.stderr)
        sys.exit(2)
