import unittest

from deploy.phase_gate import ORDER, check_transition


class PhaseGateTests(unittest.TestCase):
    def state(self, name="PRODUCT_LOCK"):
        return {"phase": name}

    def ledger(self, name="PRODUCT_LOCK"):
        return {
            "exit_proofs": {name: {"status": "OPEN", "proof": ["PRODUCT.md"]}},
            "locked_p0": {},
            "judge_simulation_v3": "NOT_RUN",
        }

    def test_cannot_skip_phase(self):
        with self.assertRaisesRegex(ValueError, "PHASE_SKIP_DENIED"):
            check_transition(self.state(), self.ledger(), "TECHNICAL_DERISK")

    def test_cannot_pass_current_phase_without_exit_proof(self):
        with self.assertRaisesRegex(ValueError, "UNMET_GATE"):
            check_transition(self.state(), self.ledger(), "NAME_LOCK")

    def test_validation_modify_can_proceed_when_thesis_is_unchanged_and_modifications_are_recorded(self):
        ledger = self.ledger("VALIDATION")
        ledger["exit_proofs"]["VALIDATION"] = {
            "status": "MODIFY",
            "proof": ["VALIDATION.md"],
            "thesis_unchanged": True,
            "modifications_recorded": True,
        }
        self.assertEqual(
            check_transition(self.state("VALIDATION"), ledger, "PRODUCT_LOCK"),
            "PRODUCT_LOCK",
        )

    def test_validation_modify_without_thesis_unchanged_is_blocked(self):
        ledger = self.ledger("VALIDATION")
        ledger["exit_proofs"]["VALIDATION"] = {
            "status": "MODIFY",
            "proof": ["VALIDATION.md"],
            "thesis_unchanged": False,
            "modifications_recorded": True,
        }
        with self.assertRaisesRegex(ValueError, "UNMET_GATE"):
            check_transition(self.state("VALIDATION"), ledger, "PRODUCT_LOCK")

    def test_validation_modify_without_recorded_modifications_is_blocked(self):
        ledger = self.ledger("VALIDATION")
        ledger["exit_proofs"]["VALIDATION"] = {
            "status": "MODIFY",
            "proof": ["VALIDATION.md"],
            "thesis_unchanged": True,
            "modifications_recorded": False,
        }
        with self.assertRaisesRegex(ValueError, "UNMET_GATE"):
            check_transition(self.state("VALIDATION"), ledger, "PRODUCT_LOCK")

    def test_modify_cannot_bypass_a_non_validation_phase(self):
        ledger = self.ledger("PRODUCT_LOCK")
        ledger["exit_proofs"]["PRODUCT_LOCK"]["status"] = "MODIFY"
        ledger["exit_proofs"]["PRODUCT_LOCK"]["thesis_unchanged"] = True
        ledger["exit_proofs"]["PRODUCT_LOCK"]["modifications_recorded"] = True
        with self.assertRaisesRegex(ValueError, "UNMET_GATE"):
            check_transition(self.state("PRODUCT_LOCK"), ledger, "NAME_LOCK")

    def test_no_p0_means_no_proof_engine(self):
        ledger = self.ledger("BUILD_LOOP")
        ledger["exit_proofs"]["BUILD_LOOP"]["status"] = "PASS"
        with self.assertRaisesRegex(ValueError, "FULL_PRODUCT_BLOCKED"):
            check_transition(self.state("BUILD_LOOP"), ledger, "PROOF_ENGINE")

    def test_all_p0_pass_allows_normal_adjacent_move(self):
        ledger = self.ledger("BUILD_LOOP")
        ledger["exit_proofs"]["BUILD_LOOP"]["status"] = "PASS"
        ledger["locked_p0"] = {
            "P0-" + str(i).zfill(2): "VERIFIED" for i in range(1, 13)
        }
        self.assertEqual(
            check_transition(self.state("BUILD_LOOP"), ledger, "PROOF_ENGINE"),
            "PROOF_ENGINE",
        )

    def test_submission_requires_post_rebuild_judge_pass(self):
        ledger = self.ledger("FEATURE_FREEZE")
        ledger["exit_proofs"]["FEATURE_FREEZE"]["status"] = "PASS"
        ledger["locked_p0"] = {
            "P0-" + str(i).zfill(2): "VERIFIED" for i in range(1, 13)
        }
        with self.assertRaisesRegex(ValueError, "JUDGE_SIMULATION_NOT_PASSED"):
            check_transition(self.state("FEATURE_FREEZE"), ledger, "SUBMISSION_AUDIT")

    def test_stage_order_exact(self):
        self.assertEqual(ORDER[ORDER.index("VALIDATION") + 1], "PRODUCT_LOCK")
        self.assertEqual(ORDER[ORDER.index("PRODUCT_LOCK") + 1], "NAME_LOCK")
        self.assertLess(ORDER.index("PRODUCT_REVIEW"), ORDER.index("PRODUCT_HYGIENE"))
        self.assertLess(ORDER.index("JUDGE_SIMULATION"), ORDER.index("SUBMISSION_AUDIT"))


if __name__ == "__main__":
    unittest.main()
