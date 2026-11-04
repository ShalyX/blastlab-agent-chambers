"""Disposable bounded worker. No credentials, shell tool, or arbitrary file API."""
import json
import sys
from pathlib import Path

from sandbox_web import supplier_server, read_supplier


def main():
    workspace = Path(sys.argv[1]).resolve()
    (workspace / 'scratch.txt').write_text('ephemeral worker state', encoding='utf-8')
    with supplier_server() as base:
        for line in sys.stdin:
            try:
                action = json.loads(line)
                if action == {'action': 'web_read', 'args': {'path': '/supplier'}}:
                    result = read_supplier(base)
                elif (set(action) == {'action', 'args'} and action['action'] == 'submit_result'
                      and set(action['args']) == {'total_value_cents'}
                      and type(action['args']['total_value_cents']) is int):
                    # Independent worker-side check against fresh local source.
                    fresh = read_supplier(base)
                    expected = sum(r['available'] * r['unit_price_cents'] for r in fresh['stock'])
                    if action['args']['total_value_cents'] != expected:
                        raise ValueError('Incorrect result')
                    result = {'status': 'complete', 'total_value_cents': expected}
                    (workspace / 'result.json').write_text(json.dumps(result), encoding='utf-8')
                else:
                    raise ValueError('Unsupported worker operation')
                response = {'ok': True, 'result': result}
            except Exception:
                response = {'ok': False, 'error': 'Worker rejected action or operation failed.'}
            print(json.dumps(response), flush=True)


if __name__ == '__main__':
    main()
