"""Reject private planning and agent-workflow files in the published tree."""
from pathlib import PurePosixPath
import subprocess
import sys

PUBLIC_ROOT_DOCS = {
    'README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'CHANGELOG.md',
    'CODE_OF_CONDUCT.md', 'AUTHORS.md', 'LICENSE.md',
}
PRIVATE_PARTS = {'.hackathon', '.codex', '.agents', 'private'}
PRIVATE_INSTRUCTIONS = {'AGENTS.md', 'CLAUDE.md', 'SKILL.md'}


def is_private(name):
    path = PurePosixPath(name)
    return (
        bool(set(path.parts) & PRIVATE_PARTS)
        or path.name in PRIVATE_INSTRUCTIONS
        or (len(path.parts) == 1 and path.suffix == '.md'
            and path.name not in PUBLIC_ROOT_DOCS)
        or name.startswith(('docs/legacy/', 'deploy/phase', 'deploy/patch_',
                              'web/qa-phase', 'test_phase'))
        or (name.startswith('submission/') and path.suffix in {'.md', '.json'})
    )


if __name__ == '__main__':
    tracked = subprocess.check_output(
        ['git', 'ls-files', '-z'], text=True).split('\0')
    blocked = [name for name in tracked if name and is_private(name)]
    if blocked:
        print('Private workflow files must stay outside the public repository:')
        print('\n'.join(blocked))
        sys.exit(1)
    print('Public file boundary passed')
