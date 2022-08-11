from birdnetlib.watcher import DirectoryWatcher
import os


def on_analyze_complete(recording):
    print(recording.detections)


def test_watcher():
    assert True == True

    # test_dir = os.path.join(os.path.dirname(__file__), "test_files")

    # watch = DirectoryWatcher(None, test_dir)
    # watch.on_analyze_complete = on_analyze_complete

    # watch.