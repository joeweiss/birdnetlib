from birdnetlib.batch import DirectoryMultiProcessingAnalyzer
from birdnetlib.analyzer_lite import LiteAnalyzer
import tempfile
import shutil
import os
from datetime import datetime
import time


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

        assert len(test_result_with_detections.detections) == 13

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
