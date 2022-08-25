from birdnetlib import Recording
from pathlib import Path


class DirectoryAnalyzer:
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
        patterns=["*.mp3", "*.wav"],
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
        self.directory_recordings = []
        self.patterns = patterns

    def on_analyze_complete(self, recording):
        pass

    def on_analyze_file_complete(self, recordings):
        pass

    def on_analyze_directory_complete(self, recordings):
        pass

    def on_error(self, recording, exception):
        # If not overridden, raise the exception.
        raise exception

    def recording_preanalyze(self, recording):
        pass

    def process_file(self, path):
        # Detect for this file.
        recordings = []
        for analyzer in self.analyzers:
            try:
                recording = Recording(
                    analyzer,
                    path,
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
        self.on_analyze_file_complete(recordings)
        self.directory_recordings.extend(recordings)

    def process(self):
        patterns = self.patterns
        # print(self.directory)
        files = []
        for pattern in patterns:
            files.extend(Path(self.directory).glob(pattern))
        # print(files)
        for file in files:
            self.process_file(str(file))

        self.on_analyze_directory_complete(self.directory_recordings)
