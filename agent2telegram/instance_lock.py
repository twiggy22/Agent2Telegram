"""Prevent two bridge processes from polling the same bot configuration."""
from __future__ import annotations

import hashlib
import os
import fcntl
from pathlib import Path

from .config import config_path, _state_dir


class InstanceAlreadyRunning(RuntimeError):
    """Raised when another bridge already owns this configuration's lock."""


def acquire() -> object:
    """Acquire a per-config process lock and keep its file descriptor open.

    The lock is advisory and released automatically by the kernel when the process exits.
    Different config files therefore remain able to run separate bots concurrently.
    """
    identity = str(config_path().resolve()).encode("utf-8")
    suffix = hashlib.sha256(identity).hexdigest()[:16]
    path = _state_dir() / f"bridge-{suffix}.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise InstanceAlreadyRunning(
            f"another Agent2Telegram bridge is already running for {config_path()}"
        ) from exc
    handle.seek(0)
    handle.truncate()
    handle.write(f"pid={os.getpid()}\n")
    handle.flush()
    return handle
