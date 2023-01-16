import os.path
from typing import Callable

from watchdog.events import FileModifiedEvent, FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class FileWatchdog(FileSystemEventHandler):
    file_path: str
    callback: Callable[..., None]
    _observer: Observer

    def __init__(self, file_path: str, callback: Callable[..., None]):
        """
        Initialize the class.
        :param file_path: the file path to monitor for changes
        :param callback: the callback to invoke when changes are detected
        """
        self.file_path = os.path.realpath(file_path)
        self.callback = callback

        # https://github.com/python/mypy/issues/10757
        self._observer = Observer()  # type: ignore[no-untyped-call]
        self._observer.schedule(event_handler=self, path=os.path.dirname(file_path))  # type: ignore[no-untyped-call]

    def start(self) -> None:
        """Start the observer."""
        # https://github.com/python/mypy/issues/10757
        self._observer.start()  # type: ignore[no-untyped-call]

    def join(self) -> None:
        """Wait until the observer thread terminates."""
        self._observer.join()

    def stop(self) -> None:
        """Stop the observer."""
        # https://github.com/python/mypy/issues/10757
        self._observer.stop()  # type: ignore[no-untyped-call]

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Invoked when a modified event is generated.
        :param event: a watchdog event
        """
        if not isinstance(event, FileModifiedEvent) or os.path.realpath(event.src_path) != self.file_path:
            return
        self.callback(self.file_path)
