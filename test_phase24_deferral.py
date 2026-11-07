"""Test the very narrow owner-directed Proof Engine defer/RED_TEAM transition."""
import copy
import unittest
from deploy.phase_gate import check_transition

class Phase24DeferralTests(unittest.TestCase):
    def ledger(self):
        return {
            "exit_proofs":{
                "PROOF_ENGINE":{
                  "status":"CONDITIONAL_DEFERRED",
                  "owner_approved":True,
                  "deferred_proof_id":"independent_outside_operator",
                  "completion_requirement":"before_submission_audit",
                  "proof":["PHASE24_OWNER_DEFERRAL.md"],
                },
                "FEATURE_FREEZE":{"status":"PASS","proof":["PHASE24_OWNER_DEFERRAL.md"]},
            },
            "locked_p0":{"P0-"+str(i).zfill(2):"VERIFIED" for i in range(1,13)},
            "deferred_requirements":{"independent_outside_operator":{"status":"OPEN","proof":[]}},
            "judge_simulation_v3":"PASS",
        }

    def test_explicit_owner_approved_adjacent_transition(self):
        self.assertEqual(check_transition({"phase":"PROOF_ENGINE"},self.ledger(),"RED_TEAM"),"RED_TEAM")

    def test_no_owner_approval_is_blocked(self):
        l=self.ledger()
        l["exit_proofs"]["PROOF_ENGINE"]["owner_approved"]=False
        with self.assertRaisesRegex(ValueError,"UNMET_GATE"):
            check_transition({"phase":"PROOF_ENGINE"},l,"RED_TEAM")

    def test_wrong_proof_id_is_blocked(self):
        l=self.ledger()
        l["exit_proofs"]["PROOF_ENGINE"]["deferred_proof_id"]="other"
        with self.assertRaisesRegex(ValueError,"UNMET_GATE"):
            check_transition({"phase":"PROOF_ENGINE"},l,"RED_TEAM")

    def test_no_recorded_open_debt_is_blocked(self):
        l=self.ledger()
        del l["deferred_requirements"]["independent_outside_operator"]
        with self.assertRaisesRegex(ValueError,"UNMET_GATE"):
            check_transition({"phase":"PROOF_ENGINE"},l,"RED_TEAM")

    def test_must_be_adjacent_red_team_not_any_later_phase(self):
        with self.assertRaisesRegex(ValueError,"PHASE_SKIP_DENIED"):
            check_transition({"phase":"PROOF_ENGINE"},self.ledger(),"PRODUCT_HYGIENE")

    def test_cannot_use_conditional_deferral_on_other_phase(self):
        l=self.ledger()
        l["exit_proofs"]["RED_TEAM"]=copy.deepcopy(l["exit_proofs"]["PROOF_ENGINE"])
        with self.assertRaisesRegex(ValueError,"UNMET_GATE"):
            check_transition({"phase":"RED_TEAM"},l,"PRODUCT_HYGIENE")

    def test_deferred_external_proof_blocks_submission_even_if_other_gates_green(self):
        with self.assertRaisesRegex(ValueError,"DEFERRED_OUTSIDE_OPERATOR_PROOF_NOT_COMPLETE"):
            check_transition({"phase":"FEATURE_FREEZE"},self.ledger(),"SUBMISSION_AUDIT")

    def test_fabricated_verified_status_without_evidence_blocks_submission(self):
        l=self.ledger()
        l["deferred_requirements"]["independent_outside_operator"]["status"]="VERIFIED"
        with self.assertRaisesRegex(ValueError,"DEFERRED_OUTSIDE_OPERATOR_PROOF_NOT_COMPLETE"):
            check_transition({"phase":"FEATURE_FREEZE"},l,"SUBMISSION_AUDIT")

    def test_deferred_decision_document_cannot_be_reused_as_fake_outside_proof(self):
        l=self.ledger()
        deferred=l["deferred_requirements"]["independent_outside_operator"]
        deferred.update(status="VERIFIED",proof=["PHASE24_OWNER_DEFERRAL.md"],
            outside_operator_reference="synthetic-test",agent_source_reference="synthetic-repo",
            six_case_report_manifest_sha256="0"*64,consent_to_cite=True)
        with self.assertRaisesRegex(ValueError,"DEFERRED_OUTSIDE_OPERATOR_PROOF_NOT_COMPLETE"):
            check_transition({"phase":"FEATURE_FREEZE"},l,"SUBMISSION_AUDIT")

if __name__=="__main__":
    unittest.main()
