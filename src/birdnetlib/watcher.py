from collections import namedtuple
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time
from birdnetlib import Recording
import glob
import os
from time import sleep
import hashlib


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
        overlap=0.0,
        use_polling=False,
    ):
        self.directory = directory
        if len(analyzers) > 0:
            self.analyzers = analyzers
        else:
            from birdnetlib.analyzer import Analyzer

            self.analyzers = [Analyzer()]

        # Configuration values for Recording object.
        # Do not norm these values here; let Recording handle them.
        self.week_48 = week_48
        self.date = date
        self.sensitivity = sensitivity
        self.lat = lat
        self.lon = lon
        self.min_conf = min_conf
        self.overlap = overlap
        self.use_polling = use_polling

    def on_analyze_complete(self, recording):
        pass

    def on_analyze_file_complete(self, recordings):
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
                    overlap=self.overlap,
                )
                # Preparse if method is available.
                self.recording_preanalyze(recording)
                recording.analyze()
                recordings.append(recording)
                self.on_analyze_complete(recording)
            except BaseException as error:
                self.on_error(recording, error)
        self.on_analyze_file_complete(recordings)

    def watch(self):
        if self.use_polling:
            self.watch_via_polling()  # Doesn't return.
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

    def return_file_list(self):
        patterns = ["*.mp3", "*.wav"]
        files = []
        for ext in patterns:
            files.extend(glob.glob(os.path.join(self.directory, ext)))
        files.sort()
        return files

    def get_file_md5(self, filepath):
        with open(filepath, "rb") as file:
            file_contents = file.read()
            return hashlib.md5(file_contents).hexdigest()
        return False

    def watch_via_polling(self):
        seen_files = self.return_file_list()
        last_hash = ""
        while True:
            new_files = self.return_file_list()
            files = [x for x in new_files if x not in seen_files]
            if len(files) > 0:
                path = os.path.join(self.directory, files[0])
                h = self.get_file_md5(path)
                # Compare file hash to last hash (to confirm file is not being recorded)
                # Clumsy, but works as a fallback to watchdog.
                if h and h == last_hash:
                    Event = namedtuple("Event", ["src_path"])
                    event = Event(path)
                    self._on_closed(event)
                    seen_files.append(files[0])
                    # Remove any seen_files no longer in directory.
                    current_list = self.return_file_list()
                    seen_files = [x for x in seen_files if x in current_list]
                else:
                    last_hash = h
            sleep(2)
