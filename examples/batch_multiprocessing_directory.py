from birdnetlib.batch import DirectoryMultiProcessingAnalyzer
from birdnetlib.analyzer import Analyzer
from datetime import datetime
from pprint import pprint


def on_analyze_directory_complete(recordings):
    print("-" * 80)
    print("directory_completed: recordings processed ", len(recordings))
    print("-" * 80)

    for recording in recordings:
        print(recording.path)
        if recording.error:
            print("Error: ", recording.error_message)
        else:
            pprint(recording.detections)

        print("-" * 80)


analyzer = Analyzer()

directory = "."
batch = DirectoryMultiProcessingAnalyzer(
    directory,
    analyzers=[analyzer],
    lon=-120.7463,
    lat=35.4244,
    date=datetime(year=2022, month=5, day=10),
    min_conf=0.4,
)

batch.on_analyze_directory_complete = on_analyze_directory_complete
batch.process()
