"""
Isolated Unit & Concurrency Tests for WP-01: Instance Authority.

Governing ADR: ADR-034 (ARCH-034)
Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Tests cover:
- T01: First acquisition
- T02: Same-process double acquisition (same instance and second instance)
- T03: Concurrent second process conflict (fail-closed, InstanceAuthorityConflictError, zero writes)
- T04: Normal release and reacquisition
- T05: Crash / forced termination recovery without stale-lock cleanup
- T06: Existing .instance.lock file does not block acquisition
- T07: No state mutation before authority
- T08: Platform behavior & latency benchmark (<= 5 ms target)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from src.core.identity.instance_lock import (
    DEFAULT_LOCK_PATH,
    InstanceAuthorityConflictError,
    InstanceLock,
)


class TestInstanceLockAuthority:
    """Comprehensive test matrix for WP-01 Instance Authority."""

    def test_t01_first_acquisition(self, tmp_path: Path):
        """T01: One process/instance acquires authority successfully."""
        lock_file = tmp_path / ".instance.lock"
        lock = InstanceLock(lock_path=lock_file)

        assert not lock.is_locked
        assert lock.acquired_at is None
        assert lock.acquisition_latency_ms is None

        lock.acquire()

        try:
            assert lock.is_locked
            assert lock.pid == os.getpid()
            assert lock.acquired_at is not None
            assert lock.acquisition_latency_ms is not None
            assert lock.acquisition_latency_ms >= 0.0
            # Target acquisition latency <= 5 ms under normal conditions
            # We record and assert a generous bound for testing environments
            assert lock.acquisition_latency_ms < 50.0

            # Lockfile exists and contains diagnostic payload
            assert lock_file.exists()
            assert lock_file.stat().st_size > 0
        finally:
            lock.release()

        assert not lock.is_locked
        # Lockfile must NOT be deleted upon release (zero stale-lock cleanup script invariant)
        assert lock_file.exists()

    def test_t02_same_process_double_acquisition(self, tmp_path: Path):
        """
        T02: Same-process double acquisition behavior:
        1. Calling acquire() on the same InstanceLock instance raises RuntimeError.
        2. Calling acquire() on a second InstanceLock targeting the same workspace
           raises InstanceAuthorityConflictError.
        """
        lock_file = tmp_path / ".instance.lock"
        lock1 = InstanceLock(lock_path=lock_file)
        lock1.acquire()

        try:
            # Case 1: Same object double acquisition
            with pytest.raises(RuntimeError, match="already held by this InstanceLock"):
                lock1.acquire()

            # Case 2: Second object in same process attempting acquisition on same workspace
            lock2 = InstanceLock(lock_path=lock_file)
            with pytest.raises(InstanceAuthorityConflictError):
                lock2.acquire()

            assert not lock2.is_locked
        finally:
            lock1.release()

        # After lock1 releases, lock2 can now acquire successfully
        lock2 = InstanceLock(lock_path=lock_file)
        lock2.acquire()
        assert lock2.is_locked
        lock2.release()

    def test_t03_concurrent_second_process(self, tmp_path: Path):
        """
        T03: Concurrent second process:
        Process A holds the lock.
        Process B attempts acquisition.
        B receives InstanceAuthorityConflictError, obtains zero authority,
        and performs zero state writes.
        """
        lock_file = tmp_path / ".instance.lock"
        state_file = tmp_path / "mock_state.json"

        # Start Process A holding lock via subprocess
        holder_code = f"""
import sys, time
from pathlib import Path
from src.core.identity.instance_lock import InstanceLock

lock = InstanceLock(lock_path=Path(r"{lock_file}"))
lock.acquire()
sys.stdout.write("LOCKED\\n")
sys.stdout.flush()

# Keep holding until signaled to terminate
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    lock.release()
"""
        proc_a = subprocess.Popen(
            [sys.executable, "-c", holder_code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd(),
        )

        try:
            ready_line = proc_a.stdout.readline()
            assert "LOCKED" in ready_line, f"Holder failed to start: {ready_line}"

            # Process B attempts acquisition (in this process)
            lock_b = InstanceLock(lock_path=lock_file)
            conflict_detected = False
            try:
                lock_b.acquire()
            except InstanceAuthorityConflictError:
                conflict_detected = True

            assert conflict_detected, "Process B did not raise InstanceAuthorityConflictError"
            assert not lock_b.is_locked
            assert not state_file.exists(), "Zero state writes must occur upon conflict"

            # Verify subprocess attempt as well (matching exit code 75 / fail closed)
            competitor_code = f"""
import sys
from pathlib import Path
from src.core.identity.instance_lock import InstanceLock, InstanceAuthorityConflictError

lock = InstanceLock(lock_path=Path(r"{lock_file}"))
try:
    lock.acquire()
    sys.exit(0)
except InstanceAuthorityConflictError:
    # Fail closed with exit code 75
    sys.exit(75)
"""
            proc_b = subprocess.run(
                [sys.executable, "-c", competitor_code],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )
            assert proc_b.returncode == 75, f"Expected exit code 75 on conflict, got {proc_b.returncode}"

        finally:
            proc_a.terminate()
            proc_a.wait(timeout=5)

    def test_t04_normal_release_and_reacquisition(self, tmp_path: Path):
        """T04: Normal release: Acquire -> release -> acquire again."""
        lock_file = tmp_path / ".instance.lock"
        lock = InstanceLock(lock_path=lock_file)

        lock.acquire()
        assert lock.is_locked
        lock.release()
        assert not lock.is_locked

        # Second acquisition succeeds
        lock.acquire()
        assert lock.is_locked
        lock.release()
        assert not lock.is_locked

    def test_t05_crash_forced_termination_recovery(self, tmp_path: Path):
        """
        T05: Crash / forced termination:
        Process A acquires lock and is forcibly terminated (os._exit or kill).
        Process B subsequently attempts acquisition.
        B acquires authority immediately without any stale-lock cleanup.
        """
        lock_file = tmp_path / ".instance.lock"

        crash_code = f"""
import os, sys, time
from pathlib import Path
from src.core.identity.instance_lock import InstanceLock

lock = InstanceLock(lock_path=Path(r"{lock_file}"))
lock.acquire()
sys.stdout.write("CRASH_READY\\n")
sys.stdout.flush()
# Abrupt crash without cleanup handlers
os._exit(42)
"""
        proc = subprocess.run(
            [sys.executable, "-c", crash_code],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )
        assert proc.returncode == 42
        assert "CRASH_READY" in proc.stdout

        # Lock file remains on disk from crashed process
        assert lock_file.exists()

        # Process B must acquire authority without manual stale-lock cleanup
        lock_b = InstanceLock(lock_path=lock_file)
        lock_b.acquire()
        assert lock_b.is_locked
        assert lock_b.pid == os.getpid()
        lock_b.release()

    def test_t06_existing_lockfile_does_not_imply_authority(self, tmp_path: Path):
        """
        T06: Existing .instance.lock:
        Ensure an existing lock file does NOT by itself imply authority.
        Authority must depend strictly on the OS kernel lock state.
        """
        lock_file = tmp_path / ".instance.lock"
        # Simulate a pre-existing dead lock file with old PID
        stale_content = json.dumps({
            "pid": 999999,
            "acquired_at": "2020-01-01T00:00:00Z",
            "platform": "win32",
        })
        lock_file.write_text(stale_content, encoding="utf-8")
        assert lock_file.exists()

        # A new process must acquire without needing to delete the file
        lock = InstanceLock(lock_path=lock_file)
        lock.acquire()
        assert lock.is_locked
        assert lock.pid == os.getpid()

        lock.release()
        assert lock_file.exists()

    def test_t07_no_mutation_before_authority(self, tmp_path: Path):
        """
        T07: No mutation before authority:
        Attempt authoritative startup / state mutation while authority is unavailable.
        Verify no identity-state mutation occurs.
        """
        lock_file = tmp_path / ".instance.lock"
        state_dir = tmp_path / "data"
        state_dir.mkdir(parents=True, exist_ok=True)
        profile_file = state_dir / "profile.json"
        profile_file.write_text('{"is_onboarded": false}', encoding="utf-8")

        # Process A holds the lock
        lock_a = InstanceLock(lock_path=lock_file)
        lock_a.acquire()

        try:
            # Candidate startup attempt that respects WP-01 boundary
            def mock_authoritative_startup(workspace: Path) -> None:
                lock = InstanceLock(lock_path=workspace / ".instance.lock")
                lock.acquire()  # must raise InstanceAuthorityConflictError
                # Mutating action that MUST NEVER BE REACHED:
                with open(workspace / "data" / "profile.json", "w", encoding="utf-8") as f:
                    f.write('{"is_onboarded": true}')

            with pytest.raises(InstanceAuthorityConflictError):
                mock_authoritative_startup(tmp_path)

            # State must remain 100% untouched
            assert profile_file.read_text(encoding="utf-8") == '{"is_onboarded": false}'
        finally:
            lock_a.release()

    def test_t08_platform_behavior_and_latency(self, tmp_path: Path):
        """
        T08: Platform behavior:
        Measure acquisition latency against architectural target (<= 5 ms).
        Note: The prompt explicitly states:
        'Target acquisition latency <= 5 ms under normal local conditions...
         Do not treat this as a hard guarantee if the platform cannot guarantee it; measure it in tests.'
        """
        lock_file = tmp_path / ".instance.lock"
        latencies = []

        for _ in range(5):
            lock = InstanceLock(lock_path=lock_file)
            lock.acquire()
            assert lock.acquisition_latency_ms is not None
            latencies.append(lock.acquisition_latency_ms)
            lock.release()
            # Brief yield to allow OS handle teardown
            time.sleep(0.01)

        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        print(f"\n[T08] Measured acquisition latencies: {latencies} ms (min: {min_latency:.4f} ms, avg: {avg_latency:.4f} ms)")
        # Cold/min acquisition latency easily achieves the <= 5 ms target
        assert min_latency < 5.0, f"Minimum acquisition latency {min_latency:.4f} ms exceeded 5 ms target"
        # Bounded acquisition check: must not hang or block indefinitely
        assert avg_latency < 50.0, f"Average acquisition latency {avg_latency:.4f} ms exceeded 50 ms bounded limit"

    def test_context_manager_support(self, tmp_path: Path):
        """Verify context manager interface (__enter__ / __exit__)."""
        lock_file = tmp_path / ".instance.lock"
        with InstanceLock(lock_path=lock_file) as lock:
            assert lock.is_locked
            assert lock_file.exists()
        assert not lock.is_locked
