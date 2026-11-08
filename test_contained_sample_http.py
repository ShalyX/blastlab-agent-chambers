"""HTTP gate proof for fixed sample - no custom code and no Origin bypass."""
import tempfile
from pathlib import Path
from unittest.mock import patch

import contained_sample_service as sample
from test_control_api import GatewayTests


class FixedSampleHttpTests(GatewayTests):
    def setUp(self):
        super().setUp()
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        p=patch.object(sample,"STORE",Path(tmp.name))
        p.start()
        self.addCleanup(p.stop)

    def test_fixed_sample_http_origin_auth_and_daily_quota(self):
        with patch.object(sample,"_execute",return_value=None):
            request={"mode":"fixed-project-sample"}
            code,_=self.request("POST","/api/contained-sample/jobs",request)
            self.assertEqual(code,403)
            code,_=self.request("POST","/api/contained-sample/jobs",request,
                                {"Origin":"https://attacker.example"})
            self.assertEqual(code,403)
            code,_=self.request("POST","/api/contained-sample/jobs",
                                {**request,"url":"https://evil.example"},
                                {"Origin":"https://blastlab.example"})
            self.assertEqual(code,400)
            self.assertEqual(sample._usage(False),0)
            code,job=self.request("POST","/api/contained-sample/jobs",
                                  request,{"Origin":"https://blastlab.example"})
            self.assertEqual(code,202,job)
            self.assertEqual(len(job["job_id"]),32)
            code,status=self.request("GET",job["poll_url"])
            self.assertEqual(code,200,status)
            self.assertEqual(status["status"],"queued")
            code,latest=self.request("GET","/api/contained-sample/latest")
            self.assertEqual(code,200,latest)
            self.assertEqual(latest["job_id"],job["job_id"])
            code,_=self.request("POST","/api/contained-sample/jobs",
                                request,{"Origin":"https://blastlab.example"})
            self.assertEqual(code,429)
            code,_=self.request("GET","/api/contained-sample/jobs/not-a-valid-id")
            self.assertEqual(code,404)

    def test_owner_quota_separate_and_not_body_claimable(self):
        with patch.object(sample,"_execute",return_value=None):
            code,job=self.request("POST","/api/contained-sample/jobs",
                {"mode":"fixed-project-sample","owner":True},
                {"Origin":"https://blastlab.example"})
            self.assertEqual(code,400)
            code,job=self.request("POST","/api/contained-sample/jobs",
                {"mode":"fixed-project-sample"},self.auth())
            self.assertEqual(code,202)
            self.assertEqual(sample._usage(True),1)
            self.assertEqual(sample._usage(False),0)
