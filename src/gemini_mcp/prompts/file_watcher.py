"""
File Watcher for Hot-Reload Support.

This module provides a lightweight, cross-platform file watcher using
os.stat polling. It detects changes to YAML template files and triggers
reload callbacks.

Features:
- Polling-based (no external dependencies like watchdog)
- Configurable poll interval
- Graceful start/stop
- Thread-safe operation
"""

from __future__ import annotations

import logging
import signal
import threading
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class FileWatcher:
    """
    Lightweight file watcher using os.stat polling.

    Usage:
        watcher = FileWatcher(
            directories=[Path("./templates")],
            callback=on_file_change,
            poll_interval=2.0,
        )
        watcher.start()
        # ... later ...
        watcher.stop()

    The watcher runs in a daemon thread and will automatically stop
    when the main program exits.
    """

    def __init__(
        self,
        directories: List[Path],
        callback: Callable[[Path], None],
        poll_interval: float = 2.0,
        file_patterns: Optional[List[str]] = None,
    ):
        """
        Initialize the file watcher.

        Args:
            directories: List of directories to watch.
            callback: Function called when a file changes.
                     Receives the Path of the changed file.
            poll_interval: Seconds between file modification checks.
            file_patterns: Glob patterns to watch (default: ["*.yaml"]).
        """
        self._directories = [Path(d) for d in directories]
        self._callback = callback
        self._poll_interval = poll_interval
        self._file_patterns = file_patterns or ["*.yaml"]

        # File modification times: path -> mtime
        self._file_mtimes: Dict[Path, float] = {}

        # Known files for detecting new files
        self._known_files: Set[Path] = set()

        # Threading control
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Signal handler registration
        self._original_sighup_handler: Optional[Callable] = None

        logger.debug(
            f"FileWatcher initialized for directories: {self._directories}, "
            f"patterns: {self._file_patterns}, "
            f"poll_interval: {self._poll_interval}s"
        )

    def start(self) -> None:
        """
        Start watching files in a background thread.

        Safe to call multiple times (will only start once).
        """
        if self._running:
            logger.debug("FileWatcher already running")
            return

        self._running = True
        self._stop_event.clear()

        # Initial scan to populate file mtimes
        self._scan_files()

        # Start polling thread
        self._thread = threading.Thread(
            target=self._poll_loop,
            name="FileWatcher",
            daemon=True,  # Automatically stops when main program exits
        )
        self._thread.start()

        # Register SIGHUP handler for manual reload trigger
        self._register_signal_handler()

        logger.info("FileWatcher started")

    def stop(self) -> None:
        """
        Stop the file watcher gracefully.

        Waits for the polling thread to finish before returning.
        """
        if not self._running:
            return

        self._running = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self._poll_interval + 1)

        self._thread = None
        self._restore_signal_handler()

        logger.info("FileWatcher stopped")

    def _poll_loop(self) -> None:
        """Main polling loop that checks for file changes."""
        while self._running and not self._stop_event.is_set():
            try:
                self._check_changes()
            except Exception as e:
                logger.error(f"Error in FileWatcher poll loop: {e}")

            # Wait with interruptible sleep
            self._stop_event.wait(timeout=self._poll_interval)

    def _scan_files(self) -> None:
        """Scan directories and populate initial file modification times."""
        for directory in self._directories:
            if not directory.exists():
                logger.warning(f"Watch directory does not exist: {directory}")
                continue

            for pattern in self._file_patterns:
                for file_path in directory.glob(pattern):
                    if file_path.is_file():
                        try:
                            mtime = file_path.stat().st_mtime
                            self._file_mtimes[file_path] = mtime
                            self._known_files.add(file_path)
                        except OSError as e:
                            logger.warning(f"Cannot stat {file_path}: {e}")

        logger.debug(f"Initial scan found {len(self._file_mtimes)} files")

    def _check_changes(self) -> None:
        """Check all watched files for modifications."""
        current_files: Set[Path] = set()
        changed_files: List[Path] = []

        for directory in self._directories:
            if not directory.exists():
                continue

            for pattern in self._file_patterns:
                for file_path in directory.glob(pattern):
                    if not file_path.is_file():
                        continue

                    current_files.add(file_path)

                    try:
                        current_mtime = file_path.stat().st_mtime
                    except OSError:
                        # File may have been deleted between glob and stat
                        continue

                    # Check for modification
                    if file_path in self._file_mtimes:
                        if current_mtime > self._file_mtimes[file_path]:
                            changed_files.append(file_path)
                            logger.debug(f"File modified: {file_path}")
                    else:
                        # New file detected
                        logger.debug(f"New file detected: {file_path}")
                        changed_files.append(file_path)

                    self._file_mtimes[file_path] = current_mtime

        # Check for deleted files
        deleted_files = self._known_files - current_files
        for deleted in deleted_files:
            logger.debug(f"File deleted: {deleted}")
            self._file_mtimes.pop(deleted, None)
            # Note: We don't trigger callback for deleted files
            # The loader will handle FileNotFoundError on next access

        self._known_files = current_files

        # Trigger callbacks for changed/new files
        for changed_file in changed_files:
            self._trigger_callback(changed_file)

    def _trigger_callback(self, file_path: Path) -> None:
        """Safely trigger the callback for a changed file."""
        try:
            self._callback(file_path)
        except Exception as e:
            logger.error(f"Error in file change callback for {file_path}: {e}")

    def _register_signal_handler(self) -> None:
        """
        Register SIGHUP handler for manual reload trigger.

        On Unix systems, sending SIGHUP to the process will trigger
        a reload of all watched files.
        """
        try:
            self._original_sighup_handler = signal.getsignal(signal.SIGHUP)
            signal.signal(signal.SIGHUP, self._handle_sighup)
            logger.debug("SIGHUP handler registered for manual reload")
        except (AttributeError, ValueError, OSError):
            # Not on a Unix system or in a thread that can't handle signals
            # AttributeError: signal.SIGHUP doesn't exist on Windows
            logger.debug("SIGHUP handler not available on this platform")

    def _restore_signal_handler(self) -> None:
        """Restore the original SIGHUP handler."""
        try:
            if self._original_sighup_handler is not None:
                signal.signal(signal.SIGHUP, self._original_sighup_handler)
                self._original_sighup_handler = None
        except (AttributeError, ValueError, OSError):
            # AttributeError: signal.SIGHUP doesn't exist on Windows
            pass

    def _handle_sighup(self, signum: int, frame) -> None:
        """
        Handle SIGHUP signal for manual reload.

        Usage: kill -HUP <pid>
        """
        logger.info("Received SIGHUP, triggering manual reload")

        # Trigger callback for all known files
        for file_path in list(self._known_files):
            self._trigger_callback(file_path)

    def add_directory(self, directory: Path) -> None:
        """
        Add a new directory to watch.

        The directory will be scanned immediately.
        """
        directory = Path(directory)
        if directory not in self._directories:
            self._directories.append(directory)
            logger.info(f"Added watch directory: {directory}")

            # Scan the new directory
            if self._running:
                self._scan_files()

    def remove_directory(self, directory: Path) -> None:
        """Remove a directory from watching."""
        directory = Path(directory)
        if directory in self._directories:
            self._directories.remove(directory)

            # Remove files from this directory
            to_remove = [f for f in self._known_files if f.parent == directory]
            for f in to_remove:
                self._known_files.discard(f)
                self._file_mtimes.pop(f, None)

            logger.info(f"Removed watch directory: {directory}")

    def get_watched_files(self) -> List[Path]:
        """Get list of currently watched files."""
        return list(self._known_files)

    @property
    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        return self._running


class DebounceWrapper:
    """
    Wrapper that debounces file change callbacks.

    Useful when editors make multiple writes for a single save
    (e.g., write to temp file, then rename).
    """

    def __init__(
        self,
        callback: Callable[[Path], None],
        delay: float = 0.5,
    ):
        """
        Initialize debounce wrapper.

        Args:
            callback: The actual callback to call after debounce.
            delay: Seconds to wait before calling callback.
        """
        self._callback = callback
        self._delay = delay
        self._pending: Dict[Path, threading.Timer] = {}
        self._lock = threading.Lock()

    def __call__(self, file_path: Path) -> None:
        """Handle a file change with debouncing."""
        with self._lock:
            # Cancel any pending callback for this file
            if file_path in self._pending:
                self._pending[file_path].cancel()

            # Schedule new callback
            timer = threading.Timer(self._delay, self._fire, args=[file_path])
            self._pending[file_path] = timer
            timer.start()

    def _fire(self, file_path: Path) -> None:
        """Actually trigger the callback after debounce delay."""
        with self._lock:
            self._pending.pop(file_path, None)

        try:
            self._callback(file_path)
        except Exception as e:
            logger.error(f"Error in debounced callback for {file_path}: {e}")

    def cancel_all(self) -> None:
        """Cancel all pending callbacks."""
        with self._lock:
            for timer in self._pending.values():
                timer.cancel()
            self._pending.clear()
