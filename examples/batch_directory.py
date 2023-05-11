from birdnetlib.batch import DirectoryAnalyzer
from birdnetlib.analyzer import Analyzer
from datetime import datetime
from pprint import pprint


def on_analyze_complete(recording):
    print(recording.path)
    pprint(recording.detections)


def on_error(recording, error):
    print("An exception occurred: {}".format(error))
    print(recording.path)


print("Starting Analyzer")
analyzer = Analyzer()


print("Starting Watcher")
directory = "."
batch = DirectoryAnalyzer(
    directory,
    analyzers=[analyzer],
    lon=-120.7463,
    lat=35.4244,
    date=datetime(year=2022, month=5, day=10),
    min_conf=0.4,
)

batch.on_analyze_complete = on_analyze_complete
batch.on_error = on_error
batch.process()
