from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time
from birdnetlib import Recording


class DirectoryWatcher:
    def __init__(
        self,
        directory,
        analyzers=[],
        week_48=-1,
        date=None,
        sensitivity=1.0,
        lat=None,
        lon=None,
        min_conf=0.1,
    ):
        self.directory = directory
        if len(analyzers) > 0:
            self.analyzers = analyzers
        else:
            from birdnetlib.analyzer_lite import LiteAnalyzer

            self.analyzers = [LiteAnalyzer()]

        # Configuration values for Recording object.
        # Do not norm these values here; let Recording handle them.
        self.week_48 = week_48
        self.date = date
        self.sensitivity = sensitivity
        self.lat = lat
        self.lon = lon
        self.min_conf = min_conf

    def on_analyze_complete(self, recording):
        pass

    def on_analyze_all_complete(self, recordings):
        pass

    def on_error(self, recording, exception):
        # If not overridden, raise the exception.
        raise exception

    def recording_preanalyze(self, recording):
        pass

    def _on_closed(self, event):
        # Detect for this file.
        print(f"New file created: {event.src_path}")
        recordings = []
        for analyzer in self.analyzers:
            try:
                recording = Recording(
                    analyzer,
                    event.src_path,
                    week_48=self.week_48,
                    date=self.date,
                    sensitivity=self.sensitivity,
                    lat=self.lat,
                    lon=self.lon,
                    min_conf=self.min_conf,
                )
                # Preparse if method is available.
                self.recording_preanalyze(recording)
                recording.analyze()
                recordings.append(recording)
                self.on_analyze_complete(recording)
            except BaseException as error:
                self.on_error(recording, error)
        self.on_analyze_all_complete(recordings)

    def watch(self):
        patterns = ["*.mp3", "*.wav"]
        ignore_patterns = None
        ignore_directories = False
        case_sensitive = True
        my_event_handler = PatternMatchingEventHandler(
            patterns, ignore_patterns, ignore_directories, case_sensitive
        )
        my_event_handler.on_closed = self._on_closed
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
