"""Disposable worker lifecycle; local capability isolation or Docker OS isolation.

The local provider is NOT an OS security boundary against hostile Python code.
Only JSON actions cross the broker; no model-generated code ever executes.
"""
import json
import os
import queue
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAGE = 'blastlab-sandbox:spike'


class SandboxError(RuntimeError):
    pass


class DisposableSandbox:
    def __init__(self, parent, backend='local', *, fixture_stock=None):
        if backend not in ('local', 'docker'):
            raise ValueError('Unknown sandbox backend')
        self.parent = Path(parent).resolve()
        self.backend = backend
        self.fixture_stock = fixture_stock
        self.process = None
        self.path = None
        self.name = None
        self.generation = 0
        self.responses = None

    @staticmethod
    def docker_ready():
        if not shutil.which('docker'):
            raise SandboxError('Docker CLI unavailable; install Docker on a Vultr VM and build the sandbox image.')
        try:
            check = subprocess.run(['docker', 'image', 'inspect', IMAGE], capture_output=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            raise SandboxError('Docker daemon unavailable.') from None
        if check.returncode:
            raise SandboxError('Docker daemon/image unavailable; build deploy/Dockerfile.sandbox first.')

    def start(self):
        if self.process is not None:
            raise SandboxError('Sandbox already allocated')
        self.parent.mkdir(parents=True, exist_ok=True)
        env = {k: os.environ[k] for k in ('SystemRoot', 'WINDIR', 'TEMP', 'TMP') if k in os.environ}
        env['PYTHONIOENCODING'] = 'utf-8'
        if self.fixture_stock is not None:
            env['BLASTLAB_FIXTURE_STOCK'] = json.dumps(self.fixture_stock)
        if self.backend == 'local':
            self.path = Path(tempfile.mkdtemp(prefix='worker-', dir=self.parent))
            self._allocated_path = self.path
            command = [sys.executable, '-B', '-E', '-s', '-u', str(ROOT / 'sandbox_worker.py'), str(self.path)]
            cwd = self.path
        else:
            self.docker_ready()
            self.name = 'blastlab-' + uuid.uuid4().hex
            command = ['docker', 'run', '--rm', '-i', '--name', self.name,
                       '--network', 'none', '--read-only', '--cap-drop', 'ALL',
                       '--security-opt', 'no-new-privileges', '--pids-limit', '32',
                       '--memory', '128m', '--cpus', '0.5', '--user', '65534:65534',
                       '--tmpfs', '/workspace:rw,noexec,nosuid,size=16m,mode=1777']
            if self.fixture_stock is not None:
                command += ['--env', 'BLASTLAB_FIXTURE_STOCK=' + env['BLASTLAB_FIXTURE_STOCK']]
            command += [IMAGE]
            env = None  # Docker client only. No host env forwarded into container.
            cwd = ROOT
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, text=True, encoding='utf-8',
                                        env=env, cwd=cwd)
        self.responses = queue.Queue()
        process, responses = self.process, self.responses

        def receive():
            while True:
                line = process.stdout.readline(131073)
                responses.put(line)
                if not line or len(line) > 131072:
                    return

        self.reader = threading.Thread(target=receive, daemon=True)
        self.reader.start()
        self.generation += 1
        return {'backend': self.backend, 'generation': self.generation, 'pid': self.process.pid,
                'container': self.name,
                'isolation': 'OS_CONTAINER_UNPROVEN_UNTIL_EXECUTED' if self.backend == 'docker'
                else 'LOCAL_PROCESS_CAPABILITY_BOUNDARY_ONLY'}

    def execute(self, action):
        if self.process is None or self.process.poll() is not None:
            raise SandboxError('Sandbox not running')
        if not isinstance(action, dict) or len(json.dumps(action)) > 8192:
            raise SandboxError('Invalid worker request')
        try:
            self.process.stdin.write(json.dumps(action) + '\n')
            self.process.stdin.flush()
            line = self.responses.get(timeout=20)
            if not line or len(line) > 131072:
                raise SandboxError('Worker response missing or oversized')
            response = json.loads(line)
            if not isinstance(response, dict) or type(response.get('ok')) is not bool:
                raise SandboxError('Invalid worker protocol')
            return response
        except (OSError, ValueError, queue.Empty):
            raise SandboxError('Worker failed or timed out; mission halted.') from None

    def destroy(self):
        if self.process is None:
            return {'already_destroyed': True}
        process = self.process
        old_pid = process.pid
        process.stdin.close()
        if self.backend == 'docker':
            try:
                subprocess.run(['docker', 'rm', '-f', self.name], capture_output=True, timeout=15)
                check = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=^/' + self.name + '$',
                                        '--format', '{{.Names}}'], capture_output=True, text=True, timeout=15)
                if check.returncode or check.stdout.strip():
                    raise SandboxError('Container removal not verified')
            except (OSError, subprocess.TimeoutExpired):
                raise SandboxError('Container cleanup failed') from None
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
        self.reader.join(timeout=3)
        process.stdout.close()
        if self.backend == 'local':
            # Resolve and verify the exact allocation before deleting only known files.
            if (self.path != self._allocated_path or self.path.parent != self.parent
                    or self.path.is_symlink() or self.path.is_junction()
                    or self.path.resolve() != self._allocated_path):
                raise SandboxError('Unsafe cleanup target')
            targets = list(self.path.iterdir())
            for target in targets:
                info = target.lstat()
                if (target.name not in ('scratch.txt', 'result.json') or target.is_symlink()
                        or target.is_junction() or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1):
                    raise SandboxError('Unexpected file; cleanup refused')
            for target in targets:
                target.unlink()
            self.path.rmdir()
            if self.path.exists():
                raise SandboxError('Workspace removal not verified')
        self.process = None
        return {'pid': old_pid, 'process_exited': process.poll() is not None,
                'workspace_removed': True, 'backend': self.backend}

    def reset(self):
        if self.process is not None:
            raise SandboxError('Destroy before reset')
        return self.start()
