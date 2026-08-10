from birdnetlib.watcher import DirectoryWatcher
from birdnetlib.analyzer import Analyzer
from birdnetlib.analyzer_lite import LiteAnalyzer
import os
from collections import namedtuple
from mock import patch, Mock
import pytest
from datetime import datetime

_skip_lite = pytest.mark.skip(reason="BirdNET-Lite model requires TFLite Flex delegate (FlexRFFT); model is deprecated")


def on_analyze_complete(recording):
    print(recording.detections)


@_skip_lite
def test_watcher_complete():
    analyzer = LiteAnalyzer()
    directory = "."
    watcher = DirectoryWatcher(directory, analyzers=[analyzer])

    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    # Add a mocked call for on_analyze_complete
    watcher.on_analyze_complete = Mock()

    # Create a "file-created" event in the watcher.
    # Test calling private method directly (this would be called by watchdog)
    event = namedtuple("Event", "src_path")
    event.src_path = input_path
    watcher._on_closed(event)

    # Check complete call count and results.
    assert watcher.on_analyze_complete.call_count == 1
    detections = watcher.on_analyze_complete.call_args.args[0].detections
    assert len(detections) == 2


def preparser(recording):
    # Used to modify the recording object before analyzing.
    filename = recording.filename
    # 2022-08-15-21-05-51.wav, as an example, a file containing the datetime.
    dt = datetime.strptime(filename, "%Y-%m-%d-%H-%M-%S.wav")
    # Modify the recording object here as needed.
    # For testing, we're changing the date, lon and lat.
    recording.date = dt
    recording.lon = -120
    recording.lat = 35


@_skip_lite
def test_watcher_date_preparser_parser():
    # Test the ability for the parser to preparse for lon/lat/date.
    analyzer = LiteAnalyzer()
    directory = "."
    watcher = DirectoryWatcher(directory, analyzers=[analyzer])

    input_path = os.path.join(
        os.path.dirname(__file__), "test_files/2022-08-15-21-05-51.wav"
    )

    watcher.recording_preanalyze = preparser

    # Add a mocked call for on_analyze_complete
    watcher.on_analyze_complete = Mock()

    # Create a "file-created" event in the watcher.
    # Test calling private method directly (this would be called by watchdog)
    event = namedtuple("Event", "src_path")
    event.src_path = input_path
    watcher._on_closed(event)

    # Check complete call count and results.
    assert watcher.on_analyze_complete.call_count == 1
    recording = watcher.on_analyze_complete.call_args.args[0]
    # Assert that the date and week_48 values were correctly parsed from filename.
    assert len(recording.detections) == 2
    assert recording.date == datetime(
        year=2022, month=8, day=15, hour=21, minute=5, second=51
    )
    assert recording.week_48 == 30
    assert recording.lat == 35
    assert recording.lon == -120


def test_watcher_error():
    analyzer = Analyzer()
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
    assert type(watcher.analyzers[0]).__name__ == "Analyzer"


class StopWatching(Exception):
    """Sentinel used to break out of watch()'s otherwise endless loop."""


def run_watch_with_mocked_watchdog(watcher):
    # watch() never returns on its own, so stop it at the observer's start()
    # call, after every watchdog object has been constructed and wired up.
    with patch("birdnetlib.watcher.PatternMatchingEventHandler") as handler_class:
        with patch("birdnetlib.watcher.Observer") as observer_class:
            observer_class.return_value.start.side_effect = StopWatching
            with pytest.raises(StopWatching):
                watcher.watch()
    return handler_class, observer_class


def test_watch_builds_event_handler_with_keyword_arguments():

    # watchdog 5.0.0 made PatternMatchingEventHandler's arguments keyword-only,
    # so passing them positionally is what pins birdnetlib to watchdog < 5.

    watcher = DirectoryWatcher(".", analyzers=[Mock()])

    handler_class, _ = run_watch_with_mocked_watchdog(watcher)

    assert handler_class.call_count == 1
    args, kwargs = handler_class.call_args
    assert args == ()
    assert kwargs == {
        "patterns": ["*.mp3", "*.wav"],
        "ignore_patterns": None,
        "ignore_directories": False,
        "case_sensitive": True,
    }


def test_watch_schedules_event_handler_with_recursive_by_keyword():

    # The other half of watch()'s watchdog call surface.

    directory = os.path.join(os.path.dirname(__file__), "test_files")
    watcher = DirectoryWatcher(directory, analyzers=[Mock()])

    handler_class, observer_class = run_watch_with_mocked_watchdog(watcher)

    observer = observer_class.return_value
    assert observer.schedule.call_count == 1
    args, kwargs = observer.schedule.call_args
    assert args == (handler_class.return_value, directory)
    assert kwargs == {"recursive": True}
