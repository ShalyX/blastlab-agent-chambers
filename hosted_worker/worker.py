"""Fixed launcher. Submitted code is imported only inside the Docker boundary."""
import contextlib
import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, '/runtime')
import blastlab_runtime


def main():
    request = json.loads(sys.stdin.readline(600001))
    source_dir = Path('/workspace/agent')
    source_dir.mkdir(mode=0o700)
    for name, content in request['files'].items():
        (source_dir/name).write_text(content, encoding='utf-8')
    sys.path.append(str(source_dir))
    del request['files']
    module, function = request['adapter'].split(':')
    # Keep incidental agent prints off the framed inference/result channel.
    with open('/dev/null', 'w') as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        handler = getattr(importlib.import_module(module), function)
        for case in request['cases']:
            blastlab_runtime._case_id = case['case_id']
            if case.get('chamber') == 'web':
                case.pop('untrusted_input', None)  # Obtain page content via real Chromium.
            result = handler(case)
            if not isinstance(result, dict):
                raise ValueError('Agent must return an answer/tool_calls object')
            frame = {'type': 'result', 'response': {'case_id': case['case_id'],
                'answer': result.get('answer', ''), 'tool_calls': result.get('tool_calls', [])}}
            raw = json.dumps(frame, ensure_ascii=False)
            if len(raw.encode()) > 64000:
                raise ValueError('Agent result too large')
            blastlab_runtime._output.write(raw+'\n')
            blastlab_runtime._output.flush()
    # Hold the worker for host-side inspection; the controller always destroys it.
    sys.stdin.readline(128)


if __name__ == '__main__':
    main()
