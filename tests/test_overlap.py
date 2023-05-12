from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer, MODEL_PATH, LABEL_PATH

from pprint import pprint
import pytest
import os
import tempfile
import csv
from collections import Counter


# Overlapping detections are when the library returns more than one detection for the same (3 sec) piece of audio.
# We want to ensure that birdnetlib isn't filtering out these overlapping detections, or prematurely
# filtering or ranking them.


def test_without_species_list():

    # Process file with command line utility, then process with python library and ensure equal commandline_results.

    min_conf = 0.0  # Irresponsibly low, just for testing.
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")

    tf = tempfile.NamedTemporaryFile(suffix=".csv")
    output_path = tf.name

    # Process using python script as is.
    birdnet_analyzer_path = os.path.join(os.path.dirname(__file__), "BirdNET-Analyzer")

    cmd = f"python analyze.py --i '{input_path}' --o={output_path} --min_conf {min_conf} --rtype=csv"

    print(cmd)
    os.system(f"cd {birdnet_analyzer_path}; {cmd}")

    with open(tf.name) as f:
        for line in f:
            print(line)

    with open(tf.name, newline="") as csvfile:
        # reader = csv.reader(csvfile, delimiter=";", quotechar="|")
        reader = csv.DictReader(csvfile)
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
    assert len(commandline_results) > 0

    analyzer = Analyzer()
    recording = Recording(
        analyzer,
        input_path,
        min_conf=min_conf,
    )
    recording.analyze()

    # Check that birdnetlib results match command line results.
    assert len(recording.detections) == len(commandline_results)

    # Check that detection confidence is float.
    assert type(recording.detections[0]["confidence"]) is float

    # groups
    start_times = [i["start_time"] for i in recording.detections]
    item_counts = Counter(start_times)
    assert item_counts[48.0] == 15

    # Ensure that multiple detections exist for 57-60 seconds.
    overlapping = [i for i in recording.detections if i["start_time"] == 57.0]
    assert len(overlapping) == 15


def test_with_species_list():

    # Process file with command line utility, then process with python library and ensure equal commandline_results.

    min_conf = 0.1
    input_path = os.path.join(os.path.dirname(__file__), "test_files/soundscape.wav")
    custom_list_path = os.path.join(
        os.path.dirname(__file__), "test_files/species_list.txt"
    )

    tf = tempfile.NamedTemporaryFile(suffix=".csv")
    output_path = tf.name

    # Process using python script as is.
    birdnet_analyzer_path = os.path.join(os.path.dirname(__file__), "BirdNET-Analyzer")

    cmd = f"python analyze.py --i '{input_path}' --o={output_path} --min_conf {min_conf} --slist {custom_list_path} --rtype=csv"
    os.system(f"cd {birdnet_analyzer_path}; {cmd}")

    with open(tf.name) as f:
        for line in f:
            print(line)

    with open(tf.name, newline="") as csvfile:
        # reader = csv.reader(csvfile, delimiter=";", quotechar="|")
        reader = csv.DictReader(csvfile)
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
    assert len(commandline_results) > 0

    analyzer = Analyzer(custom_species_list_path=custom_list_path)
    recording = Recording(
        analyzer,
        input_path,
        min_conf=min_conf,
    )
    recording.analyze()

    assert recording.duration == 120
    assert (
        commandline_results[0]["common_name"] == recording.detections[0]["common_name"]
    )

    commandline_birds = [i["common_name"] for i in commandline_results]
    detected_birds = [i["common_name"] for i in recording.detections]
    assert commandline_birds == detected_birds

    assert len(recording.detections) == len(commandline_results)
    assert (
        len(analyzer.custom_species_list) == 41
    )  # Check that this matches the number printed by the cli version.

    # Ensure that multiple detections exist for 57-60 seconds.
    overlapping = [i for i in recording.detections if i["start_time"] == 57.0]
    assert len(overlapping) == 2

    # Run a recording with lat/lon and throw an error when used with custom species list.

    lon = -120.7463
    lat = 35.4244
    week_48 = 18

    with pytest.raises(ValueError):
        recording = Recording(
            analyzer,
            input_path,
            lon=lon,
            lat=lat,
            week_48=week_48,
            min_conf=min_conf,
        )
        recording.analyze()
