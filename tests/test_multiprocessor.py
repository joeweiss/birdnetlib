from birdnetlib.batch import DirectoryMultiProcessingAnalyzer
from birdnetlib.analyzer_lite import LiteAnalyzer
from birdnetlib.analyzer import Analyzer, MODEL_PATH, LABEL_PATH
from birdnetlib import MultiProcessRecording
import tempfile
import shutil
import os
from datetime import datetime, date
import time
import pytest
from pprint import pprint


def copytree(src, dst, symlinks=False, ignore=None):
    # Works on 3.7+
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def test_batch():
    analyzer = LiteAnalyzer()
    test_files = "tests/test_files"

    start = time.time()

    with tempfile.TemporaryDirectory() as input_dir:
        # Copy test files to temp directory.
        copytree(test_files, input_dir)
        assert len(os.listdir(input_dir)) == 7
        batch = DirectoryMultiProcessingAnalyzer(
            input_dir,
            analyzers=[analyzer],
        )
        batch.process()
        assert len(batch.directory_recordings) == 5
        # Ensure path is a string rather than PosixPath
        assert type(batch.directory_recordings[0].path).__name__ == "str"

    print("test_batch completed in", time.time() - start)


def test_multiprocess_recording_obj():
    results = {
        "config": {
            "date": date(year=2023, month=1, day=1),
            "lat": 55.11,
            "lon": 54.11,
            "minimum_confidence": 0.1,
            "model_name": "BirdNET-Lite",
            "sensitivity": 1.0,
            "week_48": -1,
        },
        "detections": [
            {
                "common_name": "House Wren",
                "confidence": 0.19981279969215393,
                "end_time": 15.0,
                "label": "Troglodytes aedon_House Wren",
                "scientific_name": "Troglodytes aedon",
                "start_time": 12.0,
            },
            {
                "common_name": "Huet's Fulvetta",
                "confidence": 0.1636040210723877,
                "end_time": 27.0,
                "label": "Alcippe hueti_Huet's Fulvetta",
                "scientific_name": "Alcippe hueti",
                "start_time": 24.0,
            },
            {
                "common_name": "Spotted Towhee",
                "confidence": 0.17119209468364716,
                "end_time": 51.0,
                "label": "Pipilo maculatus_Spotted Towhee",
                "scientific_name": "Pipilo maculatus",
                "start_time": 48.0,
            },
            {
                "common_name": "Gray-bellied Spinetail",
                "confidence": 0.1158079132437706,
                "end_time": 99.0,
                "label": "Synallaxis cinerascens_Gray-bellied Spinetail",
                "scientific_name": "Synallaxis cinerascens",
                "start_time": 96.0,
            },
        ],
        "error": False,
        "error_message": None,
        "path": "tests/test_files/soundscape.wav",
        "duration": 120.0,
    }

    recording = MultiProcessRecording(results=results)
    assert len(recording.detections) == 4
    assert recording.date == date(year=2023, month=1, day=1)
    assert recording.lat == results["config"]["lat"]
    assert recording.lon == results["config"]["lon"]
    assert recording.minimum_confidence == results["config"]["minimum_confidence"]
    assert recording.error == results["error"]
    assert recording.error_message == results["error_message"]
    assert recording.path == results["path"]
    assert recording.duration == 120.0

    with tempfile.TemporaryDirectory() as export_dir:
        recording.extract_detections_as_audio(
            directory=export_dir,
            format="mp3",
            bitrate="128k",
            padding_secs=2,
        )

        recording.extract_detections_as_spectrogram(
            directory=export_dir,
            format="png",
            padding_secs=2,
        )

        # Check file list.
        files = os.listdir(export_dir)

        files.sort()

        assert files == [
            "soundscape_10s-17s.mp3",
            "soundscape_10s-17s.png",
            "soundscape_22s-29s.mp3",
            "soundscape_22s-29s.png",
            "soundscape_46s-53s.mp3",
            "soundscape_46s-53s.png",
            "soundscape_94s-101s.mp3",
            "soundscape_94s-101s.png",
        ]

    # Check that not implemented methods are raised on multi-processed recordings.

    with pytest.raises(NotImplementedError) as exc_info:
        recording.analyze()

    assert (
        str(exc_info.value)
        == "MultiProcessRecording objects can not be re-analyzed from this interface."
    )

    with pytest.raises(NotImplementedError) as exc_info:
        recording.process_audio_data(44100)

    assert (
        str(exc_info.value)
        == "MultiProcessRecording objects can not be re-processed from this interface."
    )


def test_batch_with_kwargs():
    test_files = "tests/test_files"

    start = time.time()

    defined_date = datetime(year=2022, month=5, day=10)

    with tempfile.TemporaryDirectory() as input_dir:
        # Copy test files to temp directory.
        copytree(test_files, input_dir)
        assert len(os.listdir(input_dir)) == 7
        batch = DirectoryMultiProcessingAnalyzer(
            input_dir, date=defined_date, min_conf=0.4
        )
        batch.process()
        assert len(batch.directory_recordings) == 5
        # Ensure date was used
        assert batch.directory_recordings[0].config["date"] == defined_date
        assert batch.directory_recordings[0].config["minimum_confidence"] == 0.4
        # Ensure the default is BirdNET-Analyzer
        assert batch.directory_recordings[0].config["model_name"] == "BirdNET-Analyzer"
        test_result_with_detections = [
            i
            for i in batch.directory_recordings
            if i.path.endswith("XC563936 - Soundscape.mp3")
        ][0]

        assert len(test_result_with_detections.detections) == 11

    print("test_batch completed in", time.time() - start)


def test_process_defined_batch():
    analyzer = LiteAnalyzer()
    test_files = "tests/test_files"
    processes = 1

    start = time.time()

    with tempfile.TemporaryDirectory() as input_dir:
        # Copy test files to temp directory.
        copytree(test_files, input_dir)
        assert len(os.listdir(input_dir)) == 7
        batch = DirectoryMultiProcessingAnalyzer(
            input_dir, analyzers=[analyzer], processes=processes
        )
        batch.process()
        assert len(batch.directory_recordings) == 5
        # Ensure path is a string rather than PosixPath
        assert type(batch.directory_recordings[0].path).__name__ == "str"

    print("test_process_defined_batch completed in", time.time() - start)


def test_batch_error():
    analyzer = LiteAnalyzer()
    test_files = "tests/test_files"
    processes = 1

    start = time.time()

    with tempfile.TemporaryDirectory() as input_dir:
        # Copy test files to temp directory.
        copytree(test_files, input_dir)
        # Create an empty for non-audio file error test.
        with open(f"{input_dir}/error-example.wav", "w") as f:
            pass

        assert len(os.listdir(input_dir)) == 8
        batch = DirectoryMultiProcessingAnalyzer(
            input_dir, analyzers=[analyzer], processes=processes
        )
        batch.process()
        assert len(batch.directory_recordings) == 6
        # Ensure path is a string rather than PosixPath
        assert type(batch.directory_recordings[0].path).__name__ == "str"

        assert batch.exceptions_raised == True

    print("test_process_defined_batch completed in", time.time() - start)


def test_batch_extensions():
    analyzer = LiteAnalyzer()
    test_files = "tests/test_files"

    with tempfile.TemporaryDirectory() as input_dir:
        # Copy test files to temp directory.
        copytree(test_files, input_dir)
        assert len(os.listdir(input_dir)) == 7
        batch = DirectoryMultiProcessingAnalyzer(
            input_dir, analyzers=[analyzer], patterns=["*.wav"]
        )
        batch.process()
        assert len(batch.directory_recordings) == 2
