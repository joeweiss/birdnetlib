from birdnetlib.watcher import DirectoryWatcher
from birdnetlib.analyzer_lite import LiteAnalyzer
import os
from collections import namedtuple
from mock import patch, Mock


def on_analyze_complete(recording):
    print(recording.detections)


def test_watcher_complete():
    analyzer = LiteAnalyzer()
    directory = "."
    watcher = DirectoryWatcher(directory, analyzer=analyzer)

    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    # Add a mocked call for on_analyze_complete
    watcher.on_analyze_complete = Mock()

    # Create a "file-created" event in the watcher.
    # Test calling private method directly (this would be called by watchdog)
    event = namedtuple("Event", "src_path")
    event.src_path = input_path
    watcher._on_created(event)

    # Check complete call count and results.
    assert watcher.on_analyze_complete.call_count == 1
    detections = watcher.on_analyze_complete.call_args.args[0].detections
    assert len(detections) == 2


def test_watcher_error():
    analyzer = LiteAnalyzer()
    directory = "."
    watcher = DirectoryWatcher(directory, analyzer=analyzer)

    # Not an mp3 file, should throw error.
    input_path = os.path.join(os.path.dirname(__file__), "test_files/species_list.txt")

    # Add a mocked call for on_analyze_complete
    watcher.on_error = Mock()

    # Create a "file-created" event in the watcher.
    # Normally a txt would never make it this far,
    # but we're just testing to see if error is thrown.
    event = namedtuple("Event", "src_path")
    event.src_path = input_path
    watcher._on_created(event)

    # Check complete call count and results.
    assert watcher.on_error.call_count == 1
    assert type(watcher.on_error.call_args.args[0]).__name__ == "Recording"
    assert type(watcher.on_error.call_args.args[1]).__name__ == "AudioFormatError"


def test_default_analyzer():

    # Test that if an analyzer isn't provided, that the LiteAnalyzer is used.

    directory = "."
    watcher = DirectoryWatcher(directory)
    assert type(watcher.analyzer).__name__ == "LiteAnalyzer"
