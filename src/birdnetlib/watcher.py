from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time

from birdnetlib import Recording


class DirectoryWatcher:
    def __init__(self, analyzer, directory):
        self.directory = directory
        self.analyzer = analyzer
        # Init the analyzer
        pass

    def on_analyze_complete(self, recording):
        return recording

    def on_error(self):
        pass

    def _on_created(self, event):
        # Detect for this file.
        print(f"hey, {event.src_path} has been created!")
        minimum_confidence = 0.7

        recording = Recording(
            self.analyzer, event.src_path, min_conf=minimum_confidence
        )
        recording.analyze()
        self.on_analyze_complete(recording)

    def watch(self):
        patterns = ["*.mp3", "*.wav"]
        ignore_patterns = None
        ignore_directories = False
        case_sensitive = True
        my_event_handler = PatternMatchingEventHandler(
            patterns, ignore_patterns, ignore_directories, case_sensitive
        )
        my_event_handler.on_created = self._on_created
        go_recursively = True
        my_observer = Observer()
        my_observer.schedule(my_event_handler, self.directory, recursive=go_recursively)
        my_observer.start()
        print("Starting watcher ...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            my_observer.stop()
            my_observer.join()
