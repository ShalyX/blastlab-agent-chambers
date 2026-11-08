"""Security and API contract tests for the owner-only BlastLab gateway."""
import http.client
import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import control_api as gateway


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)
        token=root/'owner.token'
        token.write_text('synthetic-test-token-with-more-than-25-chars',encoding='utf-8')
        data=root/'data'
        data.mkdir()
        (data/'live.json').write_text(json.dumps({'id':'live','proof':{'hash_chain_valid':True}}),encoding='utf-8')
        self.patches=[
            patch.object(gateway,'TOKEN_FILE',token),
            patch.object(gateway,'DATA_DIR',data),
            patch.object(gateway,'ALLOWED_ORIGIN','https://blastlab.example'),
            patch.object(gateway,'RUNS_DIR',root/'runs')
        ]
        for p in self.patches:
            p.start();self.addCleanup(p.stop)
        with gateway.JOB_LOCK:
            gateway.JOBS.clear()
            gateway.LAST_STARTED.clear()
            gateway.ACTIVE_JOB=None
        self.server=ThreadingHTTPServer(('127.0.0.1',0),gateway.Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        # Ensure the Windows HTTP listener thread actually exits before
        # closing/reusing its ephemeral port in the 200+ test regression.
        # LIFO cleanup: shutdown, join, then close.
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.thread.join, 4)
        self.addCleanup(self.server.shutdown)

    def request(self,method,path,body=None,headers=None):
        payload=json.dumps(body).encode() if body is not None else None
        hs={'Content-Type':'application/json'}
        hs.update(headers or {})
        # Windows occasionally aborts a brand-new ephemeral loopback connection
        # (WinError 10053) while a large suite creates/destroys HTTP fixtures.
        # Retry only on this client transport error, not for HTTP failures, and
        # keep all assertions on the actual server response.
        for attempt in range(2 if sys.platform == 'win32' else 1):
            conn=http.client.HTTPConnection('127.0.0.1',self.server.server_address[1],timeout=8)
            try:
                conn.request(method,path,body=payload,headers=hs)
                resp=conn.getresponse()
                raw=resp.read()
                return (resp.status,json.loads(raw))
            except ConnectionAbortedError as exc:
                if sys.platform != 'win32' or getattr(exc,'winerror',None)!=10053 or attempt:
                    raise
                print('TEST_ONLY_WINDOWS_LOOPBACK_RETRY',method,path,flush=True)
            finally:
                conn.close()
        raise AssertionError('Unreachable retry path')

    def auth(self):
        return {'Authorization':'Bearer synthetic-test-token-with-more-than-25-chars','Origin':'https://blastlab.example'}

    def test_public_health(self):
        status,body=self.request('GET','/api/health')
        self.assertEqual(status,200)
        self.assertIn('owner live',body['execution_mode'])

    def test_public_safe_proof(self):
        status,body=self.request('GET','/api/runs/live')
        self.assertEqual(status,200)
        self.assertEqual(body['id'],'live')
        status,body=self.request('GET','/api/runs/missing')
        self.assertEqual(status,404)

    def test_owner_token_required(self):
        status,body=self.request('POST','/api/runs',{'mode':'scripted'})
        self.assertEqual(status,401)
        self.assertIn('token required',body['error'].lower())
        status,_=self.request('GET','/api/jobs/nothing')
        self.assertEqual(status,401)

    def test_origin_enforced(self):
        headers=self.auth();headers['Origin']='https://evil.example'
        status,_=self.request('POST','/api/runs',{'mode':'live'},headers)
        self.assertEqual(status,403)

    def test_arbitrary_commands_and_urls_rejected(self):
        for body in ({'mode':'scripted','path':'https://evil.example'},
                     {'mode':'live','prompt':'delete host files'},
                     {'mode':'shell'}, {'mode':'live','args':[]},
                     {'mode':'scripted','environment':{'KEY':'bad'}}):
            status,_=self.request('POST','/api/runs',body,self.auth())
            self.assertEqual(status,400,body)

    def test_fixed_run_is_queued_and_poll_is_protected(self):
        with patch.object(gateway,'run_task', lambda *_: None):
            status,body=self.request('POST','/api/runs',{'mode':'scripted'},self.auth())
        self.assertEqual(status,202)
        self.assertRegex(body['job_id'],r'^[0-9a-f]{32}$')
        status,job=self.request('GET','/api/jobs/'+body['job_id'],headers=self.auth())
        self.assertEqual(status,200)
        self.assertEqual(job['mode'],'scripted')
        self.assertEqual(job['status'],'queued')
        status,_=self.request('GET','/api/jobs/'+body['job_id'])
        self.assertEqual(status,401)
        status,_=self.request('POST','/api/runs',{'mode':'live'},self.auth())
        self.assertEqual(status,409)

    def test_unknown_paths_rejected(self):
        status,_=self.request('GET','/api/env')
        self.assertEqual(status,404)
        status,_=self.request('POST','/api/execute_shell',{},self.auth())
        self.assertEqual(status,404)

    def test_malformed_input_rejected(self):
        status,_=self.request('POST','/api/runs',None,self.auth())
        self.assertEqual(status,413)


if __name__=='__main__':
    unittest.main()
