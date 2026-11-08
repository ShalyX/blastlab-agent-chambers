"""Fixed contained sample: bounded quota, strict input, independently checked provenance."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import contained_sample_service as sample


class FixedSampleServiceTests(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        p=patch.object(sample,"STORE",Path(d.name))
        p.start();self.addCleanup(p.stop)
        p=patch.object(sample.threading,"Thread")
        self.thread=p.start();self.addCleanup(p.stop)

    def test_rejects_user_defined_code_and_model_and_urls(self):
        for payload in (None,{},{"mode":"arbitrary"},{"mode":"fixed-project-sample","url":"https://evil.test"},
                        {"mode":"fixed-project-sample","code":"print('hello')"},
                        {"mode":"fixed-project-sample","model":"other"},
                        {"mode":"fixed-project-sample","task":"arbitrary"}):
            with self.subTest(payload=payload):
                status,body=sample.start(requested=payload)
                self.assertEqual(status,400,body)
        self.assertEqual(sample._usage(False),0)

    def test_public_quota_and_durable_restart(self):
        first,body=sample.start(requested={"mode":"fixed-project-sample"})
        self.assertEqual(first,202,body)
        self.assertRegex(body["job_id"],r"^[0-9a-f]{32}$")
        self.assertNotIn("runner",body)
        self.assertEqual(sample.get(body["job_id"])[0],200)
        self.assertEqual(sample.latest()[1]["job_id"],body["job_id"])
        code,second=sample.start(requested={"mode":"fixed-project-sample"})
        self.assertEqual(code,429,second)
        self.assertEqual(sample._usage(False),1)
        self.assertTrue((sample.STORE/"latest.json").is_file())
        self.assertNotIn("Bearer",sample.path_for(body["job_id"]).read_text())
        import os
        if os.name=="posix":
            self.assertEqual(sample.path_for(body["job_id"]).stat().st_mode & 0o777,0o600)

    def test_separate_owner_allocation_cannot_override_active(self):
        status,body=sample.start(requested={"mode":"fixed-project-sample"})
        self.assertEqual(status,202)
        code,_=sample.start(requested={"mode":"fixed-project-sample"},owner=True)
        self.assertEqual(code,409)
        job=json.loads(sample.path_for(body["job_id"]).read_text())
        job["status"]="complete"
        job["summary"]={"cases_completed":6}
        sample.atomic_json(sample.path_for(body["job_id"]),job)
        self.assertEqual(sample.start(owner=True,requested={"mode":"fixed-project-sample"})[0],202)
        self.assertEqual(sample._usage(True),1)

    def test_safe_job_lookup_and_explicit_sample_mode(self):
        status,body=sample.start(requested={"mode":"fixed-project-sample"})
        self.assertEqual(status,202)
        self.assertEqual(sample.get("..")[0],404)
        self.assertEqual(sample.get("0"*32)[0],404)
        code,data=sample.get(body["job_id"])
        self.assertEqual(code,200)
        self.assertEqual(data["status"],"queued")
        self.assertEqual(data["available_public_runs_today"],0)
        self.assertNotIn("public",data)

    def test_signed_claim_not_inferred_and_provenance_limited(self):
        keys={"run_id":"abc","status":"PASS","report_manifest_sha256":"c"*64,"tests_completed":6,
              "inference_proxy_calls":12,"worker_actions_executed":12,"forbidden_actions_denied":7,
              "container_absent_after_teardown":True,"inference_socket_removed":True,
              "direct_network_egress_blocked":True,"timestamp":"2026-11-07T00:00:00+00:00"}
        report={"tests_completed":6,"breached":0,"manifest_sha256":"c"*64,"attack_plan_sha256":"d"*64,
                "results":[{"case_id":str(i),"family":"test","verdict":"NO_OBSERVED_VIOLATION"} for i in range(6)]}
        checks={"checks":{str(i):True for i in range(22)},"status":"PASS",
                "run_id":"abc","manifest_sha256":"c"*64}
        class Source:
            def __init__(self,name,value):self.name=name;self.value=value
            def read_text(self,encoding="utf8"):return json.dumps(self.value)
        from unittest.mock import MagicMock
        d=MagicMock()
        d.__truediv__.side_effect=lambda file:Source(file,{"summary.json":keys,
                    "report.json":report,"independent-verification.json":checks}[file])
        out=sample._capture_evidence(d)
        self.assertEqual(out["checks_passed"],22)
        self.assertEqual(out["origin"],"PROJECT_OWNED_HOST_OBSERVED_NOT_CUSTOMER")
        self.assertIn("not a customer",out["limitations"])
        self.assertEqual(out["cases_completed"],6)
        self.assertEqual(out["synthetic_actions_executed"],12)
        checks["checks"]["1"]=False
        with self.assertRaises(AssertionError):sample._capture_evidence(d)

if __name__=="__main__":unittest.main()
