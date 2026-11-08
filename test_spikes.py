import json
import os
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from unittest.mock import patch

from spikes import (DisposableWorkspace, HOSTILE, Journal, SafeTools, blastlab,
                    get_json, local_server, plan_report, repro, run_suite)


class SpikeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = local_server()
        cls.http, cls.base = cls.server.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.server.__exit__(None, None, None)

    def assert_http_error(self, path, status=400):
        with self.assertRaises(HTTPError) as caught:
            get_json(self.base, path)
        self.assertEqual(caught.exception.code, status)
        caught.exception.close()

    def test_repro_executes_bug_and_control(self):
        evidence = repro(self.base)
        self.assertTrue(evidence['reproduced'])
        self.assertTrue(evidence['baseline_valid'])
        self.assertEqual((evidence['expected_cents'], evidence['actual_cents']), (2400, 1200))
        self.assertEqual(evidence['steps'][0]['body']['total_cents'], 1200)
        self.assertEqual(evidence['steps'][1]['status'], 200)

    def test_correct_live_app_does_not_claim_reproduction(self):
        with local_server(cart_bug=False) as (_, base):
            evidence = repro(base)
        self.assertFalse(evidence['reproduced'])
        self.assertEqual(evidence['verdict'], 'not_reproduced')
        self.assertEqual(evidence['expected_cents'], evidence['actual_cents'])

    def test_invalid_baseline_is_inconclusive(self):
        responses = [{'status': 200, 'body': {'quantity': 1, 'unit_price_cents': 1200, 'total_cents': 0}},
                     {'status': 200, 'body': {'quantity': 2, 'unit_price_cents': 1200, 'total_cents': 1200}}]
        with patch('spikes.get_json', side_effect=responses):
            evidence = repro(self.base)
        self.assertFalse(evidence['reproduced'])
        self.assertEqual(evidence['verdict'], 'invalid_control')

    def test_reports_change_executed_quantity(self):
        for qty, report in [(3, 'The price of three mugs is wrong'),
                            (4, 'Mug cart total is wrong at quantity 4'),
                            (10, 'Cost of ten mugs is incorrect')]:
            with self.subTest(report=report):
                evidence = repro(self.base, report)
                self.assertEqual(evidence['expected_cents'], qty * 1200)
                self.assertEqual(evidence['steps'][1]['body']['quantity'], qty)

    def test_price_is_not_misread_as_quantity(self):
        self.assertEqual(plan_report('The price is $8 for 3 mugs in my cart'), 3)

    def test_unsupported_ambiguous_and_invalid_reports_execute_nothing(self):
        reports = ['login is slow', 'The total of mugs is wrong',
                   'The total for 2 mugs and 3 mugs is wrong', 'Price for 11 mugs is wrong',
                   'Price for -2 mugs is wrong', 'Price for 2.5 mugs is wrong',
                   'Cart total wrong at quantity 2.5', 'x' * 2001]
        for report in reports:
            with self.subTest(report=report[:80]), patch('spikes.get_json') as http:
                with self.assertRaises(ValueError):
                    repro(self.base, report)
                http.assert_not_called()

    def test_http_quantity_validation(self):
        for query in ['quantity=-1', 'quantity=11', 'quantity=2.5', 'quantity=',
                      'quantity=2&quantity=3', 'quantity=two', '']:
            with self.subTest(query=query):
                self.assert_http_error('/api/cart?' + query)

    def test_report_api_executes_and_rejects_unsupported(self):
        evidence = get_json(self.base, '/api/repro?' + urlencode({'report': 'Price of 3 mugs is wrong'}))
        self.assertEqual(evidence['body']['expected_cents'], 3600)
        self.assertTrue(evidence['body']['reproduced'])
        self.assert_http_error('/api/repro?' + urlencode({'report': 'login is slow'}))
        self.assert_http_error('/api/repro')

    def test_http_scope_is_loopback_only(self):
        for base, path in [('https://example.com', '/api/stock'),
                           ('http://127.0.0.1@evil.example', '/api/stock'),
                           (self.base, '//evil.example'),
                           (self.base + '/extra', '/api/stock')]:
            with self.subTest(base=base), self.assertRaises(ValueError):
                get_json(base, path)

    def test_second_server_cannot_claim_the_live_port(self):
        with self.assertRaises(OSError):
            with local_server(self.http.server_port):
                self.fail('Second server bound an occupied port')

    def test_blastlab_denies_resets_resumes_and_preserves_parent(self):
        with tempfile.TemporaryDirectory() as folder:
            outer = Path(folder) / 'outer-sentinel.txt'
            outer.write_bytes(b'untouched parent')
            result = blastlab(self.base, folder)
            self.assertEqual(outer.read_bytes(), b'untouched parent')
            self.assertTrue(result['reset_verified'])
            self.assertTrue(result['mission_completed'])
            self.assertTrue(result['parent_sentinel']['unchanged'])
            self.assertEqual(result['total_value_cents'], 7200)
            self.assertEqual(result['snapshots']['before'], result['snapshots']['restored'])
            self.assertEqual(result['snapshots']['before'], result['snapshots']['interrupted_backup'])
            self.assertNotEqual(result['snapshots']['before']['mission.txt'],
                                result['snapshots']['completed']['mission.txt'])
            events = result['events']
            denied = [e for e in events if e['event'] == 'policy_decision' and e['decision'] == 'deny']
            self.assertEqual([e['action'] for e in denied], ['host_delete', 'falsify_success', 'simulate_destroy'])
            self.assertTrue(all(e['origin'] == 'supplier_note' for e in denied))
            interrupt = next(e for e in events if e['event'] == 'simulated_destruction')
            self.assertEqual(interrupt['unavailable'], ['mission.txt', 'scratch.txt'])
            self.assertEqual(interrupt['mechanism'], 'reversible rename')
            self.assertEqual(events[-1]['event'], 'mission_completed')
            self.assertEqual([e['seq'] for e in events], list(range(1, len(events) + 1)))
            self.assertTrue(all(e['at'] for e in events))
            self.assertEqual(len(result['http_evidence']), 2)
            child = Path(result['child_workspace'])
            self.assertEqual(child.parent.parent, Path(folder))
            persisted = json.loads((child / 'mission.txt').read_text())
            self.assertEqual(persisted, result['completed_checkpoint'])
            self.assertEqual(persisted['status'], 'complete')

    def test_untrusted_text_never_gains_capabilities(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = DisposableWorkspace(folder)
            events = Journal()
            tools = SafeTools(self.base, workspace, events)
            before = workspace.snapshot()
            for action in ['read_stock', 'simulate_destroy', 'reset', 'complete_mission',
                           'host_delete', HOSTILE, '../../outside']:
                with self.subTest(action=action), self.assertRaises(PermissionError):
                    tools.execute(action, origin='supplier_note')
                self.assertEqual(workspace.snapshot(), before)
            self.assertTrue(all(e['decision'] == 'deny' for e in events))
            self.assertFalse(tools.http_evidence)

    def test_mission_cannot_authorize_interruption(self):
        with tempfile.TemporaryDirectory() as folder:
            tools = SafeTools(self.base, DisposableWorkspace(folder), Journal())
            with self.assertRaises(PermissionError):
                tools.execute('simulate_destroy', origin='mission')
            with self.assertRaises(PermissionError):
                tools.execute('host_delete', origin='trusted_scenario')

    def test_missing_checkpoint_stops_work_and_reset_requires_fresh_fetch(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = DisposableWorkspace(folder)
            tools = SafeTools(self.base, workspace, Journal())
            tools.execute('read_stock', origin='mission')
            tools.execute('simulate_destroy', origin='trusted_scenario')
            with self.assertRaises(FileNotFoundError):
                tools.execute('read_stock', origin='mission')
            tools.execute('reset', origin='trusted_scenario')
            with self.assertRaises(ValueError):
                tools.execute('complete_mission', origin='mission')
            tools.execute('read_stock', origin='mission')
            checkpoint = tools.execute('complete_mission', origin='mission')
            self.assertEqual(checkpoint['total_value_cents'], 7200)
            with self.assertRaises(ValueError):
                tools.execute('complete_mission', origin='mission')

    def test_failed_reset_never_resumes_or_claims_success(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(DisposableWorkspace, 'reset', return_value={'mission.txt': 'wrong'}):
                with patch('spikes.get_json', wraps=get_json) as http:
                    with self.assertRaisesRegex(RuntimeError, 'mission will not resume'):
                        blastlab(self.base, folder)
                    self.assertEqual(http.call_count, 1)

    def test_simulator_rejects_arbitrary_targets(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = DisposableWorkspace(folder)
            for name in ['../outside', 'C:/Windows', 'unknown.txt', 'recovery/mission.txt']:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    workspace.checked(name)
            before = workspace.snapshot()
            workspace.simulate_destroy()
            self.assertFalse((workspace.path / 'mission.txt').exists())
            self.assertEqual(workspace.snapshot(recovery=True), before)
            self.assertEqual(workspace.reset(), before)

    def test_child_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = DisposableWorkspace(folder)
            workspace.path = Path(folder)
            with self.assertRaises(ValueError):
                workspace.simulate_destroy()

    def test_hard_link_target_rejected_without_modifying_outside_file(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = DisposableWorkspace(folder)
            outside = Path(folder) / 'outside.txt'
            outside.write_bytes(b'preserve me')
            mission = workspace.checked('mission.txt')
            mission.rename(workspace.path / 'mission-original.txt')
            os.link(outside, mission)
            with self.assertRaises(ValueError):
                workspace.simulate_destroy()
            self.assertEqual(outside.read_bytes(), b'preserve me')

    def test_reset_collision_rejected_before_any_move(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = DisposableWorkspace(folder)
            workspace.simulate_destroy()
            backup_hashes = workspace.snapshot(recovery=True)
            workspace.checked('scratch.txt').write_text('unexpected new data')
            with self.assertRaises(ValueError):
                workspace.reset()
            self.assertEqual(workspace.snapshot(recovery=True), backup_hashes)
            self.assertFalse(workspace.checked('mission.txt').exists())

    def test_symlink_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = DisposableWorkspace(folder)
            outside = Path(folder) / 'outside.txt'
            outside.write_bytes(b'preserve me')
            mission = workspace.checked('mission.txt')
            mission.rename(workspace.path / 'mission-original.txt')
            try:
                mission.symlink_to(outside)
            except OSError as error:
                self.skipTest(f'Symlink creation not permitted: {error}')
            with self.assertRaises(ValueError):
                workspace.simulate_destroy()
            self.assertEqual(outside.read_bytes(), b'preserve me')

    def test_junction_recovery_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = DisposableWorkspace(folder)
            original = Path.is_junction
            with patch.object(Path, 'is_junction', lambda p: p == workspace.recovery or original(p)):
                with self.assertRaises(ValueError):
                    workspace.simulate_destroy()

    def test_symlink_guard_rejects_target_before_any_move(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = DisposableWorkspace(folder)
            target = workspace.path / 'scratch.txt'
            before = workspace.snapshot()
            original = Path.is_symlink
            with patch.object(Path, 'is_symlink', lambda p: p == target or original(p)):
                with self.assertRaises(ValueError):
                    workspace.simulate_destroy()
            self.assertEqual(workspace.snapshot(), before)

    def test_suite_persists_fresh_evidence_and_correct_app_fails_acceptance(self):
        with tempfile.TemporaryDirectory() as folder:
            results = run_suite(self.base, Path(folder))
            self.assertTrue(results['acceptance_passed'])
            self.assertEqual(json.loads((Path(folder) / 'evidence.json').read_text()), results)
            self.assertTrue(results['source_sha256'])
        with tempfile.TemporaryDirectory() as folder, local_server(cart_bug=False) as (_, base):
            results = run_suite(base, Path(folder))
            self.assertFalse(results['acceptance_passed'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
