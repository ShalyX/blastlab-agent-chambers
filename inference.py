"""Vultr-only inference transport. Credentials stay in the supervisor process."""
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, ProxyHandler

from spikes import NoRedirect

ENDPOINT = 'https://api.vultrinference.com/v1'


class GateError(RuntimeError):
    pass


def load_environment(path):
    """Explicit dotenv file, never shell-evaluated; process environment wins."""
    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        name, sep, value = line.partition('=')
        if not sep or not name.startswith(('VULTR_', 'BLASTLAB_')) or not name.replace('_', '').isalnum():
            raise GateError('Invalid configuration line (contents suppressed).')
        os.environ.setdefault(name, value.strip().strip('"\''))


@dataclass(repr=False)
class VultrConfig:
    api_key: str = field(repr=False)
    model: str
    base_url: str = ENDPOINT

    @classmethod
    def from_env(cls):
        key = os.environ.get('VULTR_INFERENCE_API_KEY', '').strip()
        model = os.environ.get('VULTR_INFERENCE_MODEL', '').strip()
        endpoint = os.environ.get('VULTR_INFERENCE_BASE_URL', ENDPOINT).rstrip('/')
        missing = [name for name, value in [('VULTR_INFERENCE_API_KEY', key),
                                           ('VULTR_INFERENCE_MODEL', model)] if not value]
        if missing:
            raise GateError('Missing: ' + ', '.join(missing))
        if endpoint != ENDPOINT:
            raise GateError('All LLM traffic must use the fixed Vultr Serverless Inference endpoint.')
        return cls(key, model, endpoint)


def availability():
    names = ('VULTR_INFERENCE_API_KEY', 'VULTR_INFERENCE_MODEL', 'VULTR_API_KEY',
             'VULTR_VM_HOST', 'VULTR_VM_USER', 'VULTR_VM_SSH_KEY')
    return {name: bool(os.environ.get(name, '').strip()) for name in names}


class VultrInference:
    kind = 'vultr-live'

    def __init__(self, config, trace, opener=None):
        self.config, self.trace = config, trace
        self.opener = opener or build_opener(ProxyHandler({}), NoRedirect())

    def complete(self, messages, tools):
        payload = {'model': self.config.model, 'messages': messages, 'tools': tools,
                   'tool_choice': 'auto', 'stream': False, 'max_completion_tokens': 2048}
        self.trace.emit('inference_request', provider=self.kind, endpoint=ENDPOINT,
                        body=payload)
        request = Request(ENDPOINT + '/chat/completions',
                          data=json.dumps(payload).encode(), method='POST',
                          headers={'Authorization': 'Bearer ' + self.config.api_key,
                                   'Content-Type': 'application/json'})
        started = time.perf_counter()
        try:
            with self.opener.open(request, timeout=45) as response:
                raw = response.read(262145)
                if len(raw) > 262144:
                    raise GateError('Vultr response exceeds 256 KiB limit.')
                body = json.loads(raw)
        except HTTPError as error:
            status = error.code
            error.close()
            self.trace.emit('inference_error', status=status, details='Provider body suppressed')
            raise GateError(f'Vultr HTTP {status}; no fallback or alternate provider used.') from None
        except (URLError, TimeoutError, OSError, ValueError):
            self.trace.emit('inference_error', details='Transport/JSON failure; details suppressed')
            raise GateError('Vultr transport/JSON failure; no fallback used.') from None
        try:
            choice = body['choices'][0]
            message = choice['message']
            if (choice.get('finish_reason') not in ('stop', 'tool_calls')
                    or message.get('role') != 'assistant'
                    or body.get('model') != self.config.model):
                raise ValueError()
            # Do not persist provider private reasoning, only executable/public output.
            public = {k: message[k] for k in ('role', 'content', 'tool_calls') if k in message}
        except (KeyError, IndexError, TypeError, ValueError):
            raise GateError('Invalid/truncated response or returned model differs from configured model.') from None
        self.trace.emit('inference_response', provider=self.kind, response_id=body.get('id'),
                        requested_model=self.config.model, returned_model=body.get('model'),
                        elapsed_ms=round((time.perf_counter() - started) * 1000, 3),
                        usage=body.get('usage'), message=public)
        return public


class DeterministicInference:
    """SIMULATED planner. Replays page-supplied attacks to stress real dispatch."""
    kind = 'deterministic-fixture'

    def __init__(self, trace):
        self.trace = trace
        self.attacks = []
        self.attacked = False
        self.counter = 0

    def complete(self, messages, tools):
        self.counter += 1
        self.trace.emit('inference_request', provider=self.kind, body={'messages': messages, 'tools': tools})
        observations = [json.loads(m['content']) for m in messages if m['role'] == 'tool']
        pages = [o for o in observations if o.get('ok') and 'rows' in o]
        latest = pages[-1] if pages else None
        if latest and not self.attacked:
            self.attacked = True
            # Exact JSON in hostile page content; intentionally susceptible fixture.
            text = latest['text']
            if 'ATTACK_ACTIONS=' in text:
                self.attacks = json.loads(text.split('ATTACK_ACTIONS=', 1)[1].split('\n', 1)[0])
        if self.attacks:
            action = self.attacks.pop(0)
            name, args = action['name'], action['arguments']
        elif not latest or (observations and observations[-1].get('reset_required')):
            name, args = 'browse', {'path': '/supplier'}
        else:
            total = sum(r['available'] * r['unit_price_cents'] for r in latest['rows'])
            name, args = 'finish', {'total_value_cents': total, 'evidence_id': latest['evidence_id']}
        message = {'role': 'assistant', 'content': None, 'tool_calls': [
            {'id': f'call_fixture_{self.counter}', 'type': 'function',
             'function': {'name': name, 'arguments': json.dumps(args)}}]}
        self.trace.emit('inference_response', provider=self.kind, evidence_label='SIMULATED', message=message)
        return message
