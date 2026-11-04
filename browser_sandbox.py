"""Disposable browser backends. Local is a harness; Docker is the OS boundary."""
import json
import os
import queue
import shutil
import subprocess
import threading
import uuid
from pathlib import Path

from browser_inference import GateError

ROOT = Path(__file__).resolve().parent


def worker_environment():
    # No inherited API credentials, proxy settings, NODE_OPTIONS, or profile config.
    allowed = ('PATH', 'SystemRoot', 'WINDIR', 'TEMP', 'TMP', 'HOME', 'USERPROFILE',
               'LOCALAPPDATA', 'ProgramFiles', 'ProgramFiles(x86)', 'PROGRAMW6432',
               'PLAYWRIGHT_BROWSERS_PATH', 'BLASTLAB_PLAYWRIGHT_MODULE',
               'BLASTLAB_CHROME_CHANNEL')
    env = {k: os.environ[k] for k in allowed if k in os.environ}
    if 'BLASTLAB_PLAYWRIGHT_MODULE' not in env:
        existing = Path(os.environ.get('APPDATA', '')) / 'npm/node_modules/@playwright/cli/node_modules/playwright'
        if existing.is_dir():
            env['BLASTLAB_PLAYWRIGHT_MODULE'] = str(existing)
            env.setdefault('BLASTLAB_CHROME_CHANNEL', 'chrome')
    return env


def docker_command(name):
    return ['docker', 'run', '--pull=never', '--name', name, '--rm', '-i',
            '--network=none', '--read-only', '--cap-drop=ALL',
            '--security-opt=no-new-privileges', '--pids-limit=128', '--memory=768m',
            '--cpus=1', '--user=10001:10001',
            '--tmpfs=/tmp:rw,nosuid,nodev,size=256m,mode=1777',
            '--shm-size=128m', 'blastlab-browser:spike']


class BrowserSandbox:
    def __init__(self, backend, trace, rows, hostile=True):
        if backend not in ('local', 'docker'):
            raise ValueError('Unknown sandbox backend')
        self.backend, self.trace, self.rows, self.hostile = backend, trace, rows, hostile
        self.process = None
        self.generation = 0
        self.ready = None
        self.name = None

    def _read_lines(self, stream, destination):
        try:
            while True:
                line = stream.readline(131073)
                destination.put(line or None)
                if not line or len(line) > 131072:
                    return
        finally:
            pass

    def request(self, command, timeout=25):
        if not self.process or self.process.poll() is not None:
            raise GateError('Sandbox is not running')
        self.trace.emit('sandbox_request', generation=self.generation, command=command)
        try:
            self.process.stdin.write(json.dumps(command) + '\n')
            self.process.stdin.flush()
            line = self.responses.get(timeout=timeout)
            if line is None or len(line) > 131072:
                raise ValueError()
            result = json.loads(line)
            if not result.get('ok'):
                raise ValueError()
        except (queue.Empty, ValueError, OSError):
            self.trace.emit('sandbox_error', generation=self.generation, error='Timeout or invalid worker response')
            raise GateError('Sandbox timeout or invalid response') from None
        self.trace.emit('sandbox_response', generation=self.generation, result=result)
        return result

    def create(self):
        if self.process is not None:
            raise GateError('Destroy the current sandbox before reset')
        self.generation += 1
        self.name = 'blastlab-' + uuid.uuid4().hex
        if self.backend == 'docker':
            if not shutil.which('docker'):
                raise GateError('Docker executable unavailable; provision Docker on the Vultr VM')
            command, env = docker_command(self.name), None
        else:
            command, env = ['node', str(ROOT / 'browser-worker.cjs')], worker_environment()
        self.responses = queue.Queue(maxsize=16)
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, text=True, encoding='utf-8',
                                        env=env, cwd=ROOT)
        self.reader = threading.Thread(target=self._read_lines, args=(self.process.stdout, self.responses), daemon=True)
        self.reader.start()
        self.trace.emit('sandbox_created', backend=self.backend, generation=self.generation,
                        os_boundary=self.backend == 'docker', command=command)
        self.ready = self.request({'action': 'init', 'rows': self.rows, 'hostile': self.hostile})
        if self.ready['inherited_secret_names']:
            raise GateError('Sandbox inherited a secret-like variable name; aborting')
        return self.ready

    def destroy(self):
        if self.process is None:
            return
        process = self.process
        confirmed = False
        try:
            if process.poll() is None:
                result = self.request({'action': 'destroy'})
                confirmed = result.get('destroyed') and result.get('workspace_absent')
            process.wait(timeout=10)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
            if self.backend == 'docker':
                subprocess.run(['docker', 'rm', '-f', self.name], capture_output=True, timeout=15)
                inspected = subprocess.run(['docker', 'inspect', self.name], capture_output=True, timeout=15)
                if inspected.returncode == 0 or b'No such object' not in inspected.stderr:
                    raise GateError('Cannot verify Docker sandbox removal')
            process.stdin.close()
            process.stdout.close()
            self.reader.join(timeout=2)
            self.process = None
            self.trace.emit('sandbox_destroyed', generation=self.generation,
                            process_exited=process.poll() is not None, workspace_removed=bool(confirmed))
        if not confirmed:
            raise GateError('Worker did not confirm disposable workspace destruction')

    def reset(self):
        if self.process is not None:
            raise GateError('Reset requires a destroyed sandbox')
        return self.create()
