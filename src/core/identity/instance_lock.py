"""
Instance Authority & Kernel File Lock (WP-01).

Governing ADR: ADR-034 (Identity Authority, Instance Exclusivity & Anti-Branching Boundary).
Reference: docs/others/IDENTITY_AUTHORITY_SPECIFICATION/IDENTITY_AUTHORITY_SPEC_V01.md

This module implements exclusive single-writer authority over a Lucia identity workspace.
At any physical moment in time, exactly ONE operating system process may hold write
authority over the workspace.

Mechanism:
- Windows (nt): msvcrt.locking(fd, msvcrt.LK_NBLCK, 1) on byte 0
- POSIX: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

Properties:
- Non-blocking acquisition (target latency <= 5 ms)
- Fail-closed on conflict via InstanceAuthorityConflictError
- Non-inheritable file descriptor (O_NOINHERIT / O_CLOEXEC, os.set_inheritable(False))
- Kernel-lifecycle bound: normal exit or crash/forced kill releases lock automatically
- Zero stale-lock cleanup scripts: authority is derived from active OS kernel lock state,
  never from presence or contents of the lockfile alone.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import sys
import threading
import time
from typing import Optional, Set, Union

logger = logging.getLogger("lucia.identity.instance_lock")

DEFAULT_LOCK_PATH = Path("data/.instance.lock")

# Process-level registry to prevent in-process multi-instance collision
_HELD_LOCKS_GUARD = threading.Lock()
_HELD_LOCKS: Set[str] = set()


class InstanceAuthorityConflictError(RuntimeError):
    """
    Raised when instance authority cannot be acquired because another
    operating system process (or concurrent runtime) already holds write
    authority over the workspace.
    """

    def __init__(
        self,
        lock_path: Union[Path, str],
        message: Optional[str] = None,
        pid: Optional[int] = None,
    ) -> None:
        self.lock_path = Path(lock_path)
        self.pid = pid
        if message is None:
            message = (
                f"Instance authority conflict: Workspace lock '{self.lock_path}' is already "
                "held by another active process. Failing closed to prevent split-brain "
                "identity state divergence."
            )
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return f"InstanceAuthorityConflictError(lock_path={str(self.lock_path)!r})"


class InstanceLock:
    """
    Manages process-lifetime exclusive instance authority via OS kernel file lock.

    Guarantees that exactly one process holds write authority over the target
    Lucia workspace directory at any time.
    """

    def __init__(
        self,
        lock_path: Optional[Union[Path, str]] = None,
        workspace_dir: Optional[Union[Path, str]] = None,
    ) -> None:
        """
        Initialize InstanceLock for a specific lock path or workspace directory.

        Args:
            lock_path: Exact path to .instance.lock. If provided, takes precedence.
            workspace_dir: Parent directory (e.g., 'data'). Lock will be workspace_dir / '.instance.lock'.
                           If neither is provided, defaults to DEFAULT_LOCK_PATH ('data/.instance.lock').
        """
        if lock_path is not None:
            self.lock_path = Path(lock_path)
        elif workspace_dir is not None:
            self.lock_path = Path(workspace_dir) / ".instance.lock"
        else:
            self.lock_path = DEFAULT_LOCK_PATH

        self._fd: Optional[int] = None
        self._is_locked: bool = False
        self._acquired_at: Optional[float] = None
        self._acquisition_latency_ms: Optional[float] = None
        self._pid: Optional[int] = None
        self._canonical_path: str = ""

    @property
    def is_locked(self) -> bool:
        """Return True if this instance currently holds the kernel file lock."""
        return self._is_locked

    @property
    def acquired_at(self) -> Optional[float]:
        """Return timestamp when lock was acquired, or None if not locked."""
        return self._acquired_at

    @property
    def acquisition_latency_ms(self) -> Optional[float]:
        """Return measured lock acquisition latency in milliseconds, or None."""
        return self._acquisition_latency_ms

    @property
    def pid(self) -> Optional[int]:
        """Return process ID that acquired this lock, or None if not locked."""
        return self._pid

    def acquire(self) -> None:
        """
        Attempt non-blocking acquisition of the exclusive instance lock.

        Raises:
            RuntimeError: If this InstanceLock instance is already holding the lock.
            InstanceAuthorityConflictError: If another process or runtime already holds the lock.
            OSError: If an unexpected OS error occurs (e.g. read-only filesystem).
        """
        if self._is_locked:
            raise RuntimeError(
                f"Instance authority is already held by this InstanceLock object for '{self.lock_path}'."
            )

        # Ensure parent directory exists
        resolved_path = self.lock_path.resolve()
        canonical_str = str(resolved_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)

        # Check in-process registration to prevent same-process multi-instance collision
        with _HELD_LOCKS_GUARD:
            if canonical_str in _HELD_LOCKS:
                logger.warning(
                    "Instance authority conflict in process: Lock '%s' already held by another object.",
                    self.lock_path,
                )
                raise InstanceAuthorityConflictError(
                    lock_path=self.lock_path,
                    message=(
                        f"Instance authority conflict: Lock '{self.lock_path}' is already held "
                        "within this process."
                    ),
                )

        t_start = time.perf_counter()
        fd: Optional[int] = None

        try:
            if sys.platform == "win32":
                fd = self._acquire_windows(resolved_path)
            else:
                fd = self._acquire_posix(resolved_path)
        except (BlockingIOError, PermissionError) as exc:
            if fd is not None:
                try:
                    os.close(fd)
                except Exception:
                    pass
            logger.warning(
                "Instance authority acquisition rejected: %s on '%s'. Another process is active.",
                type(exc).__name__,
                self.lock_path,
            )
            raise InstanceAuthorityConflictError(lock_path=self.lock_path) from exc
        except OSError as exc:
            if fd is not None:
                try:
                    os.close(fd)
                except Exception:
                    pass
            # Errno 11 (EAGAIN/EWOULDBLOCK) or Errno 13 (EACCES/Permission denied)
            if exc.errno in (11, 13) or getattr(exc, "winerror", None) in (32, 33):
                logger.warning(
                    "Instance authority conflict (OSError %s): Lock '%s' is locked by another process.",
                    exc.errno,
                    self.lock_path,
                )
                raise InstanceAuthorityConflictError(lock_path=self.lock_path) from exc
            logger.exception("Unexpected OS error acquiring instance lock '%s': %s", self.lock_path, exc)
            raise

        t_end = time.perf_counter()
        self._acquisition_latency_ms = (t_end - t_start) * 1000.0
        self._fd = fd
        self._is_locked = True
        self._acquired_at = time.time()
        self._pid = os.getpid()
        self._canonical_path = canonical_str

        with _HELD_LOCKS_GUARD:
            _HELD_LOCKS.add(canonical_str)

        # Write diagnostic metadata into the lock file
        self._write_diagnostic_payload()

        logger.info(
            "Instance authority acquired on '%s' (PID=%d, latency=%.3f ms).",
            self.lock_path,
            self._pid,
            self._acquisition_latency_ms,
        )

    def _acquire_windows(self, path: Path) -> int:
        """Acquire non-blocking kernel lock on Windows using msvcrt."""
        import msvcrt

        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOINHERIT", 0)
        fd = os.open(str(path), flags, 0o600)
        try:
            os.set_inheritable(fd, False)
        except Exception:
            pass

        # Lock 1 byte at offset 0 without blocking
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        return fd

    def _acquire_posix(self, path: Path) -> int:
        """Acquire non-blocking kernel lock on POSIX using fcntl.flock."""
        import fcntl

        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_CLOEXEC", 0)
        fd = os.open(str(path), flags, 0o600)
        try:
            os.set_inheritable(fd, False)
        except Exception:
            pass

        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd

    def _write_diagnostic_payload(self) -> None:
        """
        Write non-authoritative diagnostic telemetry into the lockfile.
        NOTE: Authority is NEVER inferred from this payload. It exists purely
        for diagnostic observation.
        """
        if self._fd is None:
            return
        try:
            payload = {
                "pid": self._pid,
                "acquired_at": datetime.now(timezone.utc).isoformat(),
                "acquired_epoch": self._acquired_at,
                "latency_ms": self._acquisition_latency_ms,
                "platform": sys.platform,
            }
            raw_bytes = json.dumps(payload, indent=2).encode("utf-8")
            os.ftruncate(self._fd, 0)
            os.lseek(self._fd, 0, os.SEEK_SET)
            os.write(self._fd, raw_bytes)
            os.fsync(self._fd)
        except Exception as exc:
            # Metadata writing failure must not compromise the kernel lock
            logger.debug("Failed to write diagnostic payload to lock file: %s", exc)

    def release(self) -> None:
        """
        Release the instance lock and close the file descriptor.

        Does NOT delete the lockfile from disk, adhering to the invariant:
        'Zero stale-lock cleanup scripts; authority depends on OS lock state.'
        """
        if not self._is_locked:
            return

        with _HELD_LOCKS_GUARD:
            _HELD_LOCKS.discard(self._canonical_path)

        fd = self._fd
        self._fd = None
        self._is_locked = False
        self._acquired_at = None
        self._pid = None

        if fd is not None:
            try:
                if sys.platform == "win32":
                    import msvcrt

                    os.lseek(fd, 0, os.SEEK_SET)
                    try:
                        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                    except OSError:
                        pass
                else:
                    import fcntl

                    try:
                        fcntl.flock(fd, fcntl.LOCK_UN)
                    except OSError:
                        pass
            finally:
                try:
                    os.close(fd)
                except Exception:
                    pass

        logger.info("Instance authority released on '%s'.", self.lock_path)

    def __enter__(self) -> InstanceLock:
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()

    def __del__(self) -> None:
        try:
            if self._is_locked:
                self.release()
        except Exception:
            pass
