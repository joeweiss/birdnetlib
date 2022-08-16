from birdnetlib.watcher import DirectoryWatcher
from birdnetlib.analyzer_lite import LiteAnalyzer
from birdnetlib.analyzer import Analyzer
from datetime import datetime
from pprint import pprint


def on_analyze_complete(recording):
    print("on_analyze_complete")
    # Each analyzation as it is completed.
    print(recording.path, recording.analyzer.name)
    pprint(recording.detections)


def on_analyze_all_complete(recording_list):
    print("---------------------------")
    print("on_analyze_all_complete")
    print("---------------------------")
    # All analyzations are completed. Results passed as a list of Recording objects.
    for recording in recording_list:
        print(recording.path, recording.analyzer.name)
        pprint(recording.detections)
        print("---------------------------")


def on_error(recording, error):
    print("An exception occurred: {}".format(error))
    print(recording.path)


print("Starting Analyzers")
analyzer_lite = LiteAnalyzer()
analyzer = Analyzer()


print("Starting Watcher")
directory = "."
watcher = DirectoryWatcher(
    directory,
    analyzers=[analyzer, analyzer_lite],
    lon=-120.7463,
    lat=35.4244,
    date=datetime(year=2022, month=5, day=10),
    min_conf=0.4,
)

watcher.on_analyze_complete = on_analyze_complete
watcher.on_analyze_all_complete = on_analyze_all_complete
watcher.on_error = on_error
watcher.watch()
