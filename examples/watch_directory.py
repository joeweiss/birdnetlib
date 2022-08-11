from birdnetlib.watcher import DirectoryWatcher
from birdnetlib.analyzer import Analyzer
from pprint import pprint
import shutil
import random
import time


def on_analyze_complete(recording):
    print(recording.path)
    pprint(recording.detections)
    time.sleep(0.1)
    shutil.copyfile(recording.path, f"./examples/{random.randint(0,2000)}.mp3")


print("Starting Analyzer")
analyzer = Analyzer()


watcher = DirectoryWatcher(analyzer, ".")
watcher.on_analyze_complete = on_analyze_complete
watcher.watch()
