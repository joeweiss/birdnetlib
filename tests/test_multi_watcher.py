from birdnetlib.watcher import DirectoryWatcher
from birdnetlib.analyzer_lite import LiteAnalyzer
from birdnetlib.analyzer import Analyzer
import os
from collections import namedtuple
from mock import patch, Mock


def test_watcher_complete():
    analyzer = Analyzer()
    analyzer_lite = LiteAnalyzer()

    directory = "."
    watcher = DirectoryWatcher(directory, analyzers=[analyzer, analyzer_lite])

    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    # Add a mocked call for on_analyze_complete
    watcher.on_analyze_complete = Mock()
    watcher.on_analyze_all_complete = Mock()

    # Create a "file-created" event in the watcher.
    # Test calling private method directly (this would be called by watchdog)
    event = namedtuple("Event", "src_path")
    event.src_path = input_path
    watcher._on_closed(event)

    # Check complete call count and results.
    assert watcher.on_analyze_complete.call_count == 2
    analyzer_recording = watcher.on_analyze_complete.call_args_list[0][0][0]
    lite_recording = watcher.on_analyze_complete.call_args_list[1][0][0]

    assert len(analyzer_recording.detections) == 31
    assert analyzer_recording.analyzer.name == "Analyzer"
    assert len(lite_recording.detections) == 2
    assert lite_recording.analyzer.name == "LiteAnalyzer"

    assert watcher.on_analyze_all_complete.call_count == 1
    assert len(watcher.on_analyze_all_complete.call_args.args[0]) == 2


def test_watcher_error():
    analyzer = LiteAnalyzer()
    directory = "."
    watcher = DirectoryWatcher(directory, analyzers=[analyzer])

    # Not an mp3 file, should throw error.
    input_path = os.path.join(os.path.dirname(__file__), "test_files/species_list.txt")

    # Add a mocked call for on_analyze_complete
    watcher.on_error = Mock()

    # Create a "file-created" event in the watcher.
    # Normally a txt would never make it this far,
    # but we're just testing to see if error is thrown.
    event = namedtuple("Event", "src_path")
    event.src_path = input_path
    watcher._on_closed(event)

    # Check complete call count and results.
    assert watcher.on_error.call_count == 1
    assert type(watcher.on_error.call_args.args[0]).__name__ == "Recording"
    assert type(watcher.on_error.call_args.args[1]).__name__ == "AudioFormatError"


def test_default_analyzer():

    # Test that if an analyzer isn't provided, that the LiteAnalyzer is used.

    directory = "."
    watcher = DirectoryWatcher(directory)
    assert type(watcher.analyzers[0]).__name__ == "LiteAnalyzer"
