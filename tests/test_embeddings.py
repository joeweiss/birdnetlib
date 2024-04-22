from birdnetlib import Recording, LargeRecording
from birdnetlib.analyzer import Analyzer, LargeRecordingAnalyzer

from pprint import pprint
import pytest
import os
import tempfile
import csv
from unittest.mock import patch
import numpy as np


def test_embeddings():
    # Process file with command line utility, then process with python library and ensure equal commandline_results.

    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    tf = tempfile.NamedTemporaryFile(suffix=".csv")
    output_path = tf.name

    # Process using python script as is.
    birdnet_analyzer_path = os.path.join(os.path.dirname(__file__), "BirdNET-Analyzer")

    cmd = f"python embeddings.py --i '{input_path}' --o={output_path}"
    os.system(f"cd {birdnet_analyzer_path}; {cmd}")

    with open(tf.name, newline="") as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        commandline_results = []
        for row in tsvreader:
            commandline_results.append(
                {
                    "start_time": float(row[0]),
                    "end_time": float(row[1]),
                    "embeddings": [float(i) for i in row[2].split(",")],
                }
            )

    # pprint(commandline_results)
    assert len(commandline_results) == 40

    analyzer = Analyzer()
    recording = Recording(
        analyzer,
        input_path,
        lat=lat,
        lon=lon,
        week_48=week_48,
        min_conf=min_conf,
        return_all_detections=True,
    )
    recording.extract_embeddings()

    # Check that birdnetlib results match command line results.
    assert len(recording.embeddings) == 40

    for idx, i in enumerate(commandline_results):
        # Specify the tolerance level
        tolerance = 1e-4  # 4 decimal points tolerance between BirdNET and birdnetlib.

        # Assert that the arrays are almost equal within the tolerance
        assert np.allclose(
            i["embeddings"], recording.embeddings[idx]["embeddings"], atol=tolerance
        )


def test_largefile_embeddings():
    # Process file with command line utility, then process with python library and ensure equal commandline_results.

    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    tf = tempfile.NamedTemporaryFile(suffix=".csv")
    output_path = tf.name

    # Process using python script as is.
    birdnet_analyzer_path = os.path.join(os.path.dirname(__file__), "BirdNET-Analyzer")

    cmd = f"python embeddings.py --i '{input_path}' --o={output_path}"
    os.system(f"cd {birdnet_analyzer_path}; {cmd}")

    with open(tf.name, newline="") as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        commandline_results = []
        for row in tsvreader:
            commandline_results.append(
                {
                    "start_time": float(row[0]),
                    "end_time": float(row[1]),
                    "embeddings": [float(i) for i in row[2].split(",")],
                }
            )

    # pprint(commandline_results)
    assert len(commandline_results) == 40

    # TODO: Implement for LargeRecording.
    # Confirm that LargeRecording return not implemented.
    large_analyzer = LargeRecordingAnalyzer()
    recording = LargeRecording(
        large_analyzer,
        input_path,
        lat=lat,
        lon=lon,
        week_48=week_48,
        min_conf=min_conf,
        return_all_detections=True,
    )
    msg = "Extraction of embeddings is not yet implemented for LargeRecordingAnalyzer. Use Analyzer if possible."
    with pytest.raises(NotImplementedError, match=msg):
        recording.extract_embeddings()
