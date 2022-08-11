from birdnetlib.watcher import DirectoryWatcher
from birdnetlib.analyzer_lite import LiteAnalyzer
from pprint import pprint


def on_analyze_complete(recording):
    print(recording.path)
    pprint(recording.detections)


print("Starting Analyzer")
analyzer = LiteAnalyzer()

print("Starting Watcher")
watcher = DirectoryWatcher(
    analyzer, ".", lon=-120.7463, lat=35.4244, week=18, min_conf=0.4
)
watcher.on_analyze_complete = on_analyze_complete
watcher.watch()
