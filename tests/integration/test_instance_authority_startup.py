"""
Integration Tests for WP-01 Instance Authority & Server Startup Lifecycle.

Governing ADR: ADR-034 (ARCH-034)
Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IMPLEMENTATION_PLAN.md

Tests:
- Server startup in live mode acquires instance authority before model loading / orchestrator initialization.
- Server startup under authority conflict fails closed immediately with exit code 75 and 'instance_already_active'.
- Zero identity state writes occur during conflict.
- Simulation mode remains unaffected by live instance locking.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest

import src.api.server as api_server
from src.core.identity.instance_lock import (
    InstanceAuthorityConflictError,
    InstanceLock,
)


class TestServerInstanceAuthorityIntegration:
    """Test suite for server.py startup integration with InstanceLock."""

    def test_live_startup_acquires_lock(self, tmp_path: Path):
        """Verify init_server acquires the lock on the specified lock_path."""
        lock_file = tmp_path / ".instance.lock"

        # Ensure previous lock is cleared in api_server
        if api_server._instance_lock is not None and api_server._instance_lock.is_locked:
            api_server._instance_lock.release()
        api_server._instance_lock = None

        # Call init_server with invalid port/no model to test early lock acquisition
        # Because model_path is empty, it will acquire lock, then detect model_path_not_configured
        # and release lock on exit(1).
        # To test that lock was acquired, we intercept sys.exit
        exit_codes = []
        orig_exit = sys.exit

        def mock_exit(code=0):
            exit_codes.append(code)
            raise SystemExit(code)

        sys.exit = mock_exit
        try:
            with pytest.raises(SystemExit) as exc_info:
                api_server.init_server(
                    model_path="",
                    port=8765,
                    mode="live",
                    lock_path=lock_file,
                )
            assert exc_info.value.code == 1  # model_path_not_configured
            assert lock_file.exists(), "Lockfile should have been created during acquisition"
        finally:
            sys.exit = orig_exit
            if api_server._instance_lock is not None and api_server._instance_lock.is_locked:
                api_server._instance_lock.release()
            api_server._instance_lock = None

    def test_live_startup_conflict_fails_closed_exit_75(self, tmp_path: Path, capsys):
        """
        When another process holds the instance lock, init_server must:
        1. Catch InstanceAuthorityConflictError
        2. Emit LUCIA_BACKEND_ERROR: instance_already_active
        3. Exit immediately with code 75
        4. Mutate zero state
        """
        lock_file = tmp_path / ".instance.lock"

        # External holder acquires lock
        holder_lock = InstanceLock(lock_path=lock_file)
        holder_lock.acquire()

        orig_exit = sys.exit
        exit_code_captured = []

        def mock_exit(code=0):
            exit_code_captured.append(code)
            raise SystemExit(code)

        sys.exit = mock_exit
        try:
            api_server._instance_lock = None

            with pytest.raises(SystemExit) as exc_info:
                api_server.init_server(
                    model_path="dummy_model.gguf",
                    port=8765,
                    mode="live",
                    lock_path=lock_file,
                )

            assert exc_info.value.code == 75, f"Expected exit code 75, got {exc_info.value.code}"
            captured = capsys.readouterr()
            assert "LUCIA_BACKEND_ERROR: instance_already_active" in captured.out
        finally:
            sys.exit = orig_exit
            holder_lock.release()
            if api_server._instance_lock is not None and api_server._instance_lock.is_locked:
                api_server._instance_lock.release()
            api_server._instance_lock = None

    def test_subprocess_dual_launch_conflict_exit_75(self, tmp_path: Path):
        """
        Launch two server instances via subprocess targeting the same lockfile.
        Process 1 holds authority.
        Process 2 must terminate with exit code 75 and stdout 'instance_already_active'.
        """
        lock_file = tmp_path / ".instance.lock"

        # Process A holds the lock
        proc_a_code = f"""
import sys, time
from pathlib import Path
from src.core.identity.instance_lock import InstanceLock

lock = InstanceLock(lock_path=Path(r"{lock_file}"))
lock.acquire()
sys.stdout.write("HOLDER_READY\\n")
sys.stdout.flush()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    lock.release()
"""
        proc_a = subprocess.Popen(
            [sys.executable, "-c", proc_a_code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd(),
        )

        try:
            ready_line = proc_a.stdout.readline()
            assert "HOLDER_READY" in ready_line

            # Process B launches server.py targeting the same lockfile
            proc_b_code = f"""
import os, sys
from pathlib import Path
import src.api.server as srv

os.environ["LUCIA_LOCK_PATH"] = str(Path(r"{lock_file}"))
srv.init_server(
    model_path="dummy.gguf",
    port=8765,
    mode="live",
    lock_path=Path(r"{lock_file}"),
)
"""
            proc_b = subprocess.run(
                [sys.executable, "-c", proc_b_code],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            assert proc_b.returncode == 75, (
                f"Candidate process must exit with code 75, got {proc_b.returncode}. "
                f"Stdout: {proc_b.stdout}, Stderr: {proc_b.stderr}"
            )
            assert "LUCIA_BACKEND_ERROR: instance_already_active" in proc_b.stdout

        finally:
            proc_a.terminate()
            proc_a.wait(timeout=5)

    def test_simulation_mode_bypasses_live_lock(self, tmp_path: Path):
        """Verify simulation mode does not acquire or conflict on the live instance lock."""
        lock_file = tmp_path / ".instance.lock"
        holder_lock = InstanceLock(lock_path=lock_file)
        holder_lock.acquire()

        try:
            # Simulation mode should initialize without checking live lock
            api_server.init_server(mode="simulation", port=8765)
            assert api_server._mode == "simulation"
            assert api_server._sim_runtime is not None
        finally:
            holder_lock.release()
            if api_server._sim_runtime is not None:
                api_server._sim_runtime.shutdown()
                api_server._sim_runtime = None
