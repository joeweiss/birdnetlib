from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from birdnetlib.analyzer_lite import LiteAnalyzer
import os
import pytest

from birdnetlib.exceptions import AudioFormatError, AnalyzerRuntimeWarning


def test_analyzer_exceptions():

    analyzer = Analyzer()

    # Test that a non-audio file throws an appropriate exception.
    input_path = os.path.join(
        os.path.dirname(__file__), "test_files/file_does_not_exist.wav"
    )
    with pytest.raises(FileNotFoundError):
        recording = Recording(analyzer, input_path)
        recording.analyze()

    # Test that a non-audio file throws and appropriate exception.

    # Import an file that's not an audio file.
    input_path = os.path.join(os.path.dirname(__file__), "test_files/species_list.txt")
    with pytest.raises(AudioFormatError) as excinfo:
        recording = Recording(analyzer, input_path)
        recording.analyze()
    assert str(excinfo.value) == "Audio format could not be opened."


def test_lite_analyzer_exceptions():

    analyzer = LiteAnalyzer()

    # Test that a non-audio file throws an appropriate exception.
    input_path = os.path.join(
        os.path.dirname(__file__), "test_files/file_does_not_exist.wav"
    )
    with pytest.raises(FileNotFoundError):
        recording = Recording(analyzer, input_path)
        recording.analyze()

    # Test that a non-audio file throws and appropriate exception.

    # Import an file that's not an audio file.
    input_path = os.path.join(os.path.dirname(__file__), "test_files/species_list.txt")
    with pytest.raises(AudioFormatError) as excinfo:
        recording = Recording(analyzer, input_path)
        recording.analyze()
    assert str(excinfo.value) == "Audio format could not be opened."


def test_detections_before_analyze_call():
    analyzer = LiteAnalyzer()

    input_path = os.path.join(os.path.dirname(__file__), "test_files/audio.mp3")
    recording = Recording(analyzer, input_path)

    with pytest.warns(AnalyzerRuntimeWarning):
        print(recording.detections)
