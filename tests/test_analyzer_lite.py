from birdnetlib import Recording
from birdnetlib.analyzer_lite import LiteAnalyzer

from pprint import pprint
import pytest
import os
import tempfile
import csv
from unittest import TestCase


def test_basic():

    # Process file with command line utility, then process with python library and ensure equal commandline_results.

    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    input_path = os.path.join(
        os.path.dirname(__file__), "test_files/XC558716 - Soundscape.mp3"
    )

    tf = tempfile.NamedTemporaryFile()
    output_path = tf.name

    # Process using python script as is.
    birdnet_lite_path = os.path.join(os.path.dirname(__file__), "BirdNET-Lite")

    cmd = f"python analyze.py --i '{input_path}' --o={output_path} --lat {lat} --lon {lon} --week {week_48} --min_conf {min_conf}"
    os.system(f"cd {birdnet_lite_path}; {cmd}")

    with open(tf.name) as f:
        for line in f:
            print(line)

    with open(tf.name, newline="") as csvfile:
        # reader = csv.reader(csvfile, delimiter=";", quotechar="|")
        reader = csv.DictReader(csvfile, delimiter=";")
        commandline_results = []
        for row in reader:
            commandline_results.append(
                {
                    "start_time": float(row["Start (s)"]),
                    "end_time": float(row["End (s)"]),
                    "common_name": row["Common name"],
                    "scientific_name": row["Scientific name"],
                    "confidence": float(row["Confidence"]),
                }
            )

    # pprint(commandline_results)

    analyzer = LiteAnalyzer()
    recording = Recording(
        analyzer,
        input_path,
        lat=lat,
        lon=lon,
        week_48=week_48,
        min_conf=min_conf,
    )
    recording.analyze()

    # pprint(recording.detections)

    assert len(recording.detections) == 6
    assert len(commandline_results) == 6

    assert recording.detections[0]["common_name"] == "House Wren"
    assert pytest.approx(recording.detections[0]["confidence"], 0.01) == 0.27517712

    assert commandline_results[0]["common_name"] == "House Wren"
    assert pytest.approx(commandline_results[0]["confidence"], 0.01) == 0.27517712


def test_with_custom_list():

    lon = -120.7463
    lat = 35.4244
    week_48 = 18
    min_conf = 0.25
    input_path = os.path.join(
        os.path.dirname(__file__), "test_files/XC558716 - Soundscape.mp3"
    )
    custom_list_path = os.path.join(
        os.path.dirname(__file__), "test_files/custom_species_list.txt"
    )

    tf = tempfile.NamedTemporaryFile()
    output_path = tf.name

    # Process using python script as is.
    birdnet_lite_path = os.path.join(os.path.dirname(__file__), "BirdNET-Lite")

    cmd = f"python analyze.py --i '{input_path}' --o={output_path} --lat {lat} --lon {lon} --week {week_48} --min_conf {min_conf} --custom_list {custom_list_path}"
    os.system(f"cd {birdnet_lite_path}; {cmd}")

    with open(tf.name) as f:
        for line in f:
            print(line)

    with open(tf.name, newline="") as csvfile:
        # reader = csv.reader(csvfile, delimiter=";", quotechar="|")
        reader = csv.DictReader(csvfile, delimiter=";")
        commandline_results = []
        for row in reader:
            commandline_results.append(
                {
                    "start_time": float(row["Start (s)"]),
                    "end_time": float(row["End (s)"]),
                    "common_name": row["Common name"],
                    "scientific_name": row["Scientific name"],
                    "confidence": float(row["Confidence"]),
                }
            )

    pprint(commandline_results)

    analyzer = LiteAnalyzer(custom_species_list_path=custom_list_path)
    recording = Recording(
        analyzer,
        input_path,
        lat=lat,
        lon=lon,
        week_48=week_48,
        min_conf=min_conf,
    )
    recording.analyze()

    pprint(recording.detections)

    assert len(recording.detections) == 1
    assert len(commandline_results) == 1

    assert recording.detections[0]["common_name"] == "Spotted Towhee"
    assert pytest.approx(recording.detections[0]["confidence"], 0.01) == 0.55690277

    assert commandline_results[0]["common_name"] == "Spotted Towhee"
    assert pytest.approx(commandline_results[0]["confidence"], 0.01) == 0.55690277
