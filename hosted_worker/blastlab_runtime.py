"""Credential-free Vultr inference bridge available to submitted Python agents."""
import json
import sys

_input = sys.stdin
_output = sys.stdout
_case_id = None


def complete(messages, tools=None):
    """Return an assistant message from the host's fixed Vultr provider."""
    frame = {'type': 'inference', 'messages': messages, 'tools': tools or []}
    raw = json.dumps(frame, ensure_ascii=False)
    if len(raw.encode()) > 64000:
        raise ValueError('Inference request exceeds 64 KB')
    _output.write(raw+'\n')
    _output.flush()
    line = _input.readline(262145)
    result = json.loads(line)
    if not result.get('ok'):
        raise RuntimeError('Vultr inference unavailable; no alternate provider used')
    return result['message']


def read_web_page(path='/specimen'):
    """Read this case's synthetic webpage in controller-owned Chromium."""
    if path != '/specimen':
        raise ValueError('Only the configured synthetic specimen is available')
    _output.write(json.dumps({'type': 'web_read', 'case_id': _case_id, 'path': path})+'\n')
    _output.flush()
    result = json.loads(_input.readline(64001))
    if not result.get('ok'):
        raise RuntimeError('Web Chamber page read failed')
    return result['page']
