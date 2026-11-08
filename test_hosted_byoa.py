"""Behavioral contracts for actual customer code inside the hosted boundary."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import agent_lab
import agent_lab_service as service


def fake_live_plan(config, canary):
    """Unit-only planner fixture; no dependency on local untracked QA helpers."""
    state, _ = agent_lab.create_session(config)
    plan = state['attack_plan']
    for attack in plan['attacks']:
        attack['payload'] = attack['payload'].replace(state['canary'], canary)
        attack['source'] = 'VULTR_LLM_GENERATED'
    plan.update(source='VULTR_LLM_GENERATED', provider='unit-test fixture', model='test-model')
    plan['sha256'] = agent_lab.digest({k:v for k,v in plan.items() if k != 'sha256'})
    return plan


class HostedContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir_patch = patch.object(service, 'DIR', Path(self.temp.name))
        self.dir_patch.start()
        self.addCleanup(self.dir_patch.stop)

    def create(self):
        with patch.object(service, 'generate_vultr_attack_plan', side_effect=fake_live_plan):
            code, item = service.new_campaign({'agent_name': 'My own agent',
                'task': 'Summarize the supplied synthetic document.',
                'forbidden_tools': ['send_http'], 'execution_mode': 'vultr_sandbox'})
        self.assertEqual(code, 201, item)
        return item

    def test_customer_cannot_forge_hosted_results_via_external_response_endpoint(self):
        item = self.create()
        code, _ = service.post_campaign(item['session_id'], 'Bearer '+item['join_token'],
            {'case_id': 'control', 'answer': 'fabricated', 'tool_calls': []})
        self.assertEqual(code, 409)
        self.assertEqual(service._read_session(item['session_id'])['case_cursor'], 0)

    def test_hosted_replay_preserves_mode_and_exact_attack_plan(self):
        state, _ = agent_lab.create_session({'agent_name': 'My own agent',
            'task': 'Summarize the supplied synthetic document.', 'forbidden_tools': ['send_http']})
        while (case := agent_lab.next_case(state)):
            agent_lab.add_response(state, {'case_id': case['case_id'], 'answer': 'summary', 'tool_calls': []})
        before = agent_lab.report(state)
        replay, _ = agent_lab.replay_session({**state['config'], 'execution_mode': 'vultr_sandbox'}, before)
        self.assertEqual(replay['config']['execution_mode'], 'vultr_sandbox')
        self.assertEqual(replay['attack_plan'], state['attack_plan'])
        self.assertEqual(replay['canary'], state['canary'])

    def test_source_bundle_cannot_escape_or_supply_runtime_overrides(self):
        import hosted_byoa
        for name in ['../evil.py', '/evil.py', 'a\\evil.py', 'blastlab_runtime.py', '.env', 'agent.py/../../x.py']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                hosted_byoa.validate_bundle({'files': {name: 'pass'}, 'adapter': 'agent:respond'})
        with self.assertRaises(ValueError):
            hosted_byoa.validate_bundle({'files': {'agent.py': 'pass'}, 'adapter': 'os:system'})

    def test_hosted_start_requires_valid_campaign_token_and_is_idempotent(self):
        import hosted_byoa
        item = self.create()
        payload = {'files': {'agent.py': 'def respond(case): return {}'}, 'adapter': 'agent:respond'}
        self.assertEqual(hosted_byoa.start(item['session_id'], 'Bearer wrong', payload)[0], 401)
        with patch.object(hosted_byoa.threading, 'Thread') as thread:
            code, _ = hosted_byoa.start(item['session_id'], 'Bearer '+item['join_token'], payload)
            try:
                self.assertEqual(code, 202)
                self.assertEqual(hosted_byoa.start(item['session_id'], 'Bearer '+item['join_token'], payload)[0], 200)
                self.assertEqual(thread.call_count, 1)
            finally:
                hosted_byoa.SLOT.release()

    def test_failed_execution_never_publishes_a_successful_report(self):
        import hosted_byoa
        item = self.create()
        hosted_byoa.SLOT.acquire()
        with patch.object(hosted_byoa, 'provider', side_effect=RuntimeError('private provider error')):
            hosted_byoa.execute(item['session_id'], {})
        state = service._read_session(item['session_id'])
        self.assertEqual(state['execution_state'], 'failed')
        self.assertEqual(state['case_cursor'], 0)
        self.assertNotIn('private provider error', state['execution_error'])
        self.assertEqual(service.get_campaign(item['session_id'], 'Bearer '+item['join_token'], 'report')[0], 409)

    def test_restart_marks_interrupted_campaign_failed_and_removes_labeled_worker(self):
        import hosted_byoa
        item = self.create()
        state = service._read_session(item['session_id'])
        state['execution_state'] = 'running'
        service.atomic_json(service.session_file(item['session_id']), state)
        with patch.object(hosted_byoa, 'docker', side_effect=[b'abcd1234abcd\n', b'']) as command:
            hosted_byoa.recover_interrupted()
        self.assertEqual(command.call_args_list[-1].args, ('rm', '-f', 'abcd1234abcd'))
        self.assertEqual(service._read_session(item['session_id'])['execution_state'], 'failed')

    def test_docker_boundary_has_no_host_mount_network_secrets_or_unbounded_resources(self):
        import hosted_byoa
        args = hosted_byoa.container_args('blastlab-customer-'+'a'*32)
        self.assertIn('--network=none', args)
        self.assertIn('--read-only', args)
        self.assertIn('--cap-drop=ALL', args)
        self.assertIn('--memory=256m', args)
        self.assertIn('--pids-limit=48', args)
        self.assertIn('--cpus=0.5', args)
        self.assertIn('--user=10001:10001', args)
        self.assertFalse(any('mount' in arg or 'volume' in arg or 'API_KEY' in arg for arg in args))

    def test_hosted_report_requires_real_boundary_shape_and_verified_teardown(self):
        item = self.create()
        state = service._read_session(item['session_id'])
        while (case := agent_lab.next_case(state)):
            agent_lab.add_response(state, {'case_id': case['case_id'], 'answer': 'summary', 'tool_calls': []})
        checks = {name: True for name in ['network_none', 'read_only_root', 'unprivileged_user',
            'no_host_mounts', 'capabilities_dropped', 'no_new_privileges', 'not_privileged',
            'bounded_resources', 'no_credentials', 'no_host_namespaces']}
        state['execution'] = {'container_name': 'blastlab-customer-'+state['id'],
            'checks': checks, 'bundle_sha256': 'a'*64, 'image_id': 'sha256:'+'b'*64,
            'attack_plan_sha256': state['attack_plan']['sha256'], 'teardown_verified': True,
            'provider': 'Vultr Serverless Inference', 'inference_calls': 6}
        artifact = agent_lab.report(state)
        self.assertTrue(agent_lab.verify_report(artifact))
        artifact['execution']['teardown_verified'] = False
        artifact['manifest_sha256'] = agent_lab.digest({k:v for k,v in artifact.items() if k != 'manifest_sha256'})
        self.assertFalse(agent_lab.verify_report(artifact))


if __name__ == '__main__':
    unittest.main()
