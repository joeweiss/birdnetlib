from birdnetlib import (
    Recording,
    MultiProcessRecording,
)
from pathlib import Path
from multiprocessing import Pool, Manager
import multiprocessing
import queue
# from pprint import pprint


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
        overlap=0.0,
        patterns=["*.mp3", "*.wav"],
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


def process_from_queue(shared_queue, results=[], analyzers=None):
    print("process_from_queue")

    try:
        recording_config, analyzer_args = shared_queue.get(timeout=0)
    except queue.Empty:
        # Nothing left in queue, return results.
        return results

    file_path = recording_config["path"]

    # pprint(recording_config)

    if not analyzers:
        # Init the analyzers themselves, pass required kwargs
        analyzers = []
        print("Initializing analyzer(s)")
        for i in analyzer_args:
            if i["model_name"] == "BirdNET-Lite":
                from birdnetlib.analyzer_lite import LiteAnalyzer

                analyzers.append(
                    LiteAnalyzer(custom_species_list_path=i["custom_species_list_path"])
                )
            else:
                from birdnetlib.analyzer import Analyzer

                analyzers.append(
                    Analyzer(
                        custom_species_list_path=i["custom_species_list_path"],
                        classifier_model_path=i["classifier_model_path"],
                        classifier_labels_path=i["classifier_labels_path"],
                    )
                )

    recordings = []
    for analyzer in analyzers:
        try:
            recording = Recording(
                analyzer,
                file_path,
                week_48=recording_config.get("week_48", -1),
                date=recording_config.get("date", None),
                sensitivity=recording_config.get("sensitivity", 1.0),
                lat=recording_config.get("lat", None),
                lon=recording_config.get("lon", None),
                min_conf=recording_config.get("minimum_confidence", 0.1),
                overlap=recording_config.get("overlap", 0.0),
            )
            recording.analyze()
            recordings.append(recording.as_dict)
        except BaseException as error:
            print(recording, error)
            recordings.append(
                {
                    "path": file_path,
                    "config": {},
                    "error": True,
                    "error_message": error,
                    "detections": [],
                    "duration": None,
                }
            )
    results.append(*recordings)
    if not shared_queue.empty():
        process_from_queue(shared_queue, results, analyzers)
    return results


class DirectoryMultiProcessingAnalyzer:
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
        patterns=["*.mp3", "*.wav"],
        processes=None,
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
        self.directory_recordings = []
        self.patterns = patterns
        self.errors = []
        self.exceptions_raised = False
        self.processes = processes
        if not self.processes:
            max_cpus = multiprocessing.cpu_count() - 1
            self.processes = max_cpus

    def on_analyze_complete(self, recording):
        raise NotImplementedError(
            "on_analyze_complete is not implemented in DirectoryMultiProcessingAnalyzer. Use DirectoryAnalyzer instead."
        )

    def on_analyze_file_complete(self, recordings):
        raise NotImplementedError(
            "on_analyze_file_complete is not implemented in DirectoryMultiProcessingAnalyzer. Use DirectoryAnalyzer instead."
        )

    def on_analyze_directory_complete(self, recordings):
        pass

    def on_error(self, recording, exception):
        # If not overridden, raise the exception.
        raise NotImplementedError(
            "on_error is not implemented in DirectoryMultiProcessingAnalyzer. Use DirectoryMultiProcessingAnalyzer.exceptions_raised after completed."
        )

    def recording_preanalyze(self, recording):
        pass

    def process(self):
        patterns = self.patterns
        # print(self.directory)
        files = []
        for pattern in patterns:
            files.extend(Path(self.directory).glob(pattern))

        # print("cpus", multiprocessing.cpu_count())

        max_cpus = multiprocessing.cpu_count() - 1

        with Manager() as manager:
            # create the shared queue
            shared_queue = manager.Queue()

            analyzer_args = [
                {
                    "model_name": i.model_name,
                    "classifier_labels_path": i.classifier_labels_path
                    if hasattr(i, "classifier_labels_path")
                    else None,
                    "classifier_model_path": i.classifier_model_path
                    if hasattr(i, "classifier_model_path")
                    else None,
                    "custom_species_list_path": i.custom_species_list_path,
                }
                for i in self.analyzers
            ]

            for file in files:
                # Run preparsing here, then pass recording config to the process queue
                recording = Recording(
                    None,
                    str(file),
                    week_48=self.week_48,
                    date=self.date,
                    sensitivity=self.sensitivity,
                    lat=self.lat,
                    lon=self.lon,
                    min_conf=self.min_conf,
                    overlap=self.overlap,
                )

                shared_queue.put((recording.__dict__, analyzer_args))

            args = [shared_queue for _ in range(self.processes)]

            with Pool(self.processes) as p:
                # execute the tasks in parallel
                results = p.map(
                    process_from_queue,
                    args,
                )

            # print("All done")

        directory_recordings = []
        for processor_results in results:
            directory_recordings = directory_recordings + processor_results

        for results in directory_recordings:
            # Return as RecordingResults object
            # pprint(
            #     {
            #         "path": results["path"],
            #         "config": results["config"],
            #         "detections": results["detections"],
            #         "error": results.get("error", False),
            #         "error_message": results.get("error_message", None),
            #     }
            # )
            results = MultiProcessRecording(results=results)
            self.directory_recordings.append(results)

        # Look for exceptions.
        self.errors = [i for i in self.directory_recordings if i.error]
        self.exceptions_raised = len(self.errors) != 0

        self.on_analyze_directory_complete(self.directory_recordings)
