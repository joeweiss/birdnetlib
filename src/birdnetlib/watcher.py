from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time
from birdnetlib.exceptions import AudioFormatError

from birdnetlib import Recording

class DirectoryWatcher:
    def __init__(
        self,
        directory,
        analyzer=None,
        week=-1,
        sensitivity=1.0,
        lat=None,
        lon=None,
        min_conf=0.1,
    ):
        self.directory = directory
        if analyzer:
            self.analyzer = analyzer
        else:
            from birdnetlib.analyzer_lite import LiteAnalyzer
            self.analyzer = LiteAnalyzer()

        # Configuration values for Recording object.
        # Do not norm these values here; let Recording handle them.
        self.week = week
        self.sensitivity = sensitivity
        self.lat = lat
        self.lon = lon
        self.min_conf = min_conf

    def on_analyze_complete(self, recording):
        pass

    def on_error(self, recording, exception):
        # If not overridden, raise the exception.
        raise exception

    def _on_created(self, event):
        # Detect for this file.
        print(f"New file created: {event.src_path}")

        try:
            recording = Recording(
                self.analyzer,
                event.src_path,
                week=self.week,
                sensitivity=self.sensitivity,
                lat=self.lat,
                lon=self.lon,
                min_conf=self.min_conf,
            )
            recording.analyze()
            self.on_analyze_complete(recording)
        except BaseException as error:
            self.on_error(recording, error)

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
