from pathlib import Path
from typing import Callable

from watchdog.events import FileModifiedEvent, FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class FileWatchdog(FileSystemEventHandler):
    file_path: Path
    callback: Callable[..., None]
    _observer: Observer   # type: ignore[valid-type]

    def __init__(self, file_path: Path, callback: Callable[..., None]):
        """
        Initialize the class.
        :param file_path: the file path to monitor for changes
        :param callback: the callback to invoke when changes are detected
        """
        self.file_path = file_path
        self.callback = callback

        self._observer = Observer()
        self._observer.schedule(event_handler=self, path=file_path.parent)   # type: ignore[no-untyped-call]

    def start(self) -> None:
        """Start the observer."""
        self._observer.start()  # type: ignore[attr-defined]

    def join(self) -> None:
        """Wait until the observer thread terminates."""
        self._observer.join()  # type: ignore[attr-defined]

    def stop(self) -> None:
        """Stop the observer."""
        self._observer.stop()  # type: ignore[attr-defined]

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Invoked when a modified event is generated.
        :param event: a watchdog event
        """
        if not isinstance(event, FileModifiedEvent) or Path(event.src_path) != self.file_path:
            return
        self.callback(self.file_path)
