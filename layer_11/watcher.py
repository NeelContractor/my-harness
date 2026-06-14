# layer_11/watcher.py
import os
import threading
from typing import Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

IGNORE_SUFFIXES = (
    ".review.md", ".summary.md", ".suggestions.md",
    ".description.md", ".analysis.md", ".notes.md",
    ".pyc", ".DS_Store", "__pycache__"
)

IGNORE_PREFIXES = (".", "_")
DEBOUNCE_SECONDS = 2.0


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, on_change: Callable[[str], None]):
        super().__init__()
        self.on_change = on_change
        self._timers: dict[str, threading.Timer] = {}

    def _should_ignore(self, path: str) -> bool:
        filename = os.path.basename(path)
        if any(filename.endswith(s) for s in IGNORE_SUFFIXES):
            return True
        if any(filename.startswith(p) for p in IGNORE_PREFIXES):
            return True
        if "__pycache__" in path:
            return True
        return False

    def _normalize_path(self, path: str | bytes) -> str:
        """Ensure path is always a str."""
        if isinstance(path, bytes):
            return path.decode("utf-8")
        return path

    def _debounced_react(self, path: str):
        if path in self._timers:
            self._timers[path].cancel()
        timer = threading.Timer(DEBOUNCE_SECONDS, self._trigger, args=[path])
        self._timers[path] = timer
        timer.start()

    def _trigger(self, path: str):
        self._timers.pop(path, None)
        if os.path.exists(path):
            self.on_change(path)

    def on_created(self, event):
        if event.is_directory:
            return
        path = self._normalize_path(event.src_path)
        if not self._should_ignore(path):
            print(f"\n  📁 New file detected: {path}")
            self._debounced_react(path)

    def on_modified(self, event):
        if event.is_directory:
            return
        path = self._normalize_path(event.src_path)
        if not self._should_ignore(path):
            print(f"\n  ✏️  File modified: {path}")
            self._debounced_react(path)


class FileWatcher:
    def __init__(self, watch_dir: str, on_change: Callable[[str], None]):
        self.watch_dir = watch_dir
        self.on_change = on_change
        self.handler = ChangeHandler(on_change)
        self.observer = Observer()

    def start(self):
        self.observer.schedule(self.handler, self.watch_dir, recursive=True)
        self.observer.start()
        print(f"  👁️  Watching: {self.watch_dir}")

    def stop(self):
        self.observer.stop()
        self.observer.join()