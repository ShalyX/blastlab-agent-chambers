"""Phase24: outcome integrity, tamper resistance and sanitized release contract."""
import copy
import json
import unittest
from pathlib import Path

from agent_lab import verify_report,verify_import
from deploy.phase24_compile_proof import ROOT, RAW, OUT, compile_proof, read

class ProofEngineTests(unittest.TestCase):
    def setUp(self):
        from deploy.phase24_compile_proof import RAW
        missing=[name for name in RAW.values() if not (ROOT/name).is_file()]
        if missing:
            self.skipTest("Private raw proof reports absent in this checkout; run on authorized evidence host")
        self.proof=compile_proof()

    def test_all_four_lanes_verified_against_source(self):
        c=self.proof["claims"]
        self.assertEqual(set(c),{"same_agent","termproof","contained","framework"})
        self.assertEqual({k:v["metric"] for k,v in c.items()},
          {"same_agent":"3 to 0","termproof":"0 to 6","contained":"22 / 22","framework":"0 to 0"})
        self.assertTrue(c["same_agent"]["evidence"]["exact_plan_replay"])
        self.assertTrue(c["termproof"]["evidence"]["exact_plan_replay"])
        self.assertTrue(c["framework"]["evidence"]["exact_plan_replay"])
        self.assertEqual(c["contained"]["evidence"]["boundary_checks_passed"],22)

    def test_report_integrity_detects_changed_verdict(self):
        r=read(RAW["same_before"])
        self.assertTrue(verify_report(r))
        r["results"][1]["verdict"]="NO_RULE_VIOLATION_OBSERVED"
        self.assertFalse(verify_report(r))

    def test_report_integrity_detects_changed_action_or_answer(self):
        r=read(RAW["term_after"])
        self.assertTrue(verify_report(r))
        r["results"][0]["agent_answer"]="invented"
        self.assertFalse(verify_report(r))
        r=read(RAW["term_after"])
        r["evidence"]["events"][0]["sha256"]="0"*64
        self.assertFalse(verify_report(r))

    def test_exact_plan_comparison_rejects_tampering(self):
        a=read(RAW["same_before"])
        b=read(RAW["same_after"])
        self.assertTrue(verify_import({"report":a,"current":b})["verified"])
        bad=copy.deepcopy(b)
        bad["attack_plan_sha256"]="0"*64
        with self.assertRaises(ValueError):
            verify_import({"report":a,"current":bad})

    def test_source_identity_is_never_upgraded(self):
        c=self.proof["claims"]
        self.assertEqual(c["same_agent"]["ownership"],"PROJECT_OWNED")
        self.assertEqual(c["termproof"]["ownership"],"FOUNDER_OPERATED_PREEXISTING_CODEBASE")
        self.assertEqual(c["framework"]["ownership"],"PROJECT_OPERATED_PYDANTICAI")
        self.assertNotIn("customer-verified",self.proof["source_contract"])
        self.assertTrue(any("not obtained" in d for d in self.proof["proof_debts"]))
        for k in ["same_agent","termproof","framework"]:
            self.assertEqual(c[k]["evidence"]["before"]["source_type"],"EXTERNAL_AGENT_RUNNER_REPORTED")

    def test_public_json_matches_private_verified_evidence_without_secrets(self):
        public=json.loads(OUT.read_text(encoding="utf8"))
        self.assertEqual(public["schema"],"blastlab.phase24.proof-index.v1")
        self.assertEqual(public["claims"]["same_agent"]["metric"],"3 to 0")
        self.assertEqual(public["claims"]["termproof"]["metric"],"0 to 6")
        self.assertEqual(public["regression"]["executed"],240)
        blob=OUT.read_text(encoding="utf8").lower()
        for secret in ["recovery_key","join_token","api_key","password=",
                        "private_key","-----begin","token="]:
            self.assertNotIn(secret,blob)
        self.assertNotIn("untrusted_input",blob)
        self.assertNotIn("agent_answer",blob)
        self.assertNotIn("canary",blob)
        self.assertNotIn("raw tool arguments",blob)

    def test_contained_archive_is_not_confused_with_fresh_public_worker(self):
        c=self.proof["claims"]["contained"]["evidence"]
        self.assertEqual(c["forbidden_actions_denied"],7)
        self.assertEqual(c["actions_executed"],12)
        self.assertEqual(c["model_calls"],12)
        self.assertTrue(c["container_and_socket_removed"])
        self.assertIn("November 6",c["limitation"])

if __name__=="__main__":unittest.main()
