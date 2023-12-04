from birdnetlib.batch import DirectoryAnalyzer
from birdnetlib.analyzer_lite import LiteAnalyzer
import tempfile
import shutil
import os

# from pprint import pprint


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

    with tempfile.TemporaryDirectory() as input_dir:
        # Copy test files to temp directory.
        copytree(test_files, input_dir)
        batch = DirectoryAnalyzer(
            input_dir,
            analyzers=[analyzer],
        )
        batch.process()
        assert len(batch.directory_recordings) == 5
        # Ensure path is a string rather than PosixPath
        assert type(batch.directory_recordings[0].path).__name__ == "str"


def test_batch_extensions():
    analyzer = LiteAnalyzer()
    test_files = "tests/test_files"

    with tempfile.TemporaryDirectory() as input_dir:
        # Copy test files to temp directory.
        copytree(test_files, input_dir)
        batch = DirectoryAnalyzer(input_dir, analyzers=[analyzer], patterns=["*.wav"])
        batch.process()
        assert len(batch.directory_recordings) == 2
