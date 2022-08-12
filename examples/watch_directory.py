from birdnetlib.watcher import DirectoryWatcher
from birdnetlib.analyzer_lite import LiteAnalyzer
from pprint import pprint


def on_analyze_complete(recording):
    print(recording.path)
    pprint(recording.detections)


def on_error(recording, error):
    print("An exception occurred: {}".format(error))
    print(recording.path)


print("Starting Analyzer")
analyzer = LiteAnalyzer()


print("Starting Watcher")
directory = "."
watcher = DirectoryWatcher(
    directory, analyzer=analyzer, lon=-120.7463, lat=35.4244, week=18, min_conf=0.4
)

watcher.on_analyze_complete = on_analyze_complete
watcher.on_error = on_error
watcher.watch()
