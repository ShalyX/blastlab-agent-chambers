"""Offline verifier for BlastLab public sanitized evidence. No network or app account needed.

Usage: python verify_public_evidence.py public-run.json
This validates the PUBLIC SANITIZED chain only. The original private raw trace
digest is provenance, and cannot be recomputed without the original raw log.
"""
import hashlib
import json
import sys
from pathlib import Path


def digest(item):
    raw=json.dumps(item,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def verify(data):
    events=data.get('events', [])
    if not isinstance(events,list) or not events:
        raise ValueError('Empty or invalid events')
    if data.get('proof',{}).get('public_scheme')!='sha256-chain/canonical-json-v1':
        raise ValueError('Unsupported public proof format')
    previous=None
    for n, item in enumerate(events,1):
        if item.get('seq')!=n or item.get('public_previous_sha256')!=previous:
            raise ValueError(f'Invalid sequence or prior digest: event {n}')
        payload={k:v for k,v in item.items() if k not in ('public_previous_sha256','public_sha256')}
        previous=digest({'previous_sha256':previous,'event':payload})
        if item.get('public_sha256')!=previous:
            raise ValueError(f'Tampered public event {n}')
    if data['proof'].get('public_sha256')!=previous:
        raise ValueError('Public final digest mismatch')
    if data['proof'].get('public_event_count')!=len(events):
        raise ValueError('Public event count mismatch')
    return {
        'verified':True,
        'scope':'self-contained sanitized replay chain, not original raw log',
        'events':len(events),
        'sha256':previous,
        'source_digest_provenance_only':data['proof'].get('trace_sha256'),
    }


def main():
    if len(sys.argv)!=2:
        print(__doc__,file=sys.stderr);sys.exit(2)
    try:
        result=verify(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')))
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,KeyError,TypeError) as e:
        print('PUBLIC_EVIDENCE_VERIFICATION_FAILED: '+str(e),file=sys.stderr)
        sys.exit(2)


if __name__=='__main__':
    main()
