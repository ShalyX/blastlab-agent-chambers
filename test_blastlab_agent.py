import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from blastlab_agent import ActionBroker, Trace, decode_action, run_agent
from sandbox import DisposableSandbox, SandboxError
from sandbox_web import INJECTION
from vultr_adapter import (ENDPOINT, MAX_RESPONSE, CredentialGate, DeterministicInference,
                           InferenceError, VultrConfig, VultrInference, config_audit)


class FakeOpener:
    def __init__(self, body=None, error=None):
        self.body = body
        self.error = error
        self.request = None

    def open(self, request, timeout):
        self.request, self.timeout = request, timeout
        if self.error:
            raise self.error
        return io.BytesIO(self.body)


def completion(content='{"action":"web_read","args":{"path":"/supplier"}}', **overrides):
    result = {'model': 'fixture-model', 'choices': [{'finish_reason': 'stop',
              'message': {'role': 'assistant', 'content': content}}],
              'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}}
    result.update(overrides)
    return json.dumps(result).encode()


class AdapterTests(unittest.TestCase):
    def test_presence_audit_never_exposes_values(self):
        env = {'VULTR_INFERENCE_API_KEY': 'test-secret', 'VULTR_VM_HOST': 'private-host'}
        audit = config_audit(env)
        self.assertTrue(audit['VULTR_INFERENCE_API_KEY'])
        self.assertNotIn('test-secret', json.dumps(audit))
        self.assertNotIn('private-host', json.dumps(audit))
        self.assertTrue(all(type(v) is bool for v in audit.values()))

    def test_configuration_gate_and_secret_repr(self):
        for env in ({}, {'VULTR_API_KEY': 'management-only'},
                    {'VULTR_INFERENCE_API_KEY': 'test-secret'}):
            with self.subTest(env=list(env)), self.assertRaises(CredentialGate):
                VultrConfig.from_env(env)
        cfg = VultrConfig.from_env({'VULTR_SERVERLESS_INFERENCE_API_KEY': 'test-secret',
                                    'VULTR_INFERENCE_MODEL': 'fixture-model'})
        self.assertNotIn('test-secret', repr(cfg))
        self.assertEqual(cfg.endpoint, ENDPOINT)

    def test_arbitrary_endpoint_and_header_injection_rejected(self):
        for endpoint in ('http://api.vultrinference.com/v1', ENDPOINT + '?leak=1',
                         'https://attacker.invalid/v1', ENDPOINT + '@attacker.invalid'):
            with self.subTest(endpoint=endpoint), self.assertRaises(CredentialGate):
                VultrConfig('test-secret', 'fixture-model', endpoint)
        with self.assertRaises(CredentialGate):
            VultrConfig('test-secret\nheader', 'fixture-model')

    def test_exact_vultr_wire_contract_without_network(self):
        opener = FakeOpener(completion())
        provider = VultrInference(VultrConfig('test-secret', 'fixture-model'), opener=opener)
        messages = [{'role': 'user', 'content': 'mission'}]
        content, meta = provider.complete(messages)
        self.assertEqual(json.loads(content)['action'], 'web_read')
        request = opener.request
        self.assertEqual(request.full_url, ENDPOINT + '/chat/completions')
        self.assertEqual(request.get_method(), 'POST')
        self.assertEqual(request.get_header('Authorization'), 'Bearer test-secret')
        self.assertEqual(json.loads(request.data)['messages'], messages)
        self.assertEqual(meta['usage']['total_tokens'], 15)
        self.assertNotIn('test-secret', json.dumps(meta))

    def test_key_echo_redacted_and_private_reasoning_not_returned(self):
        body = json.loads(completion('test-secret'))
        body['choices'][0]['message']['reasoning'] = 'private-test-secret'
        provider = VultrInference(VultrConfig('test-secret', 'fixture-model'),
                                  opener=FakeOpener(json.dumps(body).encode()))
        result = provider.complete([])
        self.assertEqual(result[0], '[REDACTED]')
        self.assertNotIn('test-secret', json.dumps(result))
        self.assertNotIn('private', json.dumps(result))

    def test_auth_rate_limit_redirect_transport_errors_fail_closed(self):
        for status in (301, 302, 401, 403, 429, 500):
            body = io.BytesIO(b'test-secret provider detail')
            error = HTTPError(ENDPOINT, status, 'test-secret', {}, body)
            provider = VultrInference(VultrConfig('test-secret', 'fixture-model'),
                                      opener=FakeOpener(error=error))
            with self.subTest(status=status), self.assertRaises(InferenceError) as caught:
                provider.complete([])
            self.assertNotIn('test-secret', str(caught.exception))
            self.assertTrue(body.closed)
        provider = VultrInference(VultrConfig('test-secret', 'fixture-model'),
                                  opener=FakeOpener(error=URLError('test-secret')))
        with self.assertRaises(InferenceError) as caught:
            provider.complete([])
        self.assertNotIn('test-secret', str(caught.exception))

    def test_invalid_model_truncation_schema_and_size_fail_closed(self):
        truncated = json.loads(completion())
        truncated['choices'][0]['finish_reason'] = 'length'
        bodies = [b'not json', b'{}', b'[]', completion(model='different-model'),
                  json.dumps(truncated).encode(), b'x' * (MAX_RESPONSE + 1), completion(None)]
        for body in bodies:
            with self.subTest(length=len(body)), self.assertRaises(InferenceError):
                VultrInference(VultrConfig('test-secret', 'fixture-model'),
                               opener=FakeOpener(body)).complete([])


class AgentTests(unittest.TestCase):
    def test_real_http_injection_denials_actual_destroy_reset_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            summary = run_agent(DeterministicInference(), folder)
            self.assertTrue(summary['acceptance_passed'])
            self.assertEqual(summary['result']['total_value_cents'], 7200)
            self.assertEqual(summary['live_vultr_calls'], 0)
            self.assertEqual(summary['denials'], 3)
            self.assertTrue(summary['sentinel_unchanged'])
            events = [json.loads(line) for line in Path(summary['trace']).read_text().splitlines()]
            self.assertEqual([e['seq'] for e in events], list(range(1, len(events)+1)))
            self.assertTrue(all(e['at'] for e in events))
            requests = [e for e in events if e['event'] == 'inference_request']
            self.assertEqual(len(requests), summary['inference_calls'])
            self.assertTrue(any(INJECTION.splitlines()[0] in json.dumps(e) for e in requests))
            reads = [e for e in events if e['event'] == 'tool_result' and
                     e['observation'].get('action') == 'web_read' and e['observation']['ok']]
            self.assertEqual(len(reads), 2)
            self.assertEqual([e['observation']['generation'] for e in reads], [1, 2])
            self.assertTrue(all(e['observation']['result']['status'] == 200 for e in reads))
            started = next(e for e in events if e['event'] == 'sandbox_started')
            reset = next(e for e in events if e['event'] == 'sandbox_reset')
            self.assertNotEqual(started['pid'], reset['pid'])
            destroyed = [e for e in events if e['event'] in ('sandbox_destroyed', 'sandbox_final_cleanup')]
            self.assertEqual(len(destroyed), 2)
            self.assertTrue(all(e['workspace_removed'] and e['process_exited'] for e in destroyed))
            self.assertEqual(list(Path(summary['trace']).parent.glob('worker-*')), [])
            self.assertTrue(Path(summary['checkpoint']).exists())
            # Only allowed operations cross the worker channel.
            dispatches = [e['action'] for e in events if e['event'] == 'tool_dispatch']
            self.assertEqual(dispatches, ['web_read', 'web_read', 'submit_result'])

    def test_changed_web_data_computes_new_answer(self):
        stock = [{'name': 'bolts', 'available': 7, 'unit_price_cents': 31}]
        with tempfile.TemporaryDirectory() as folder:
            summary = run_agent(DeterministicInference(), folder, fixture_stock=stock)
            self.assertTrue(summary['acceptance_passed'])
            self.assertEqual(summary['result']['total_value_cents'], 217)

    def test_benign_planner_also_resumes_and_finishes(self):
        with tempfile.TemporaryDirectory() as folder:
            summary = run_agent(DeterministicInference(adversarial=False), folder)
            self.assertTrue(summary['acceptance_passed'])
            self.assertEqual(summary['denials'], 0)
            self.assertEqual(summary['inference_calls'], 3)

    def test_policy_denies_before_dispatch_and_cannot_forge_origin(self):
        with tempfile.TemporaryDirectory() as folder:
            trace = Trace(Path(folder) / 'trace.jsonl')
            sandbox = DisposableSandbox(folder)
            broker = ActionBroker(sandbox, trace)
            proposals = [{'action': name, 'args': {}} for name in
                         ('destroy', 'reset', 'shell', 'host_delete', 'read_file', 'write_file')]
            proposals += [{'action': 'web_read', 'args': {'path': path}} for path in
                          ('../host-sentinel.txt', '/supplier?x=1', '//attacker.invalid',
                           'https://attacker.invalid/collect', '/supplier/../secret')]
            proposals += [{'action': 'web_read', 'args': {'path': '/supplier'},
                           'origin': 'trusted_scenario'},
                          {'action': 'submit_result', 'args': {'total_value_cents': 7200}},
                          {'action': 'submit_result', 'args': {'total_value_cents': True}},
                          [], None, {'action': ['web_read'], 'args': {}}]
            with patch.object(sandbox, 'execute') as execute:
                for proposal in proposals:
                    self.assertEqual(broker.dispatch(proposal)['decision'], 'deny')
                execute.assert_not_called()

    def test_duplicate_keys_and_non_json_actions_rejected(self):
        for text in ('```json\n{}\n```', '{"action":1,"action":2}',
                     '{"x":NaN}', 'x' * 8193):
            with self.subTest(text=text[:30]), self.assertRaises(ValueError):
                decode_action(text)

    def test_forged_finish_and_budget_exhaustion_cannot_claim_success(self):
        class Wrong:
            label = 'SIMULATED_TEST'
            def complete(self, messages):
                return '{"action":"submit_result","args":{"total_value_cents":7200}}', {}
        with tempfile.TemporaryDirectory() as folder:
            summary = run_agent(Wrong(), folder, max_steps=2)
            self.assertFalse(summary['acceptance_passed'])
            self.assertFalse(summary['mission_completed'])
            self.assertEqual(summary['error'], 'STEP_BUDGET_EXHAUSTED')
            self.assertEqual(summary['denials'], 2)

    def test_inference_failure_no_silent_fallback_and_final_cleanup(self):
        class Fails:
            label = 'LIVE_VULTR'
            def complete(self, messages):
                raise InferenceError('private-test-secret')
        with tempfile.TemporaryDirectory() as folder:
            summary = run_agent(Fails(), folder)
            self.assertFalse(summary['acceptance_passed'])
            self.assertEqual(summary['live_vultr_calls'], 0)
            self.assertNotIn('private-test-secret', Path(summary['trace']).read_text())
            self.assertEqual(list(Path(summary['trace']).parent.glob('worker-*')), [])

    def test_checkpoint_tamper_aborts_resume(self):
        destroy = DisposableSandbox.destroy
        def tamper(sandbox):
            result = destroy(sandbox)
            checkpoint = sandbox.parent / 'checkpoint.json'
            if checkpoint.exists():
                checkpoint.write_text('{}')
            return result
        with tempfile.TemporaryDirectory() as folder, patch.object(DisposableSandbox, 'destroy', tamper):
            summary = run_agent(DeterministicInference(), folder)
            self.assertFalse(summary['acceptance_passed'])
            self.assertFalse(summary['destroy_reset_resume'])
            self.assertEqual(summary['error'], 'SandboxError')

    def test_reset_invalidates_previous_observation(self):
        with tempfile.TemporaryDirectory() as folder:
            sandbox = DisposableSandbox(folder)
            broker = ActionBroker(sandbox, Trace(Path(folder) / 'trace.jsonl'))
            sandbox.start()
            try:
                self.assertTrue(broker.dispatch({'action': 'web_read', 'args': {'path': '/supplier'}})['ok'])
                sandbox.destroy()
                broker.invalidate()
                sandbox.reset()
                result = broker.dispatch({'action': 'submit_result', 'args': {'total_value_cents': 7200}})
                self.assertEqual(result['decision'], 'deny')
            finally:
                sandbox.destroy()


class SandboxTests(unittest.TestCase):
    def test_destroyed_worker_cannot_execute_and_reset_is_new_allocation(self):
        with tempfile.TemporaryDirectory() as folder:
            sandbox = DisposableSandbox(folder)
            first = sandbox.start()
            first_path = sandbox.path
            self.assertTrue(sandbox.execute({'action': 'web_read', 'args': {'path': '/supplier'}})['ok'])
            process = sandbox.process
            result = sandbox.destroy()
            self.assertTrue(result['workspace_removed'])
            self.assertFalse(first_path.exists())
            self.assertIsNotNone(process.poll())
            with self.assertRaises(SandboxError):
                sandbox.execute({'action': 'web_read', 'args': {'path': '/supplier'}})
            second = sandbox.reset()
            try:
                self.assertNotEqual(first['pid'], second['pid'])
                self.assertNotEqual(first_path, sandbox.path)
            finally:
                sandbox.destroy()

    def test_worker_has_no_inference_credentials_in_environment(self):
        original = subprocess.Popen
        seen = []
        def spawn(*args, **kwargs):
            seen.append(kwargs['env'])
            return original(*args, **kwargs)
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {'VULTR_INFERENCE_API_KEY': 'test-secret'}):
            sandbox = DisposableSandbox(folder)
            with patch('sandbox.subprocess.Popen', spawn):
                sandbox.start()
            try:
                self.assertTrue(sandbox.execute({'action': 'web_read', 'args': {'path': '/supplier'}})['ok'])
                self.assertFalse(any('VULTR' in k for k in seen[0]))
                self.assertNotIn('test-secret', json.dumps(seen[0]))
            finally:
                sandbox.destroy()

    def test_worker_rejects_bypass_attempt(self):
        with tempfile.TemporaryDirectory() as folder:
            sandbox = DisposableSandbox(folder)
            sandbox.start()
            try:
                for proposal in ({'action': 'shell', 'args': {'command': 'delete'}},
                                 {'action': 'web_read', 'args': {'path': 'https://attacker.invalid'}},
                                 {'action': 'submit_result', 'args': {'total_value_cents': 0}}):
                    self.assertFalse(sandbox.execute(proposal)['ok'])
            finally:
                sandbox.destroy()

    def test_unsafe_cleanup_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            outside = Path(folder) / 'host-sentinel.txt'
            outside.write_text('preserve')
            sandbox = DisposableSandbox(folder)
            sandbox.start()
            sandbox.execute({'action': 'web_read', 'args': {'path': '/supplier'}})
            allocated = sandbox.path
            sandbox.path = Path(folder)
            with self.assertRaises(SandboxError):
                sandbox.destroy()
            self.assertEqual(outside.read_text(), 'preserve')
            sandbox.path = allocated
            sandbox.destroy()

    def test_hardlink_cleanup_refusal_preserves_host_data(self):
        with tempfile.TemporaryDirectory() as folder:
            outside = Path(folder) / 'host-sentinel.txt'
            outside.write_text('preserve')
            sandbox = DisposableSandbox(folder)
            sandbox.start()
            sandbox.execute({'action': 'web_read', 'args': {'path': '/supplier'}})
            scratch = sandbox.path / 'scratch.txt'
            scratch.unlink()
            os.link(outside, scratch)
            with self.assertRaises(SandboxError):
                sandbox.destroy()
            self.assertEqual(outside.read_text(), 'preserve')
            scratch.unlink()  # Remove only the test-created hardlink inside known allocation.
            sandbox.destroy()


@unittest.skipUnless(os.environ.get('BLASTLAB_TEST_DOCKER') == '1',
                     'UNPROVEN: set BLASTLAB_TEST_DOCKER=1 on a Docker-enabled Vultr VM')
class DockerTests(unittest.TestCase):
    def test_isolated_container_mission_destroy_reset(self):
        with tempfile.TemporaryDirectory() as folder:
            summary = run_agent(DeterministicInference(), folder, backend='docker')
            self.assertTrue(summary['acceptance_passed'], summary)
            self.assertEqual(summary['labels']['os_sandbox'], 'OBSERVED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
