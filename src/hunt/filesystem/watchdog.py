import os.path
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileModifiedEvent


class FileWatchdog(FileSystemEventHandler):
    file_path: str
    callback: Callable[..., None]
    _observer: Observer

    def __init__(self, file_path: str, callback: Callable[..., None]):
        self.file_path = os.path.realpath(file_path)
        # https://github.com/python/mypy/issues/708
        self.callback = callback  # type: ignore

        self._observer = Observer()
        self._observer.schedule(event_handler=self, path=os.path.dirname(file_path))

    def start(self) -> None:
        """Start the observer."""
        self._observer.start()

    def join(self) -> None:
        """Wait until the observer thread terminates."""
        self._observer.join()

    def stop(self) -> None:
        """Stop the observer."""
        self._observer.stop()

    def on_modified(self, event: FileSystemEvent) -> None:
        """Invoked when a modified event is generated."""
        if not isinstance(event, FileModifiedEvent) or os.path.realpath(event.src_path) != self.file_path:
            return
        self.callback(self.file_path)
